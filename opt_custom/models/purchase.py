# -*- coding: utf-8 -*-


from collections import defaultdict
from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError


class Purchase(models.Model):
    _inherit = "purchase.order"

    vendor_invoice = fields.Char(string="Vendor Invoice")
    invoice_date = fields.Date(string="Invoice Date")
    phone = fields.Char(related="partner_id.phone", string="Phone")
    vendor_bank_id = fields.Many2one('res.partner.bank', string="Acct #")
    transmission_method = fields.Selection(
        [("email", "Email"),
        ("phone", "Phone"),
        ("fax", "Fax"),
        ("online", "Online"),
        ("representative", "Representative"),],
        string="Transmission Method")
    placed_with = fields.Char(string="Placed with")
    shipping_method_id = fields.Many2one("delivery.carrier", string="Shipping")
    state = fields.Selection([
        ('draft', 'Request'),
        ('purchase', 'Purchase Order'),
        ('sent', 'PO Sent'),
        ('to approve', 'To Approve'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    patient_ids = fields.Many2many('res.partner', 'partner_purchase_rel', 'partner_id', 'purchase_id', string='Patient Reference')

    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        res = super(Purchase, self).onchange_partner_id_warning()
        self.vendor_bank_id = False
        if self.partner_id and self.partner_id.bank_ids:
            self.vendor_bank_id =  self.partner_id.bank_ids.ids[0]
        return res

    @api.model
    def create(self, vals):
        res = super(Purchase,self).create(vals)
        if res.transmission_method:
            res.print_quotation()
            res.user_id = self.env.user.id
        return res

    def write(self, vals):
        res = super(Purchase,self).write(vals)
        if vals.get('transmission_method'):
            self.print_quotation()
            self.user_id = self.env.user.id
        return res


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        procurements_by_po_domain = defaultdict(list)
        for procurement, rule in procurements:

            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
            schedule_date = procurement_date_planned 
            # schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))

            supplier = procurement.product_id.with_context(force_company=procurement.company_id.id)._select_seller(
                partner_id=procurement.values.get("supplier_id"),
                quantity=procurement.product_qty,
                date=schedule_date.date(),
                uom_id=procurement.product_uom)

            # Fall back on a supplier for which no price may be defined. Not ideal, but better than
            # blocking the user.
            supplier = supplier or procurement.product_id._prepare_sellers(False).filtered(
                lambda s: not s.company_id or s.company_id == procurement.company_id
            )[:1]

            if not supplier:
                msg = _('There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (procurement.product_id.display_name)
                raise UserError(msg)

            partner = supplier.name
            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            procurement.values['propagate_date'] = rule.propagate_date
            procurement.values['propagate_date_minimum_delta'] = rule.propagate_date_minimum_delta
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            procurements_by_po_domain[domain].append((procurement, rule))

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id
            if not po:
                # We need a rule to generate the PO. However the rule generated
                # the same domain for PO and the _prepare_purchase_order method
                # should only uses the common rules's fields.
                vals = rules[0]._prepare_purchase_order(company_id, origins, [p.values for p in procurements])
                # The company_id is the same for all procurements since
                # _make_po_get_domain add the company in the domain.
                # We use SUPERUSER_ID since we don't want the current user to be follower of the PO.
                # Indeed, the current user may be a user without access to Purchase, or even be a portal user.
                # pos_sales = self.env['pos.order'].search([('name', '=',vals.get('origin'))])
                # if pos_sales:
                #     vals.update({'patient_ids': [(6, 0, [pos_sales.partner_id.id])]})
                po = self.env['purchase.order'].with_context(force_company=company_id.id).with_user(SUPERUSER_ID).create(vals)
            else:
                # If a purchase order is found, adapt its `origin` field.
                if po.origin:
                    missing_origins = origins - set(po.origin.split(', '))
                    all_origins = list(origins) + po.origin.split(', ')
                    
                    if missing_origins:
                        sales = self.env['sale.order'].search([('name', 'in', tuple(all_origins))])
                        # pos_sales = self.env['pos.order'].search([('name', 'in', tuple(all_origins))])
                        # if not pos_sales:
                        #     po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
                        if sales:
                            po.write({'patient_ids': [(6, 0, sales.mapped('partner_id').ids)]})
                        # if pos_sales:
                        #     po.write({'origin': po.origin + ', ' + ', '.join(missing_origins),
                        #             'patient_ids': [(6, 0, pos_sales.mapped('partner_id').ids)]})
                else:
                    sales = self.env['sale.order'].search([('name', 'in', tuple(origins))])
                    # pos_sales = self.env['pos.order'].search([('name', 'in', tuple(origins))])
                    # if not pos_sales:
                    #     po.write({'origin': ', '.join(origins)})
                    if sales:
                        po.write({'patient_ids': [(6, 0, sales.mapped('partner_id').ids)]})
                    # if pos_sales:
                    #     po.write({'origin': ', '.join(origins),
                    #             'patient_ids': [(6, 0, pos_sales.mapped('partner_id').ids)]})
                    

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(lambda l: l.product_id.id), key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                        procurement.product_qty, procurement.product_uom, company_id,
                        procurement.values, po_line)
                    po_line.write(vals)
                else:
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].name
                    po_line_values.append(self._prepare_purchase_order_line(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
            self.env['purchase.order.line'].sudo().create(po_line_values)

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        sales = self.env['sale.order'].search([('name', 'in', tuple(origins))])
        res['patient_ids'] = [(6, 0, sales.mapped('partner_id').ids)]

        dates = [fields.Datetime.from_string(value['date_planned']) for value in values]
        procurement_date_planned = min(dates)
        res['date_order'] = procurement_date_planned
        return res

    