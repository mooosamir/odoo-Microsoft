import json
import logging
from odoo import models, fields, tools, api, exceptions

_logger = logging.getLogger(__name__)


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    # date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now,
    #                              states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #                              help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    physician_id = fields.Many2one('hr.employee', string="Provider",
                                   domain="['|', ('doctor','=',True), ('is_outside_doctor','=',True)]")
    insurance_id = fields.Many2one('spec.insurance', domain="[('partner_id','=', partner_id),('terminated','=',False)]")
    secondary_insurance_id = fields.Many2one('spec.insurance', domain="[('partner_id','=', partner_id),('terminated','=',False)]")
    authorization_id = fields.Many2one('spec.insurance.authorizations', domain="[('insurance_id','=', insurance_id)]")
    date_fo_birth = fields.Date(string="Date of Birth", related='partner_id.date_of_birth')
    cell = fields.Char(string="Cell", related='partner_id.phone')
    email = fields.Char(string="Email", related='partner_id.email')
    diagnosis_lines = fields.One2many('sale.diagnosis.setup', 'sale_id')
    insurance_count = fields.Integer(readonly=True, compute='compute_insurance_count')
    # payment_method_id = fields.Many2one('pos.payment.method', string="Payment Methods")
    # [('patient','=', True)]
    partner_id = fields.Many2one(
        'res.partner', string='Patient', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', '&', ('company_id', '=', False), ('company_id', '=', company_id), ('patient','=', True)]")

    @api.depends('insurance_id')
    def compute_insurance_count(self):
        self.insurance_count = 0
        invoices = self.env['account.move'].search(
            [('insured_id', '=', self.insurance_id.id), ('invoice_origin', '=', self.name)])
        self.insurance_count = len(invoices)

    def action_view_insurance(self):
        invoices = self.env['account.move'].search([('insured_id', '=', self.insurance_id.id), ('invoice_origin', '=', self.name)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id,
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def _compute_payments_widget_reconciled_info_invoice(self):
        for rec in self:
            inv = rec.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', rec.name)],
                                                 limit=1)
            if inv:
                rec.invoice_outstanding_credits_debits_widget = inv.invoice_outstanding_credits_debits_widget
                rec.invoice_payments_widget = inv.invoice_payments_widget
                rec.invoice_payment_state = inv.invoice_payment_state
                rec.invoice_amount_residual = inv.amount_residual
            else:
                rec.invoice_outstanding_credits_debits_widget = json.dumps(False)
                rec.invoice_payments_widget = json.dumps(False)
                rec.invoice_payment_state = None
                rec.invoice_amount_residual = None

    invoice_payment_state = fields.Selection(selection=[
        ('draft', 'draft'),
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid')],
        string='Payment', copy=False, tracking=True, default='draft'
    )

    # amount widget due for invoice
    invoice_outstanding_credits_debits_widget = fields.Text(groups="account.group_account_invoice",
                                                            compute='_compute_payments_widget_reconciled_info_invoice')
    invoice_payments_widget = fields.Text(groups="account.group_account_invoice",
                                          compute='_compute_payments_widget_reconciled_info_invoice')
    invoice_amount_residual = fields.Monetary(string='Amount Due',
                                              compute='_compute_payments_widget_reconciled_info_invoice')

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        if res:
            rfq = self.order_line.filtered(lambda x: x.product_id.product_tmpl_id.categ_id.name in ['Frames', 'Lens']
                                                     and x.product_id.route_ids.filtered(lambda y:y.name == 'Purchase Order')
                                                     and not x.product_id.qty_available
                                                     or x.product_id.qty_available < x.product_uom_qty)

            if rfq:
                for products in rfq:
                    if products.product_id.seller_ids.id:
                        po = self.env['purchase.order'].create({
                            'partner_id': products.product_id.seller_ids[0].name.id,
                            'origin': self.name,
                            # 'name': self.name,
                        })
                        self.env['purchase.order.line'].create({
                            'order_id': po.id,
                            'name': products.product_id.name,
                            'product_id': products.product_id.id,
                            'product_qty': products.product_uom_qty - products.product_id.qty_available,
                            'product_uom': products.product_uom.id,
                            'price_unit': products.product_id.seller_ids[0].price,
                            'date_planned': fields.datetime.today().strftime(tools.misc.DEFAULT_SERVER_DATETIME_FORMAT),
                        })

            if not self.env.context.get('no_invoice_create', False):
                if 'post_sale_type' in self and self.post_sale_type in ["Warranty", "Remake"]:
                    pass
                else:
                    order = self.env['sale.order']
                    order = order.create(self.copy_data())
                    insurances = {x.lab_details_id.id: self.order_line.filtered(
                        lambda y: y.lab_details_id.id == x.lab_details_id.id and y.display_type != "line_section").insurance_id.ids for x in
                                  self.order_line}
                    # insurances = {x.insurance_id: order.order_line.filtered(
                    #     lambda y: y.insurance_id.id == x.insurance_id.id and y.display_type != "line_section") for x in
                    #  order.order_line}
                    insurances = {k: v for k, v in insurances.items() if len(v)}
                    if len(insurances) >= 1:
                        for insurance in insurances:
                            if len(insurances[insurance]) == 1:
                                for line in self.order_line:
                                    if line.lab_details_id.id == insurance:
                                        line.actual_retail = line.price_unit
                                        line.price_unit = (line.insur / line.product_uom_qty) if line.insur else 0
                                        line.co_pay = 0
                                        line.pt_resp = 0
                                    else:
                                        line.qty_to_invoice = 0

                                invoice = self._create_invoices()
                                invoice.invoice_line_ids = False

                                spec_insurance = self.insurance_id
                                invoice.partner_id = spec_insurance.carrier_id.id
                                for line in invoice.line_ids:
                                    line.partner_id = spec_insurance.carrier_id.id
                                lab_details_id = self.env['multi.order.type'].browse(insurance)
                                invoice.sale_order_id = self.id
                                # invoice.provider_id = self.physician_id.id
                                invoice.insured_id = spec_insurance.id
                                invoice.insured = spec_insurance.relationship
                                invoice.primary_insurance_company_id = spec_insurance.carrier_id.id
                                invoice.patient_id = order.partner_id.id
                                invoice.authorization_id = self.authorization_id.id
                                invoice.service_date = self.date_order
                                # invoice.post()
                                # # DX Codes
                                for dx_line in self.diagnosis_lines:
                                    if dx_line.seq == 'A':
                                        invoice.a_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'B':
                                        invoice.b_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'C':
                                        invoice.c_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'D':
                                        invoice.d_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'E':
                                        invoice.e_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'F':
                                        invoice.f_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'G':
                                        invoice.g_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'H':
                                        invoice.h_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'I':
                                        invoice.i_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'J':
                                        invoice.j_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'K':
                                        invoice.k_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                    elif dx_line.seq == 'L':
                                        invoice.l_diagnosis_code_id = dx_line.diagnosis_code_id.id
                                #
                                name = ''
                                for hcpcs_id in lab_details_id.hcpcs_id:
                                    if hcpcs_id.display_type == 'line_section':
                                        name = hcpcs_id.name
                                    elif name != "":
                                        if len(hcpcs_id.hcpcs_code.ids) == 0:
                                            vals = {
                                                'move_id': invoice.id,
                                                'name': name,
                                                # 'procedure_code_id': [(5, 0, 0)],
                                                'spec_modifier_ids': hcpcs_id.hcpcs_modifier.ids,
                                                'actual_retail': hcpcs_id.retail_price,
                                                'pt_total': hcpcs_id.pt_total,
                                                'quantity': hcpcs_id.qty,
                                                'ins_receivable': hcpcs_id.insurance,
                                                'diagnosis_code_sale_ids': hcpcs_id.order_line_id.DX.ids,
                                                'account_id': hcpcs_id.categ_id.property_account_income_categ_id.id
                                            }
                                            invoice.invoice_line_ids.create(vals)
                                        else:
                                            for hcpcs_code in hcpcs_id.hcpcs_code:
                                                vals = {
                                                    'move_id': invoice.id,
                                                    'name': name,
                                                    'procedure_code_id': hcpcs_code.id,
                                                    'spec_modifier_ids': hcpcs_id.hcpcs_modifier.ids,
                                                    'actual_retail': hcpcs_id.retail_price,
                                                    'pt_total': hcpcs_id.pt_total,
                                                    'quantity': hcpcs_id.qty,
                                                    'ins_receivable': hcpcs_id.insurance,
                                                    'diagnosis_code_sale_ids': hcpcs_id.order_line_id.DX.ids,
                                                    'account_id': hcpcs_id.categ_id.property_account_income_categ_id.id
                                                }
                                                invoice.invoice_line_ids.create(vals)
                                print("INO", invoice.invoice_line_ids)
                                invoice.post()
                                self._reset_order_lines(order)

                    for line in self.order_line:
                        line.actual_retail = line.price_unit
                        line.price_unit = (line.pt_total / line.product_uom_qty) if line.pt_total else 0
                        if line.co_pay > 0:
                            price = (line.price_unit * line.product_uom_qty) - line.co_pay
                            line.pt_resp = price
                        # else:
                        # line.pt_resp = (line.price_unit * line.product_uom_qty)
                        line.insur = 0
                        # if line.name == 'Exchange':
                        #     line.price_unit = 0

                    if 'post_sale_type' in self and self.post_sale_type == "Exchange" and sum(self.order_line.mapped('price_unit')) < 0:
                        raise exceptions.MissingError("Patient Invoice can't be generated, as it is " +
                                                      str("{:.2f}".format(sum(self.order_line.mapped('price_unit')))))
                    invoice = self._create_invoices()
                    invoice.post()
                    self._reset_order_lines(order)
                    order.unlink()

            # wiz_act = self.picking_ids.button_validate()
            # wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
            # wiz.process()
            return True

    def _reset_order_lines(self, order):
        self.partner_id = order.partner_id
        for i in range(0, len(self.order_line), 1):
            self.order_line[i].price_unit = order.order_line[i].price_unit
            self.order_line[i].co_pay = order.order_line[i].co_pay
            self.order_line[i].pt_resp = order.order_line[i].pt_resp
            self.order_line[i].qty_to_invoice = order.order_line[i].product_uom_qty

    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrderInherit, self)._create_invoices()
        for i in self.diagnosis_lines:
            i.move_id = res.id
        return res

    @api.onchange('diagnosis_lines')
    def get_dx_on_lines(self):
        for rec in self:
            create_dx_ls = []
            for diagnosis in rec.diagnosis_lines:
                diag_dic = {'diagnosis_code_id': diagnosis.diagnosis_code_id.id, 'seq': diagnosis.seq ,'sale_id': rec._origin.id}
                create_dx = self.env['sale.line.diagnosis.setup'].search([('diagnosis_code_id', '=', diagnosis.diagnosis_code_id.id), ('seq', '=', diagnosis.seq)])
                if not create_dx:
                    create_dx = self.env['sale.line.diagnosis.setup'].create(diag_dic)
                create_dx_ls.append((4, create_dx.id))
            for line in rec.order_line:
                line.DX = [(5, 0, 0)]
            for line in rec.order_line.filtered(lambda x: x.display_type != 'line_section'):
                line.DX = create_dx_ls
            pointer = 0
            for line in rec.diagnosis_lines:
                line.seq = chr(pointer+65)
                pointer += 1

    def action_complete_pair(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'multi.order.type',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'so_id': rec.id, 'order_ref': "Complete Pair", 'insurance_id': rec.insurance_id.id, 'authorization_id': rec.authorization_id.id, 'partner_id': rec.partner_id.id, 'domain_rx': 'glasses',
                            'new_size':'max-width_1180px'},
            }

    def action_contact_lens(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'multi.order.type',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'so_id': rec.id, 'order_ref': "Contact Lens", 'insurance_id': rec.insurance_id.id, 'authorization_id': rec.authorization_id.id, 'partner_id': rec.partner_id.id, 'domain_rx': 'soft,hard',
                            'new_size':'max-width_1180px'},
            }

    def action_frame_only(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'multi.order.type',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'so_id': rec.id, 'order_ref': "Frame Only", 'insurance_id': rec.insurance_id.id, 'authorization_id': rec.authorization_id.id, 'partner_id': rec.partner_id.id, 'new_size':'max-width_1180px'},
            }

    def action_lens_only(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'multi.order.type',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'so_id': rec.id, 'order_ref': "Lenses Only", 'insurance_id': rec.insurance_id.id, 'authorization_id': rec.authorization_id.id, 'partner_id': rec.partner_id.id, 'domain_rx': 'glasses',
                            'new_size':'max-width_1180px'}
            }

    def action_services(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'multi.order.type',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'so_id': rec.id, 'order_ref': "Services", 'insurance_id': rec.insurance_id.id, 'authorization_id': rec.authorization_id.id, 'partner_id': rec.partner_id.id, 'new_size':'max-width_1180px'}
            }

    def action_miscellaneous(self):
        for rec in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'multi.order.type',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {'so_id': rec.id, 'order_ref': "Miscellaneous", 'insurance_id': rec.insurance_id.id, 'authorization_id': rec.authorization_id.id ,'partner_id': rec.partner_id.id, 'new_size':'max-width_1180px'}
            }

    def delete_sale_order_line(self, multi_order_id, sale_order_line_id):
        so = self.env['sale.order.line'].search([('id', '=', int(sale_order_line_id))]).order_id
        for line in so.order_line.filtered(lambda x: x.lab_details_id.id == multi_order_id):
            line.unlink()
        return "1"