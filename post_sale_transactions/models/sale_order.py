import odoo.exceptions
from odoo import models, fields, tools, api, _
from odoo.addons.test_impex.models import compute_fn


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_post_sale_ref(self):
        for data in self:
            post_sale_ref = [(5, 0, 0)]
            for id in self.env['sale.order'].search([('post_sale_order_ref', '=', data.id), ('state', '!=', 'cancel')]).ids:
                post_sale_ref.append((4, id))
            if len(data.order_line.invoice_lines.move_id.filtered(lambda r: r.type == 'out_refund')) > 0:
                post_sale_ref.append((4, data.id))
            data.post_sale_ref = post_sale_ref
            data.processed_in_post_sale = True if len(data.post_sale_ref.ids) > 0 else False

    # def _get_processed_in_post_sale(self):
    #     for res in self:
    #         post_sale_order_ref = self.env['sale.order'].search_count([('post_sale_order_ref', '=', self.id)])
    #         res.processed_in_post_sale = True if post_sale_order_ref > 0 else False

    processed_in_post_sale = fields.Boolean(compute="_get_post_sale_ref")
    post_sale_type = fields.Selection([('Return', 'Return'), ('Remake', 'Remake'),
                             ('Exchange', 'Exchange'), ('Warranty', 'Warranty'),
                             ], required=False, default=None)
    post_sale_order_line_ids = fields.One2many('post.sale.order.line', 'sale_order_id', help="Post Sale Lines")
    post_sale_order_ref = fields.Many2one('sale.order', help="Post Sale ref", readonly=1)
    post_sale_ref = fields.One2many('sale.order',help="Post Sale ref", readonly=1, compute="_get_post_sale_ref")
    sale_order_session_id = fields.Many2one('sale.order.session', relation="sos_id", readonly=True, copy=False)
    post_sale_reasons_id = fields.Many2one('post.sale.reasons', string="Post Sale Reason", readonly=True)

    @api.depends('order_line.invoice_lines')
    def _get_customer_note_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type == 'out_refund')
            order.customer_note_count = len(invoices)

    def _get_post_sale_exchange_delivery(self):
        for order in self:
            order.post_sale_exchange_delivery = 0
            if order.post_sale_order_ref:
                order.post_sale_exchange_delivery = self.env['stock.picking']\
                    .search_count([('post_sale_order_ref', '=', order.post_sale_order_ref.id)])

    def _get_post_sale_amount(self):
        amount = 0
        if self.post_sale_type == 'Exchange':
            for psol_ids in self.post_sale_order_line_ids:
                amount += psol_ids.sol_pt_total
        if self.post_sale_type == 'Remake':
            for ol_ids in self.order_line:
                if ol_ids.product_uom_qty < 0:
                    amount += ol_ids.price_total
            amount = amount * -1
        self.post_sale_amount = amount

    def _get_sale_order_session(self):
        for order in self:
            order.sale_order_session = self.env['sale.order.session'].search([("state", 'in', ['in_progress'])]).id

    post_sale_exchange_delivery = fields.Integer(string='EXCHG Delivery',
                                                 compute='_get_post_sale_exchange_delivery', readonly=True)
    customer_note_count = fields.Integer(string='Customer Note',
                                         compute='_get_customer_note_invoiced', readonly=True)
    post_sale_amount = fields.Float(compute='_get_post_sale_amount', readonly=True)
    sale_order_session = fields.Many2one('sale.order.session', compute='_get_sale_order_session', readonly=True, copy=False)

    @api.model
    def create(self, values):
        open_session = self.env['sale.order.session'].search([("state", 'in', ['in_progress'])])
        res = super(SaleOrder, self).create(values)
        if open_session.id:
            res.sale_order_session_id = open_session.id
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrder, self).default_get(fields_list)
        post_sale_order_line_ids = []
        if len(self.env.context.get('post_sale_transactions_lines_ids', [])) > 0:
            if self.env.context.get('default_post_sale_type', '') == 'Exchange':
                post_sale_transactions_lines_ids = self.env.context.get('post_sale_transactions_lines_ids', [])
                post_sale_transactions_lines_ids = self.env['post.sale.transactions.lines'].search([('id', 'in', post_sale_transactions_lines_ids)])
                for pstl_id in post_sale_transactions_lines_ids:
                    if "Promotion~" in pstl_id.name:
                        name = pstl_id.name.split("~")[0]
                        post_sale_order_line_ids.append(self.env['post.sale.order.line'].create({
                            'sale_order_line_id': pstl_id.account_move_line_id.sale_line_ids.id,
                            'name': name,
                            'qty': pstl_id.qty,
                            'display_type': pstl_id.display_type,
                            'return_location': pstl_id.return_location.id,
                            'sol_name': pstl_id.name,
                            'sol_product_id': pstl_id.product_id.id,
                            'sol_product_uom_qty': pstl_id.account_move_line_id.sale_line_ids.product_uom_qty,
                            'sol_pt_total': float(pstl_id.name.split("~")[1]),
                            'tax_id': pstl_id.account_move_line_id.sale_line_ids.tax_id,
                            # 'pt_total': float(pstl_id.name.split("~")[1]) * -1,
                        }).id)
                    else:
                        name = "EXCHG " + pstl_id.name if pstl_id.display_type == 'line_section' else pstl_id.name
                        post_sale_order_line_ids.append(self.env['post.sale.order.line'].create({
                            'sale_order_line_id': pstl_id.account_move_line_id.sale_line_ids.id,
                            'name': name,
                            'qty': pstl_id.return_qty,
                            'display_type': pstl_id.display_type,
                            'return_location': pstl_id.return_location.id,
                            'sol_name': pstl_id.name,
                            'sol_product_id': pstl_id.product_id.id,
                            'sol_product_uom_qty': pstl_id.account_move_line_id.sale_line_ids.product_uom_qty,
                            'sol_pt_total': (pstl_id.account_move_line_id.price_total/pstl_id.account_move_line_id.quantity) * pstl_id.return_qty if pstl_id.account_move_line_id.price_total else 0,
                            'tax_id': pstl_id.account_move_line_id.sale_line_ids.tax_id,
                            # 'pt_total': pstl_id.account_move_line_id.sale_line_ids.pt_total,
                        }).id)
                res['post_sale_order_line_ids'] = post_sale_order_line_ids
            elif self.env.context.get('default_post_sale_type', '') == 'Remake':
                pass
            elif self.env.context.get('default_post_sale_type', '') == 'Warranty':
                pass
        return res

    def action_confirm(self):
        if self.post_sale_type == "Exchange":
            # if self.post_sale_amount > self.amount_total:
            #     raise odoo.exceptions.ValidationError("Exchange order can't have -ve amount.")
            product = self.env['product.product'].sudo().search([('name', '=', 'Exchange')], limit=1)
            if not product.id:
                product = self.env['product.product'].create({
                    'name': 'Exchange',
                    'type': 'service',
                    'spec_product_type': None,
                })
            tax_ids = self.post_sale_order_line_ids.mapped(lambda x: x.tax_id.ids)
            self.env['sale.order.line'].create({
                'order_id': self.id,
                'sequence': -1,
                'product_id': product.id,
                'name': "Exchange",
                'pt_resp': -float(self.post_sale_amount),
                'price_unit': -float(self.post_sale_amount),
                # 'insurance_id': self.order_line[0].insurance_id.id,
                # 'tax_id': [item for sublist in tax_ids for item in sublist],
            })
        if self.post_sale_type == "Warranty":
            if self.amount_total < 0:
                raise odoo.exceptions.ValidationError("Warranty order can't have -ve amount.")
        res = super(SaleOrder, self).action_confirm()
        if self.post_sale_type == "Remake":
            if self.amount_total != 0:
                raise odoo.exceptions.ValidationError("Remake order can't have -ve or +ve amount.")
            post_sale_lines_transactions_ids = [(5, 0, 0)]
            post_sale_order_ref = self.post_sale_order_ref.name
            # post_sale_order_ref = self.post_sale_order_line_ids[0].sale_order_line_id.order_id.name
            so = self.env['sale.order'].search([('name', '=', post_sale_order_ref)])
            stock_picking_ids = self.env['stock.picking'].search([('origin', '=', post_sale_order_ref),('state', '!=', 'cancel')])
            for order_line in self.order_line.filtered(lambda x:x.return_location.id != 0):
                move_line_id = order_line.post_sale_order_line_id.invoice_lines.filtered(lambda x: x.move_id.type == 'out_invoice'
                                                                                         and x.partner_id == self.partner_id).id
                post_sale_lines_transactions_ids.append((0, 0, {
                    'check': True if order_line.display_type != "line_section" else False,
                    'account_move_line_id': move_line_id,
                    'product_id': order_line.product_id.id,
                    'display_type': order_line.display_type,
                    'name': order_line.name,
                    'qty': order_line.product_uom_qty if order_line.product_uom_qty > 0 else order_line.product_uom_qty * -1,
                    'return_location': order_line.return_location.id,
                    'return_qty': order_line.product_uom_qty if order_line.product_uom_qty > 0 else order_line.product_uom_qty * -1,
                    'company_id': self.env.company.id,
                    'original_location_id': stock_picking_ids[0].location_id.id if len(stock_picking_ids) > 1 else stock_picking_ids.location_id.id,
                    'uom_qty': order_line.product_qty if order_line.product_qty > 0 else 1,
                }))

            post_sale_transactions_id = self.env['post.sale.transactions'].create({
                'post_sale_reasons_id': self.env['post.sale.reasons'].search([])[0].id,
                'date': fields.Date.today(),
                'sale_order_id': so.id,
                'type': 'Remake',
                'stock_picking_ids': stock_picking_ids.ids,
                'post_sale_lines_transactions_ids': post_sale_lines_transactions_ids,
            })
            post_sale_transactions_id.delivery_move()
            lab_details_id = {x.lab_details_id.id for x in self.order_line if 'REMK' in self.order_line[0].name}
            for key in lab_details_id:
                order_lines = self.order_line.filtered(lambda x: x.lab_details_id.id == key and x.display_type != "line_section" and x.return_location.id != 0)
                for order_line in order_lines:
                    post_sale_order_ref = order_line.post_sale_order_line_id
                    post_sale_order_ref.processed_in_post_sale = True
        if self.post_sale_type == "Warranty":
            lab_details_id = {x.lab_details_id.id for x in self.order_line if 'WTY' in self.order_line[0].name}

            post_sale_lines_transactions_ids = [(5, 0, 0)]
            post_sale_order_ref = self.post_sale_order_ref.name
            so = self.env['sale.order'].search([('name', '=', post_sale_order_ref)])
            stock_picking_ids = self.env['stock.picking'].search([('origin', '=', post_sale_order_ref),('state', '!=', 'cancel')])
            for order_line in self.order_line.filtered(lambda x: x.return_location.id != 0):
                move_line_id = order_line.post_sale_order_line_id.invoice_lines.filtered(lambda x: x.move_id.type == 'out_invoice'
                                                                                         and x.partner_id == self.partner_id).id
                post_sale_lines_transactions_ids.append((0, 0, {
                    'check': True if order_line.display_type != "line_section" else False,
                    'account_move_line_id': move_line_id,
                    'product_id': order_line.product_id.id,
                    'display_type': order_line.display_type,
                    'name': order_line.name,
                    'qty': order_line.product_uom_qty * -1 if order_line.product_uom_qty < 0 else order_line.product_uom_qty,
                    'return_location': order_line.return_location.id,
                    'return_qty': order_line.product_uom_qty * -1 if order_line.product_uom_qty < 0 else order_line.product_uom_qty,
                    'company_id': self.env.company.id,
                    'original_location_id': stock_picking_ids[0].location_id.id if len(stock_picking_ids) > 1 else stock_picking_ids.location_id.id,
                    'uom_qty': order_line.product_qty if order_line.product_qty > 0 else 1,
                }))

            post_sale_transactions_id = self.env['post.sale.transactions'].create({
                'post_sale_reasons_id': self.env['post.sale.reasons'].search([])[0].id,
                'date': fields.Date.today(),
                'sale_order_id': so.id,
                'type': 'Exchange',
                'stock_picking_ids': stock_picking_ids.ids,
                'post_sale_lines_transactions_ids': post_sale_lines_transactions_ids,
            })
            post_sale_transactions_id.delivery_move()

            for key in lab_details_id:
                order_lines = self.order_line.filtered(lambda x: x.lab_details_id.id == key and x.display_type != "line_section" and x.return_location.id != 0)
                for order_line in order_lines:
                    post_sale_order_ref = order_line.post_sale_order_line_id
                    post_sale_order_ref.processed_in_post_sale = True
        if self.post_sale_type == "Exchange":
            post_sale_lines_transactions_ids = [(5, 0, 0)]
            post_sale_order_ref = self.post_sale_order_ref.name
            # post_sale_order_ref = self.post_sale_order_line_ids[0].sale_order_line_id.order_id.name
            so = self.env['sale.order'].search([('name', '=', post_sale_order_ref)])
            stock_picking_ids = self.env['stock.picking'].search([('origin', '=', post_sale_order_ref),('state', '!=', 'cancel')])
            for psol_id in self.post_sale_order_line_ids:
                if psol_id.return_location.id:
                    move_line_id = psol_id.sale_order_line_id.invoice_lines.filtered(lambda x: x.move_id.type == 'out_invoice' and x.partner_id == self.partner_id).ids[0]
                    # move_line_id = psol_id.sale_order_line_id.invoice_lines.filtered(lambda x: x.partner_id == self.partner_id).id

                    post_sale_lines_transactions_ids.append((0, 0, {
                        'check': True if psol_id.display_type != "line_section" else False,
                        'account_move_line_id': move_line_id,
                        'product_id': psol_id.sol_product_id.id,
                        'display_type': psol_id.display_type,
                        'name': psol_id.name,
                        'qty': psol_id.qty,
                        'return_location': psol_id.return_location.id,
                        'return_qty': psol_id.qty,
                        'company_id': self.env.company.id,
                        'original_location_id': stock_picking_ids[0].location_id.id if len(stock_picking_ids) > 1 else stock_picking_ids.location_id.id,
                        'uom_qty': psol_id.sale_order_line_id.product_qty
                                        if psol_id.sale_order_line_id.product_qty > 0 else 1,
                    }))

            post_sale_transactions_id = self.env['post.sale.transactions'].create({
                'post_sale_reasons_id': self.env['post.sale.reasons'].search([])[0].id,
                'date': fields.Date.today(),
                'sale_order_id': so.id,
                'type': 'Exchange',
                'stock_picking_ids': stock_picking_ids.ids,
                'post_sale_lines_transactions_ids': post_sale_lines_transactions_ids,
            })
            post_sale_transactions_id.delivery_move()
            lab_details_id = {x.sale_order_line_id.lab_details_id.id for x in self.post_sale_order_line_ids}
            for key in lab_details_id:
                post_sale_order_line_ids = self.post_sale_order_line_ids.filtered(lambda x: x.sale_order_line_id.lab_details_id.id == key and x.display_type != "line_section" and x.return_location.id != 0)
                for post_sale_order_line_id in post_sale_order_line_ids:
                    post_sale_order_ref = post_sale_order_line_id.sale_order_line_id
                    post_sale_order_ref.processed_in_post_sale = True

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.type == 'out_invoice')
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    def action_view_post_sale_exchange_delivery(self):
        values = {
            'name': _('Return'),
            'res_model': 'stock.picking',
            # 'view_id': self.env.ref('stock.view_picking_form').id,
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
        if self.post_sale_exchange_delivery == 1:
            values['view_mode'] = 'form'
            values['res_id'] = self.post_sale_exchange_delivery = self.env['stock.picking']\
                .search([('post_sale_order_ref', '=', self.post_sale_order_ref.id)]).id
            return values
        else:
            values['view_mode'] = 'tree,form'
            values['domain'] = [('post_sale_order_ref', '=',self.post_sale_order_ref.id)]
            return values

    def action_post_sale_return(self):
        return {
            'name': _('Return'),
            'res_model': 'post.sale.transactions',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.post_sale_transactions_view').id,
            'context': {
                'default_type': 'Return',
                'default_sale_order_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_post_sale_exchange(self):
        return {
            'name': _('Exchange'),
            'res_model': 'post.sale.transactions',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.post_sale_transactions_view').id,
            'context': {
                'default_type': 'Exchange',
                'default_sale_order_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_post_sale_remake(self):
        return {
            'name': _('Remake'),
            'res_model': 'post.sale.transactions',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.post_sale_transactions_view').id,
            'context': {
                'default_type': 'Remake',
                'default_sale_order_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_post_sale_warranty(self):
        return {
            'name': _('Warranty'),
            'res_model': 'post.sale.transactions',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.post_sale_transactions_view').id,
            'context': {
                'default_type': 'Warranty',
                'default_sale_order_id': self.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_view_customer_note(self):
        invoices = self.order_line.invoice_lines.move_id.filtered(lambda r: r.type == 'out_refund')
        # invoices = self.mapped(invoice_ids)
        self.order_line.invoice_lines.move_id.filtered(lambda r: r.type == 'out_refund')
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        if len(invoices) > 0:
            action['domain'] = [('type', '=', 'out_refund'), ('id', 'in', invoices.ids)]
        # elif len(invoices) == 1:
        #     form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        #     if 'views' in action:
        #         action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        #     else:
        #         action['views'] = form_view
        #     action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_refund',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.mapped('name'),
                'default_user_id': self.user_id.id,
            })
        action['context'] = context
        return action

    def action_invoice_register_payment(self):
        context = self.env.context.copy()
        context['active_ids'] = [self.id]
        return {
            'name': _('Register Payment'),
            'res_model': 'multi.invoice.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.multi_invoice_payment_form').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
        # inv = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', self.name)], limit=1)
        # if inv and self.invoice_payment_state == 'not_paid':
        #     sum = 0
        #     if self.invoice_payments_widget:
        #         sum = self.invoice_amount_residual
        #     #     for b in json.loads(self.invoice_payments_widget)['content']:
        #     #         sum += b['amount']
        #     return self.env['account.payment'].with_context(default_so_balance=sum,default_from_sale_order=True,active_ids=inv.ids, active_model='account.move', active_id=inv.id,rec_id=self.id).action_register_payment()

    def action_multi_register_payment(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        return {
            'name': _('Register Multiple Payment'),
            'res_model': 'multi.invoice.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.multi_invoice_payment_form').id,
            'context': self.env.context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    # def action_invoice_register_multiple_payment(self,invoices):
    #     # 'account.payment.register'
    #     Payment = self.env['account.payment']
    #     inv = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', self.name)], limit=1)
    #     if inv and self.invoice_payment_state == 'not_paid':
    #         payments = Payment.create(inv.manual_creation())
    #
    #         payments.post()
