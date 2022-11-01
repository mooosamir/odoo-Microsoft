# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class PostSaleTransactions(models.TransientModel):
    _name = 'post.sale.transactions'
    _description = 'post sale transactions'

    sale_order_id = fields.Many2one('sale.order', required=True)
    account_move_id = fields.Many2one('account.move', readonly=True)
    post_sale_reasons_id = fields.Many2one('post.sale.reasons', string="Reason", required=True)
    post_sale_lines_transactions_ids = fields.One2many("post.sale.transactions.lines", "post_sale_transactions_id", required=True)
    # vendor_return = fields.Boolean(string="Generate Vendor Return")
    # re_order = fields.Boolean(string="Re-order")
    date = fields.Date(string='Reversal date', default=fields.Date.context_today, required=True)
    type = fields.Selection([('Return', 'Return'), ('Remake', 'Remake'),
                             ('Exchange', 'Exchange'), ('Warranty', 'Warranty'),
                             ], required=True)
    stock_picking_ids = fields.Many2many('stock.picking', 'pst_stock_picking_id_rel')

    @api.model
    def default_get(self, fields_list):
        res = super(PostSaleTransactions, self).default_get(fields_list)
        if 'sale_order_id' in res:
            so = self.env['sale.order'].search([('id', '=', res['sale_order_id'])])
            inv = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', so.name)],
                                                  limit=1)
            stock_picking_ids = self.env['stock.picking'].search([('origin', '=', so.name), ('state', '!=', 'cancel')])
            invoice_line_ids = inv.invoice_line_ids
            out_invoice_invoice_line_ids = {x.sale_line_ids.id: x.id for x in invoice_line_ids}
            invoice_qty = {}
            out_refund_invs = self.env['account.move'].search([('type', '=', 'out_refund'),
                                                               ('invoice_origin', '=', so.name)])
            for out_refund_inv in out_refund_invs:
                out_refund_invoice_line_ids = {x.sale_line_ids.id: x for x in out_refund_inv.invoice_line_ids}
                for k in out_refund_invoice_line_ids:
                    if k in out_invoice_invoice_line_ids:
                        invoice_qty[k] = invoice_qty.get(k, 0) - out_refund_invoice_line_ids[k].quantity

            exchange_sale_orders  = self.env['sale.order'].search([('post_sale_type', '=', 'Exchange'),
                                                                   ('post_sale_order_ref', '=', so.id),
                                                                   ('state', '!=', 'cancel')])
            for exchange_sale_order in exchange_sale_orders:
                exchange_sale_order_sale_line_ids = {x.sale_order_line_id.id: x for x in exchange_sale_order.post_sale_order_line_ids}
                for k in exchange_sale_order_sale_line_ids:
                    if k in out_invoice_invoice_line_ids:
                        invoice_qty[k] = invoice_qty.get(k, 0) - exchange_sale_order_sale_line_ids[k].qty

            post_sale_lines_transactions_ids = [(5, 0, 0)]
            for account_move_line in invoice_line_ids:
                if account_move_line.name not in ["Exchange"] and account_move_line.product_id.name not in ["Promotion"]:
                    quantity = account_move_line.quantity + invoice_qty[
                        account_move_line.sale_line_ids.id] if account_move_line.sale_line_ids.id in invoice_qty else account_move_line.quantity

                    post_sale_lines_transactions_ids.append((0, 0, {
                        'display_type': 'line_section' if account_move_line.display_type == "line_section" else None,
                        'name': account_move_line.name,
                        'account_move_line_id': account_move_line.id,
                        'product_id': account_move_line.product_id.id,
                        'qty': quantity if quantity > 0 else 0,
                        'uom_qty': account_move_line.sale_line_ids.product_qty if account_move_line.sale_line_ids.product_qty > 0 else 0,
                        # 'uom_qty': quantity if quantity > 0 else 0,
                        # 'uom_qty': account_move_line.product_id.uom_id.factor + account_move_line.product_id.uom_id.factor_inv,
                        'return_qty': quantity if quantity > 0 else 0,
                        'original_location_id': stock_picking_ids[0].location_id.id,
                        'company_id': self.env.company.id,
                        'processed_in_post_sale': account_move_line.sale_line_ids.processed_in_post_sale,
                    }))
            res['account_move_id'] = inv.id
            res['post_sale_lines_transactions_ids'] = post_sale_lines_transactions_ids
            res['stock_picking_ids'] = stock_picking_ids.ids
        return res

    def post(self):
        for line in self.post_sale_lines_transactions_ids:
            if (line.type in ['Remake', 'Warranty'] and line.re_order and not line.return_location.id) or \
                    (line.type not in ['Remake', 'Warranty'] and line.check and not line.return_location.id):
                raise exceptions.ValidationError("Return location missing in 1 or more selected lines.")

        if self.type == 'Return':
            invoice_order_line = {x.account_move_line_id.lab_details_id.id: self.post_sale_lines_transactions_ids.filtered(
                lambda y: y.check and y.return_qty > 0 and
                          y.account_move_line_id.display_type != "line_section" and
                          y.account_move_line_id.lab_details_id == x.account_move_line_id.lab_details_id)
                for x in self.post_sale_lines_transactions_ids}
            invoice_order_line = {k: v for k, v in invoice_order_line.items() if len(v)}
            # Insurance invoice
            insurance_order_lines = {x.account_move_line_id.insurance_id: self.post_sale_lines_transactions_ids.filtered(
                lambda y: y.check and y.return_qty > 0 and
                          y.account_move_line_id.display_type != "line_section" and
                          y.account_move_line_id.insurance_id == x.account_move_line_id.insurance_id)
                for x in self.post_sale_lines_transactions_ids}
            insurance_order_lines = {k: v for k, v in insurance_order_lines.items() if len(v) and k.id != 0}
            # Cancel insurance invoice
            for insurance_order_line in insurance_order_lines:
                for insurance_invoice in self.sale_order_id.invoice_ids.filtered(lambda x:x.partner_id == insurance_order_line.carrier_id):
                    insurance_invoice.button_cancel()
            # Promotion Lines
            for key in invoice_order_line:
                promotion = self.sale_order_id.order_line.filtered(lambda x: x.product_id.name == "Promotion" and x.lab_details_id.id == key)
                if promotion.id:
                    account_move_line = promotion.invoice_lines[0]
                    if account_move_line.id:
                        price = account_move_line.price_subtotal * -1
                        promotion_lines = self.post_sale_lines_transactions_ids.filtered(lambda x:x.account_move_line_id.lab_details_id.id == key and x.account_move_line_id.display_type != "line_section")
                        sale_lines = self.sale_order_id.order_line.filtered(lambda x: x.lab_details_id.id == key and x.display_type != "line_section" and x.product_uom_qty > 0 and x.product_id.name not in ['Exchange','Promotion'])
                        actual_sum = 0
                        for line in sale_lines.mapped(lambda x: x.invoice_lines[0].quantity):
                            actual_sum += line
                        promo_sum = 0
                        if promotion.promotion_id.promotion_type != 'buy_x_get_y':
                            for promotion_line in promotion_lines:
                                if promotion_line.check:
                                    promo_sum += promotion_line.return_qty
                            price = (price/actual_sum) * promo_sum
                        price = price * -1
                        invoice_order_line[key] += self.env['post.sale.transactions.lines'].create({
                            'post_sale_transactions_id': self.id,
                            'display_type': None,
                            'name': "Promotion~" + str(price),
                            'account_move_line_id': account_move_line.id,
                            'product_id': account_move_line.product_id.id,
                            'qty': 1,
                            'uom_qty': account_move_line.sale_line_ids.product_qty if account_move_line.sale_line_ids.product_qty > 0 else 1,
                            'return_qty': 1,
                            'original_location_id': self.stock_picking_ids[0].location_id.id,
                            'company_id': self.env.company.id,
                            'processed_in_post_sale': account_move_line.sale_line_ids.processed_in_post_sale,
                        })

            if invoice_order_line:
                for pstl_id in invoice_order_line:
                    line_section = self.sale_order_id.order_line.filtered(
                        lambda x: x.lab_details_id.id == pstl_id and x.display_type == "line_section")
                    self.env['post.sale.order.line'].create({
                        'sale_order_line_id': line_section.id,
                        'name': "RETURN " + line_section.name,
                        'display_type': line_section.display_type,
                        'sol_name': line_section.name,
                        'sol_product_id': line_section.product_id.id,
                        'sol_product_uom_qty': line_section.product_uom_qty,
                        'sale_order_id': self.sale_order_id.id
                    })
                    for order_line in invoice_order_line[pstl_id]:
                        if "Promotion~" in order_line.name:
                            name = order_line.name.split("~")[0]
                            self.env['post.sale.order.line'].create({
                                'sale_order_line_id': order_line.account_move_line_id.sale_line_ids.id,
                                'name': name,
                                'qty': order_line.qty,
                                'display_type': order_line.display_type,
                                'return_location': order_line.return_location.id,
                                'sol_name': order_line.name,
                                'sol_product_id': order_line.product_id.id,
                                'sol_product_uom_qty': order_line.account_move_line_id.sale_line_ids.product_uom_qty,
                                'sol_pt_total': float(order_line.name.split("~")[1]),
                                'tax_id': order_line.account_move_line_id.sale_line_ids.tax_id,
                                'sale_order_id': self.sale_order_id.id
                            })
                        else:
                            name = "RETURN " + order_line.name if order_line.display_type == 'line_section' else order_line.name
                            self.env['post.sale.order.line'].create({
                                'sale_order_line_id': order_line.account_move_line_id.sale_line_ids.id,
                                'name': name,
                                'qty': order_line.return_qty,
                                'display_type': order_line.display_type,
                                'return_location': order_line.return_location.id,
                                'sol_name': order_line.name,
                                'sol_product_id': order_line.product_id.id,
                                'sol_product_uom_qty': order_line.account_move_line_id.sale_line_ids.product_uom_qty,
                                'sol_pt_total': order_line.account_move_line_id.sale_line_ids.pt_total,
                                'tax_id': order_line.account_move_line_id.sale_line_ids.tax_id,
                                'sale_order_id': self.sale_order_id.id
                            })

                post_sale_lines_transactions_ids = self.post_sale_lines_transactions_ids
                delivery_order_lines = {x.return_location.id: post_sale_lines_transactions_ids.filtered(
                    lambda y: y.check and y.return_qty > 0 and
                              y.account_move_line_id.display_type != "line_section" and
                              y.return_location == x.return_location)
                    for x in post_sale_lines_transactions_ids if not x.return_location.scrap_location}
                delivery_order_lines = {k: v for k, v in delivery_order_lines.items() if len(v)}

                done_picking_ids = self.stock_picking_ids.filtered(lambda x: x.state == 'done')
                not_done_picking_ids = self.stock_picking_ids.filtered(lambda x: x.state != 'done')

                for pslt_id in post_sale_lines_transactions_ids.filtered(lambda x: x.return_location.scrap_location):
                    uom_qty = pslt_id.uom_qty / pslt_id.account_move_line_id.quantity if pslt_id.uom_qty and pslt_id.account_move_line_id.quantity else 0
                    picking_id = self.stock_picking_ids.move_lines.filtered(
                        lambda x: x.product_id.id == pslt_id.product_id.id and
                                  x.product_qty >= (pslt_id.qty * uom_qty)).picking_id.id
                    stock_scrap = self.env['stock.scrap'].create({
                        'picking_id': picking_id,
                        'product_id': pslt_id.product_id.id,
                        'product_uom_id': pslt_id.product_id.uom_id.id,
                        'company_id': pslt_id.company_id.id,
                        'scrap_qty': pslt_id.return_qty,
                        'scrap_location_id': pslt_id.return_location.id,
                    })
                    stock_scrap.action_validate()

                # if (not len(not_done_picking_ids) and len(done_picking_ids) > 0) or \
                #         (not len(done_picking_ids) and len(not_done_picking_ids) > 0):
                for done_picking_id in done_picking_ids:
                    for delivery_order_line in delivery_order_lines:
                        reverse_delivery = self.env['stock.return.picking'] \
                            .with_context(post_sale_orderlines=delivery_order_lines[delivery_order_line]).create({
                            'picking_id': done_picking_id.id,
                            'location_id': delivery_order_line,
                        })
                        return_post_sale_orderlines = reverse_delivery._post_sale_onchange_picking_id()
                        if len(return_post_sale_orderlines) > 0:
                            post_sale_lines_transactions_ids = post_sale_lines_transactions_ids.filtered(lambda x: x.id not in return_post_sale_orderlines.ids)
                            delivery_order_lines = {x.return_location.id: post_sale_lines_transactions_ids.filtered(
                                lambda y: y.check and y.return_qty > 0 and
                                          y.account_move_line_id.display_type != "line_section" and
                                          y.return_location == x.return_location)
                                for x in post_sale_lines_transactions_ids}
                            delivery_order_lines = {k: v for k, v in delivery_order_lines.items() if len(v)}
                            res_id = reverse_delivery.create_returns()['res_id']
                            stock_picking_id = self.env['stock.picking'].search([('id', '=', res_id)])
                            wiz_act = stock_picking_id.button_validate()
                            wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
                            wiz.process()
                        else:
                            reverse_delivery.unlink()

                for not_done_picking_ids in not_done_picking_ids:
                    delivery_order_lines = [y for y in post_sale_lines_transactions_ids if y.check and y.return_qty > 0 and
                                            y.account_move_line_id.display_type != "line_section"]
                    move_id = []
                    return_post_sale_orderlines = self.env['post.sale.transactions.lines']
                    for delivery_order_line in delivery_order_lines:
                        for line in not_done_picking_ids.move_ids_without_package:
                            uom_qty = delivery_order_line.uom_qty/delivery_order_line.account_move_line_id.quantity if delivery_order_line.uom_qty and delivery_order_line.account_move_line_id.quantity else 0
                            if line.product_id.id == delivery_order_line.product_id.id and line.id not in move_id \
                                    and line.product_qty >= (delivery_order_line.qty * uom_qty) and \
                                    (line.quantity_done == 0 or
                                     line.quantity_done >= (delivery_order_line.qty * uom_qty)):
                                return_post_sale_orderlines += delivery_order_line
                                line.product_uom_qty -= (delivery_order_line.return_qty * uom_qty)
                                if line.quantity_done > 0:
                                    line.quantity_done -= (delivery_order_line.return_qty * uom_qty)
                                if line.reserved_availability > 0:
                                    if line.reserved_availability >= (delivery_order_line.return_qty * uom_qty):
                                        line.reserved_availability -= (delivery_order_line.return_qty * uom_qty)
                                    elif (delivery_order_line.return_qty * uom_qty) > line.reserved_availability > line.quantity_done:
                                        line.reserved_availability = line.quantity_done

                                # for line in self.stock_picking_ids[0].move_line_ids_without_package:
                                #     if line.product_id.id == delivery_order_line.product_id.id \
                                #             and line.product_qty >= delivery_order_line.qty and \
                                #             (line.qty_done == 0 or line.qty_done >= delivery_order_line.qty) and \
                                #             line.id not in move_id:
                                #         if line.product_qty == delivery_order_line.return_qty:
                                #             line.unlink()
                                #         else:
                                #             line.product_qty -= delivery_order_line.return_qty
                                #             if line.qty_done > 0:
                                #                 line.qty_done -= delivery_order_line.return_qty
                                move_id.append(line.id)

                    if len(return_post_sale_orderlines) > 0:
                        post_sale_lines_transactions_ids = post_sale_lines_transactions_ids.filtered(
                            lambda x: x.id not in return_post_sale_orderlines.ids)

                # Customer Note (Invoice), posted and payment registered
                default_values = [{
                    'ref': _('RETURN : %s') % self.account_move_id.name,
                    'date': self.date or self.account_move_id.date,
                    'invoice_date': self.account_move_id.is_invoice(include_receipts=True) and (
                                self.date or self.account_move_id.date) or False,
                    'journal_id': self.account_move_id.journal_id.id,
                    'invoice_payment_term_id': None,
                    'auto_post': True if self.date > fields.Date.context_today(self) else False,
                    'invoice_user_id': self.account_move_id.invoice_user_id.id,
                }]
                reverse_moves = self.account_move_id._post_sale_reverse_moves(default_values,
                                                                              post_sale_orderlines=invoice_order_line,
                                                                              cancel=False)
                reverse_moves.post()
                for key in invoice_order_line.keys():
                    # return_post_sale = self.sale_order_id.order_line.filtered(lambda x: x.lab_details_id.id == key)
                    for data in invoice_order_line[key]:
                        data.account_move_line_id.sale_line_ids.processed_in_post_sale = True
                # self.sale_order_id.post_sale_ref = (4, 0, self.sale_order_id.id)
                self.sale_order_id.post_sale_reasons_id = self.post_sale_reasons_id.id

            # Invoice Payment
            # reverse_moves_payment = self.env['account.payment']\
            #     .with_context(default_from_sale_order=True, active_ids=reverse_moves.ids, active_id=reverse_moves.id,
            #                  active_model='account.move', rec_id=self.sale_order_id.id)\
            #     .create({'payment_method_id': self.env['account.payment.method'].search([], limit=1).id,
            #              'journal_id': self.env['account.journal']
            #             .search([('type', 'in', ('bank', 'cash')), ('company_id', '=', self.env.company.id)], limit=1).id})
            # reverse_moves_payment._onchange_amount()
            # reverse_moves_payment._onchange_journal()
            # reverse_moves_payment._onchange_payment_type()
            # reverse_moves_payment.post()

            # New Sale Order
            # new_so = self.sale_order_id.copy_data()[0]
            # new_so['order_line'] = []
            # invoice_order_line = {x.account_move_line_id.sale_line_ids: self.post_sale_lines_transactions_ids.filtered(
            #     lambda y: y.check and y.return_qty > 0 and
            #               y.account_move_line_id.display_type != "line_section" and
            #               y.account_move_line_id.lab_details_id == x.account_move_line_id.lab_details_id)
            #     for x in self.post_sale_lines_transactions_ids if x.account_move_line_id.display_type == "line_section"}
            # invoice_order_line = {k: v for k, v in invoice_order_line.items() if len(v)}
            #
            # for k,v in invoice_order_line.items():
            #     new_so['order_line'].append((0, 0, k.copy_data()[0]))
            #     for post_sale_line in v:
            #         new_sale_order_line = v.account_move_line_id.sale_line_ids.copy_data()[0]
            #         new_sale_order_line['product_uom_qty'] = v.return_qty * -1
            #         new_so['order_line'].append((0, 0, new_sale_order_line))
            #
            # refund_so = self.env['sale.order'].create(new_so)
            # refund_so.with_context(no_invoice_create=True).action_confirm()
        elif self.type == "Exchange":
            pstl_id = {x: self.post_sale_lines_transactions_ids.filtered(
                        lambda y: y.check and y.return_qty > 0 and
                                  y.account_move_line_id.display_type != "line_section" and
                                  y.account_move_line_id.lab_details_id == x.account_move_line_id.lab_details_id)
                        for x in self.post_sale_lines_transactions_ids if x.account_move_line_id.display_type == "line_section"}
            # iol = []
            # for k, v in invoice_order_line.items():
            #     if len(v):
            #         iol.append(k.id)
            #         for line in v:
            #             iol.append(v.id)

            # Promotion Lines
            for key in pstl_id:
                if len(pstl_id[key]) > 0:
                    lab_details_id = key.account_move_line_id.lab_details_id.id
                    promotion = self.sale_order_id.order_line.filtered(lambda x: x.product_id.name == "Promotion" and x.lab_details_id.id == lab_details_id)
                    if promotion.id:
                        account_move_line = promotion.invoice_lines[0]
                        if promotion.invoice_lines[0].id:
                            price = account_move_line.price_subtotal * -1
                            promotion_lines = self.post_sale_lines_transactions_ids.filtered(lambda x:x.account_move_line_id.lab_details_id.id == lab_details_id and x.account_move_line_id.display_type != "line_section")
                            sale_lines = self.sale_order_id.order_line.filtered(lambda x: x.lab_details_id.id == lab_details_id and x.display_type != "line_section" and x.product_uom_qty > 0)
                            actual_sum = 0
                            for line in sale_lines.mapped(lambda x: x.invoice_lines[0].quantity):
                                actual_sum += line
                            promo_sum = 0
                            if promotion.promotion_id.promotion_type != 'buy_x_get_y':
                                for promotion_line in promotion_lines:
                                    if promotion_line.check:
                                        promo_sum += promotion_line.return_qty
                                price = (price/actual_sum) * promo_sum
                            price = price * -1
                            pstl_id[key] += self.env['post.sale.transactions.lines'].create({
                                'post_sale_transactions_id': self.id,
                                'display_type': None,
                                'name': "Promotion~" + str(price),
                                'account_move_line_id': account_move_line.id,
                                'product_id': account_move_line.product_id.id,
                                'qty': 1,
                                'uom_qty': account_move_line.sale_line_ids.product_qty if account_move_line.sale_line_ids.product_qty > 0 else 1,
                                'return_qty': 1,
                                'original_location_id': self.stock_picking_ids[0].location_id.id,
                                'company_id': self.env.company.id,
                                'processed_in_post_sale': account_move_line.sale_line_ids.processed_in_post_sale,
                            })
            pstl_id = [[k.id] + [line.id for line in v] for k, v in pstl_id.items() if len(v) > 0]
            # pstl_id = [(y for x in ([k.id] + [line.id for line in v]) for y in x) for k, v in pstl_id.items() if len(v) > 0]
            pstl_id = [item for sublist in pstl_id for item in sublist]
            if len({x.account_move_line_id.lab_details_id.id for x in self.env['post.sale.transactions.lines'].search([('id', 'in', pstl_id)])}) > 1:
                raise exceptions.ValidationError("Only 1 order type can be selected for exchange")
            current_sale_order = self.sale_order_id.copy_data()[0]
            current_sale_order['order_line'] = []
            current_sale_order['post_sale_type'] = 'Exchange'
            if 'post_sale_order_line_ids'in current_sale_order:
                del (current_sale_order['post_sale_order_line_ids'])
            new_sale_order = self.env['sale.order']\
                .with_context(post_sale_transactions_lines_ids=pstl_id,
                              default_post_sale_type= 'Exchange',
                              default_post_sale_order_ref = self.sale_order_id.id)\
                .create(current_sale_order)
            if new_sale_order.id:
                new_sale_order.update({
                    'name': "EXCHG " + new_sale_order.name,
                    'post_sale_order_ref': self.sale_order_id.id,
                    'post_sale_reasons_id': self.post_sale_reasons_id.id,
                })
                pstl_id = self.env['post.sale.transactions.lines'].search([('id', 'in', pstl_id)])
                name = pstl_id.filtered(lambda x:x.display_type == "line_section").name
                if 'Lenses Only' in name:
                    lens = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens')
                    lens_treatment = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    lab_details_id = pstl_id.account_move_line_id.lab_details_id
                    pstl_id = self.post_sale_lines_transactions_ids.filtered(lambda x:x.account_move_line_id.lab_details_id.id == lab_details_id.id and x.id not in pstl_id.ids)
                    a_lens = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens')
                    a_lens_treatment = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    context = {'so_id': new_sale_order.id, 'order_ref': "Lenses Only", 'partner_id': new_sale_order.partner_id.id,
                                    'domain_rx': 'glasses'}
                    if len(a_lens) >= 1 or len(a_lens_treatment) >= 1:
                        context['default_is_post_sale'] = True
                        if len(a_lens) >= 1:
                            context['default_is_lens'] = 1
                            context['default_lens_products'] = a_lens.account_move_line_id.sale_line_ids.product_id.id
                        if len(a_lens_treatment) >= 1:
                            lens_treatment = [(5, 0, 0)]
                            lenstreatment_products_ids = [(5, 0, 0)]
                            for line in a_lens_treatment:
                                lenstreatment_products_ids.append((0, 0,
                                                                   {'lenstreatment_products_id': line.account_move_line_id.sale_line_ids.product_id.id,
                                                                    'return_location': line.return_location.id,
                                                                    'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                                lens_treatment.append((4, line.account_move_line_id.sale_line_ids.product_id.id))
                            context['default_lenstreatment_products'] = lens_treatment
                            context['default_lenstreatment_products_ids'] = lenstreatment_products_ids

                        # patients own frame (copy to new multi order)
                        context['default_model_number'] = lab_details_id.model_number
                        context['default_color_patient_frame'] = lab_details_id.color_patient_frame
                        context['default_a'] = lab_details_id.a
                        context['default_b'] = lab_details_id.b
                        context['default_dbl'] = lab_details_id.dbl
                        context['default_ed'] = lab_details_id.ed
                        context['default_bridge'] = lab_details_id.bridge
                        context['default_temple'] = lab_details_id.temple
                        context['default_edge_id'] = lab_details_id.edge_id
                        context['default_frame_id'] = lab_details_id.frame_id.id
                        # prescription (copy to new multi order)
                        context['default_prescription_id'] = lab_details_id.prescription_id.id
                        # lab details section (Measurements)(copy to new multi order)
                        context['default_dist_pd_lab_details'] = lab_details_id.dist_pd_lab_details
                        context['default_near_pd_lab_details'] = lab_details_id.near_pd_lab_details
                        context['default_oc_hit_lab_details'] = lab_details_id.oc_hit_lab_details
                        context['default_seg_ht_lab_details'] = lab_details_id.seg_ht_lab_details
                        context['default_bc_lab_details'] = lab_details_id.bc_lab_details
                        context['default_dist_pd_lab_details_os'] = lab_details_id.dist_pd_lab_details_os
                        context['default_near_pd_lab_details_os'] = lab_details_id.near_pd_lab_details_os
                        context['default_oc_hit_lab_details_os'] = lab_details_id.oc_hit_lab_details_os
                        context['default_seg_ht_lab_details_os'] = lab_details_id.seg_ht_lab_details_os
                        context['default_bc_lab_details_os'] = lab_details_id.bc_lab_details_os
                        context['default_panto_lab_details'] = lab_details_id.panto_lab_details
                        context['default_thickness_lab_details'] = lab_details_id.thickness_lab_details
                        context['default_wrap_lab_details'] = lab_details_id.wrap_lab_details
                        context['default_vertex_mlab_details'] = lab_details_id.vertex_mlab_details
                        # lab details section (Lens)(copy to new multi order)
                        context['default_eye_lab_details'] = lab_details_id.eye_lab_details
                        # lab details section (Lens Treatement)(copy to new multi order)
                        context['default_tint_color_lab_details'] = lab_details_id.tint_color_lab_details
                        context['default_tint_sample_lab_details'] = lab_details_id.tint_sample_lab_details
                        context['default_mirror_coating_lab_details'] = lab_details_id.mirror_coating_lab_details
                        context['default_by_lab_details'] = lab_details_id.by_lab_details
                        # lab details section (Frame)(copy to new multi order)
                        # context['default_frame_rel'] = lab_details_id.frame_rel
                        context['default_edge_type'] = lab_details_id.edge_type
                        context['default_frame_type'] = lab_details_id.frame_type.id
                        context['default_a_lab_details'] = lab_details_id.a_lab_details
                        context['default_b_lab_details'] = lab_details_id.b_lab_details
                        context['default_dbl_lab_details'] = lab_details_id.dbl_lab_details
                        context['default_ed_lab_details'] = lab_details_id.ed_lab_details
                        # lab details section (Lab Information)(copy to new multi order)
                        context['default_lab_details'] = lab_details_id.lab_details.id
                        context['default_physician_id'] = lab_details_id.physician_id.id
                        context['default_ship_to'] = lab_details_id.ship_to.id
                        context['new_size'] = 'max-width_1180px'

                        return {
                            'type': 'ir.actions.act_window',
                            'res_model': 'multi.order.type',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': context,
                        }
                elif 'Frame Only' in name:
                    frame = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Frames')
                    lens_treatment = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    lab_details_id = pstl_id.account_move_line_id.lab_details_id
                    pstl_id = self.post_sale_lines_transactions_ids.filtered(lambda x:x.account_move_line_id.lab_details_id.id == lab_details_id.id and x.id not in pstl_id.ids)
                    a_lens_treatment = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    a_frame = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Frames')
                    context = {'so_id': new_sale_order.id, 'order_ref': "Frame Only", 'partner_id': new_sale_order.partner_id.id}
                    if len(a_frame) >= 1 or len(a_lens_treatment) >= 1:
                        context['default_is_post_sale'] = True
                        if len(a_frame) >= 1:
                            context['default_is_frame'] = 1
                            context['default_frames_products_variants'] = a_frame.account_move_line_id.sale_line_ids.product_template_id.id
                        if len(a_lens_treatment) >= 1:
                            lens_treatment = [(5, 0, 0)]
                            lenstreatment_products_ids = [(5, 0, 0)]
                            for line in a_lens_treatment:
                                lenstreatment_products_ids.append((0, 0,
                                                                   {'lenstreatment_products_id': line.account_move_line_id.sale_line_ids.product_id.id,
                                                                    'return_location': line.return_location.id,
                                                                    'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                                lens_treatment.append((4, line.account_move_line_id.sale_line_ids.product_id.id))
                            context['default_lenstreatment_products'] = lens_treatment
                            context['default_lenstreatment_products_ids'] = lenstreatment_products_ids

                        # patients own frame (copy to new multi order)
                        context['default_model_number'] = lab_details_id.model_number
                        context['default_color_patient_frame'] = lab_details_id.color_patient_frame
                        context['default_a'] = lab_details_id.a
                        context['default_b'] = lab_details_id.b
                        context['default_dbl'] = lab_details_id.dbl
                        context['default_ed'] = lab_details_id.ed
                        context['default_bridge'] = lab_details_id.bridge
                        context['default_temple'] = lab_details_id.temple
                        context['default_edge_id'] = lab_details_id.edge_id
                        context['default_frame_id'] = lab_details_id.frame_id.id
                        # prescription (copy to new multi order)
                        context['default_prescription_id'] = lab_details_id.prescription_id.id
                        # lab details section (Measurements)(copy to new multi order)
                        context['default_dist_pd_lab_details'] = lab_details_id.dist_pd_lab_details
                        context['default_near_pd_lab_details'] = lab_details_id.near_pd_lab_details
                        context['default_oc_hit_lab_details'] = lab_details_id.oc_hit_lab_details
                        context['default_seg_ht_lab_details'] = lab_details_id.seg_ht_lab_details
                        context['default_bc_lab_details'] = lab_details_id.bc_lab_details
                        context['default_dist_pd_lab_details_os'] = lab_details_id.dist_pd_lab_details_os
                        context['default_near_pd_lab_details_os'] = lab_details_id.near_pd_lab_details_os
                        context['default_oc_hit_lab_details_os'] = lab_details_id.oc_hit_lab_details_os
                        context['default_seg_ht_lab_details_os'] = lab_details_id.seg_ht_lab_details_os
                        context['default_bc_lab_details_os'] = lab_details_id.bc_lab_details_os
                        context['default_panto_lab_details'] = lab_details_id.panto_lab_details
                        context['default_thickness_lab_details'] = lab_details_id.thickness_lab_details
                        context['default_wrap_lab_details'] = lab_details_id.wrap_lab_details
                        context['default_vertex_mlab_details'] = lab_details_id.vertex_mlab_details
                        # lab details section (Lens)(copy to new multi order)
                        context['default_eye_lab_details'] = lab_details_id.eye_lab_details
                        # lab details section (Lens Treatement)(copy to new multi order)
                        context['default_tint_color_lab_details'] = lab_details_id.tint_color_lab_details
                        context['default_tint_sample_lab_details'] = lab_details_id.tint_sample_lab_details
                        context['default_mirror_coating_lab_details'] = lab_details_id.mirror_coating_lab_details
                        context['default_by_lab_details'] = lab_details_id.by_lab_details
                        # lab details section (Frame)(copy to new multi order)
                        # context['default_frame_rel'] = lab_details_id.frame_rel
                        context['default_edge_type'] = lab_details_id.edge_type
                        context['default_frame_type'] = lab_details_id.frame_type.id
                        context['default_a_lab_details'] = lab_details_id.a_lab_details
                        context['default_b_lab_details'] = lab_details_id.b_lab_details
                        context['default_dbl_lab_details'] = lab_details_id.dbl_lab_details
                        context['default_ed_lab_details'] = lab_details_id.ed_lab_details
                        # lab details section (Lab Information)(copy to new multi order)
                        context['default_lab_details'] = lab_details_id.lab_details.id
                        context['default_physician_id'] = lab_details_id.physician_id.id
                        context['default_ship_to'] = lab_details_id.ship_to.id
                        context['new_size'] = 'max-width_1180px'

                        return {
                            'type': 'ir.actions.act_window',
                            'res_model': 'multi.order.type',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': context,
                        }
                elif 'Complete Pair' in name:
                    frame = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Frames')
                    lens = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens')
                    lens_treatment = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    lab_details_id = pstl_id.account_move_line_id.lab_details_id
                    pstl_id = self.post_sale_lines_transactions_ids.filtered(lambda x:x.account_move_line_id.lab_details_id.id == lab_details_id.id and x.id not in pstl_id.ids)
                    a_lens = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens')
                    a_lens_treatment = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    a_frame = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Frames')
                    context = {'so_id': new_sale_order.id, 'order_ref': "Complete Pair", 'partner_id': new_sale_order.partner_id.id,
                                    'domain_rx': 'glasses'}
                    if len(a_lens) >= 1 or len(a_frame) >= 1 or len(a_lens_treatment) >= 1:
                        context['default_is_post_sale'] = True
                        if len(a_lens) >= 1:
                            context['default_is_lens'] = 1
                            context['default_lens_products'] = a_lens.account_move_line_id.sale_line_ids.product_id.id
                        if len(a_frame) >= 1:
                            context['default_is_frame'] = 1
                            context['default_frames_products_variants'] = a_frame.account_move_line_id.sale_line_ids.product_id.id
                        if len(a_lens_treatment) >= 1:
                            lens_treatment = [(5, 0, 0)]
                            lenstreatment_products_ids = [(5, 0, 0)]
                            for line in a_lens_treatment:
                                lenstreatment_products_ids.append((0, 0,
                                                                   {'lenstreatment_products_id': line.account_move_line_id.sale_line_ids.product_id.id,
                                                                    'return_location': line.return_location.id,
                                                                    'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                                lens_treatment.append((4, line.account_move_line_id.sale_line_ids.product_id.id))
                            context['default_lenstreatment_products'] = lens_treatment
                            context['default_lenstreatment_products_ids'] = lenstreatment_products_ids

                        # patients own frame (copy to new multi order)
                        context['default_model_number'] = lab_details_id.model_number
                        context['default_color_patient_frame'] = lab_details_id.color_patient_frame
                        context['default_a'] = lab_details_id.a
                        context['default_b'] = lab_details_id.b
                        context['default_dbl'] = lab_details_id.dbl
                        context['default_ed'] = lab_details_id.ed
                        context['default_bridge'] = lab_details_id.bridge
                        context['default_temple'] = lab_details_id.temple
                        context['default_edge_id'] = lab_details_id.edge_id
                        context['default_frame_id'] = lab_details_id.frame_id.id
                        # prescription (copy to new multi order)
                        context['default_prescription_id'] = lab_details_id.prescription_id.id
                        # lab details section (Measurements)(copy to new multi order)
                        context['default_dist_pd_lab_details'] = lab_details_id.dist_pd_lab_details
                        context['default_near_pd_lab_details'] = lab_details_id.near_pd_lab_details
                        context['default_oc_hit_lab_details'] = lab_details_id.oc_hit_lab_details
                        context['default_seg_ht_lab_details'] = lab_details_id.seg_ht_lab_details
                        context['default_bc_lab_details'] = lab_details_id.bc_lab_details
                        context['default_dist_pd_lab_details_os'] = lab_details_id.dist_pd_lab_details_os
                        context['default_near_pd_lab_details_os'] = lab_details_id.near_pd_lab_details_os
                        context['default_oc_hit_lab_details_os'] = lab_details_id.oc_hit_lab_details_os
                        context['default_seg_ht_lab_details_os'] = lab_details_id.seg_ht_lab_details_os
                        context['default_bc_lab_details_os'] = lab_details_id.bc_lab_details_os
                        context['default_panto_lab_details'] = lab_details_id.panto_lab_details
                        context['default_thickness_lab_details'] = lab_details_id.thickness_lab_details
                        context['default_wrap_lab_details'] = lab_details_id.wrap_lab_details
                        context['default_vertex_mlab_details'] = lab_details_id.vertex_mlab_details
                        # lab details section (Lens)(copy to new multi order)
                        context['default_eye_lab_details'] = lab_details_id.eye_lab_details
                        # lab details section (Lens Treatement)(copy to new multi order)
                        context['default_tint_color_lab_details'] = lab_details_id.tint_color_lab_details
                        context['default_tint_sample_lab_details'] = lab_details_id.tint_sample_lab_details
                        context['default_mirror_coating_lab_details'] = lab_details_id.mirror_coating_lab_details
                        context['default_by_lab_details'] = lab_details_id.by_lab_details
                        # lab details section (Frame)(copy to new multi order)
                        # context['default_frame_rel'] = lab_details_id.frame_rel
                        context['default_edge_type'] = lab_details_id.edge_type
                        context['default_frame_type'] = lab_details_id.frame_type.id
                        context['default_a_lab_details'] = lab_details_id.a_lab_details
                        context['default_b_lab_details'] = lab_details_id.b_lab_details
                        context['default_dbl_lab_details'] = lab_details_id.dbl_lab_details
                        context['default_ed_lab_details'] = lab_details_id.ed_lab_details
                        # lab details section (Lab Information)(copy to new multi order)
                        context['default_lab_details'] = lab_details_id.lab_details.id
                        context['default_physician_id'] = lab_details_id.physician_id.id
                        context['default_ship_to'] = lab_details_id.ship_to.id
                        context['new_size'] = 'max-width_1180px'

                        return {
                            'type': 'ir.actions.act_window',
                            'res_model': 'multi.order.type',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'target': 'new',
                            'context': context,
                        }
                return {
                    'name': _('Return Sale Order'),
                    'res_model': 'sale.order',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_id': new_sale_order.id,
                    'type': 'ir.actions.act_window',
                }
        elif self.type == "Remake":
            pstl_id = {x.account_move_line_id.lab_details_id.id: self.post_sale_lines_transactions_ids.filtered(
                        lambda y: y.check and y.return_qty > 0 and
                                  y.account_move_line_id.display_type != "line_section" and
                                  y.account_move_line_id.lab_details_id == x.account_move_line_id.lab_details_id)
                        for x in self.post_sale_lines_transactions_ids if x.account_move_line_id.display_type == "line_section"}
            pstl_id = [[k] + [line for line in v] for k, v in pstl_id.items() if len(v) > 0]
            pstl_id = [data[0] for data in pstl_id]
            post_sale_lines_transactions_ids = self.env["post.sale.transactions.lines"]
            for data in pstl_id:
                post_sale_lines_transactions_ids += self.post_sale_lines_transactions_ids.filtered(
                    lambda x: x.account_move_line_id.lab_details_id.id == data)

            # pstl_id = [item for sublist in pstl_id for item in sublist]
            current_sale_order = self.sale_order_id.copy_data()[0]
            current_sale_order['order_line'] = []
            current_sale_order['post_sale_type'] = 'Remake'
            new_sale_order = self.env['sale.order']\
                .with_context(post_sale_transactions_lines_ids=pstl_id,
                              default_post_sale_type= 'Remake',
                              default_post_sale_order_ref = self.sale_order_id.id)\
                .create(current_sale_order)

            if new_sale_order.id:
                # sale_order_line = [(5, 0, 0)]
                # # post_sale_transactions_lines_ids = pstl_id
                # for pstl_id in post_sale_lines_transactions_ids:
                #     name = "REMK " + pstl_id.name if pstl_id.display_type == 'line_section' else pstl_id.name
                #     current_sale_order_line = pstl_id.account_move_line_id.sale_line_ids.copy_data()[0]
                #     current_sale_order_line['post_sale_order_line_id'] = pstl_id.account_move_line_id.sale_line_ids.id
                #     if pstl_id.re_order:
                #         current_sale_order_line['return_location'] = pstl_id.return_location.id
                #     sale_order_line.append((0, 0, current_sale_order_line))
                lab_detail_ids = pstl_id
                for lab_detail_id in lab_detail_ids:
                    pstl_id = self.post_sale_lines_transactions_ids.filtered(lambda x: x.account_move_line_id.lab_details_id.id == lab_detail_id)
                    name = pstl_id.filtered(lambda x: x.display_type == "line_section").name
                    frame = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Frames')
                    lens = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens')
                    lens_treatments = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                    miscellaneouss = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Accessory')
                    services = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Services')
                    contact_lenses = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Contact Lens')
                    lab_details_id = pstl_id.account_move_line_id.lab_details_id
                    if "Complete Pair" in name:
                        context = {'so_id': new_sale_order.id,
                                   'order_ref': "Complete Pair",
                                   'partner_id': new_sale_order.partner_id.id,
                                   'domain_rx': 'glasses'}
                        values = {'post_sale_type': 'Remake'}
                    elif "Contact Lens" in name:
                        context = {'so_id': new_sale_order.id,
                                   'order_ref': "Contact Lens",
                                   'partner_id': new_sale_order.partner_id.id,
                                   'domain_rx': 'soft,hard'}
                        values = {'post_sale_type': 'Remake'}
                    elif "Lenses Only" in name:
                        context = {'so_id': new_sale_order.id,
                                   'order_ref': "Lenses Only",
                                   'partner_id': new_sale_order.partner_id.id,
                                   'domain_rx': 'glasses'}
                        values = {'post_sale_type': 'Remake'}
                    elif "Frame Only" in name:
                        context = {'so_id': new_sale_order.id,
                                   'order_ref': "Frame Only",
                                   'partner_id': new_sale_order.partner_id.id}
                        values = {'post_sale_type': 'Remake'}
                    elif "Services" in name:
                        context = {'so_id': new_sale_order.id,
                                   'order_ref': "Services",
                                   'partner_id': new_sale_order.partner_id.id}
                        values = {'post_sale_type': 'Remake'}
                    else:
                        context = {'so_id': new_sale_order.id,
                                   'order_ref': "Miscellaneous",
                                   'partner_id': new_sale_order.partner_id.id}
                        values = {'post_sale_type': 'Remake'}

                    values['is_post_sale'] = True
                    if len(frame) >= 1:
                        values['default_frames_products_variants'] = frame.account_move_line_id.sale_line_ids.product_id.id
                        values['default_frames_products_variants_return_location'] = frame.return_location.id
                        values['default_frames_products_variants_post_sale_order_line_id'] = frame.account_move_line_id.sale_line_ids.id
                    if len(lens) >= 1:
                        values['default_lens_products'] = lens.account_move_line_id.sale_line_ids.product_id.id
                        values['default_lens_products_return_location'] = lens.return_location.id
                        values['default_lens_products_post_sale_order_line_id'] = lens.account_move_line_id.sale_line_ids.id
                    if len(lens_treatments) >= 1:
                        lens_treatment = [(5, 0, 0)]
                        lenstreatment_products_ids = [(5, 0, 0)]
                        for line in lens_treatments:
                            lens_treatment.append((4, line.account_move_line_id.sale_line_ids.product_id.id))
                            lenstreatment_products_ids.append((0, 0,
                                                                  {'lenstreatment_products_id': line.account_move_line_id.sale_line_ids.product_id.id,
                                                                   'return_location': line.return_location.id,
                                                                   'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                        values['default_lenstreatment_products'] = lens_treatment
                        values['default_lenstreatment_products_ids'] = lenstreatment_products_ids
                    if len(miscellaneouss) >= 1:
                        miscellaneous = [(5, 0, 0)]
                        for line in miscellaneouss:
                            miscellaneous.append((0, 0, {'miscellaneous_products': line.account_move_line_id.sale_line_ids.product_id.id,
                                                         'qty': line.return_qty if line.return_location.id else -line.return_qty,
                                                         'return_location': line.return_location.id,
                                                         'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                        values['default_miscellaneous_products'] = miscellaneous
                    if len(services) >= 1:
                        service = [(5, 0, 0)]
                        for line in services:
                            service.append((0, 0, {'service_products': line.account_move_line_id.sale_line_ids.product_id.id,
                                                   'qty': line.return_qty if line.return_location.id else -line.return_qty,
                                                   'return_location': line.return_location.id,
                                                   'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                        values['default_service_products'] = service
                    if len(contact_lenses) == 1:
                        post_sale_lines_transactions_ids = self.post_sale_lines_transactions_ids.filtered(lambda x: x.account_move_line_id.lab_details_id.id == lab_details_id.id and x.display_type != "line_section")
                        if post_sale_lines_transactions_ids[0].id == contact_lenses.id:
                            values['default_contact_lens_products_od'] = contact_lenses.account_move_line_id.sale_line_ids.product_id.id
                            values['default_contact_lens_products_od_return_location'] = contact_lenses.return_location.id
                            values['default_contact_lens_products_od_post_sale_order_line_id'] = contact_lenses.account_move_line_id.sale_line_ids.id
                            values['default_od_qty'] = contact_lenses.return_qty
                        else:
                            values['default_contact_lens_products_os'] = contact_lenses.account_move_line_id.sale_line_ids.product_id.id
                            values['default_contact_lens_products_os_return_location'] = contact_lenses.return_location.id
                            values['default_contact_lens_products_os_post_sale_order_line_id'] = contact_lenses.account_move_line_id.sale_line_ids.id
                            values['default_os_qty'] = contact_lenses.return_qty
                    elif len(contact_lenses) > 1:
                        values['default_contact_lens_products_od'] = contact_lenses[0].account_move_line_id.sale_line_ids.product_id.id
                        values['default_contact_lens_products_od_return_location'] = contact_lenses[0].return_location.id
                        values['default_contact_lens_products_od_post_sale_order_line_id'] = contact_lenses[0].account_move_line_id.sale_line_ids.id
                        values['default_od_qty'] = contact_lenses[0].return_qty
                        values['default_contact_lens_products_os'] = contact_lenses[1].account_move_line_id.sale_line_ids.product_id.id
                        values['default_contact_lens_products_os_return_location'] = contact_lenses[1].return_location.id
                        values['default_contact_lens_products_os_post_sale_order_line_id'] = contact_lenses[1].account_move_line_id.sale_line_ids.id
                        values['default_os_qty'] = contact_lenses[1].return_qty
                    # patients own frame (copy to new multi order)
                    values['default_model_number'] = lab_details_id.model_number
                    values['default_color_patient_frame'] = lab_details_id.color_patient_frame
                    values['default_a'] = lab_details_id.a
                    values['default_b'] = lab_details_id.b
                    values['default_dbl'] = lab_details_id.dbl
                    values['default_ed'] = lab_details_id.ed
                    values['default_bridge'] = lab_details_id.bridge
                    values['default_temple'] = lab_details_id.temple
                    values['default_edge_id'] = lab_details_id.edge_id
                    values['default_frame_id'] = lab_details_id.frame_id.id
                    # prescription (copy to new multi order)
                    values['default_prescription_id'] = lab_details_id.prescription_id.id
                    # lab details section (Measurements)(copy to new multi order)
                    values['default_dist_pd_lab_details'] = lab_details_id.dist_pd_lab_details
                    values['default_near_pd_lab_details'] = lab_details_id.near_pd_lab_details
                    values['default_oc_hit_lab_details'] = lab_details_id.oc_hit_lab_details
                    values['default_seg_ht_lab_details'] = lab_details_id.seg_ht_lab_details
                    values['default_bc_lab_details'] = lab_details_id.bc_lab_details
                    values['default_dist_pd_lab_details_os'] = lab_details_id.dist_pd_lab_details_os
                    values['default_near_pd_lab_details_os'] = lab_details_id.near_pd_lab_details_os
                    values['default_oc_hit_lab_details_os'] = lab_details_id.oc_hit_lab_details_os
                    values['default_seg_ht_lab_details_os'] = lab_details_id.seg_ht_lab_details_os
                    values['default_bc_lab_details_os'] = lab_details_id.bc_lab_details_os
                    values['default_panto_lab_details'] = lab_details_id.panto_lab_details
                    values['default_thickness_lab_details'] = lab_details_id.thickness_lab_details
                    values['default_wrap_lab_details'] = lab_details_id.wrap_lab_details
                    values['default_vertex_mlab_details'] = lab_details_id.vertex_mlab_details
                    # lab details section (Lens)(copy to new multi order)
                    values['default_eye_lab_details'] = lab_details_id.eye_lab_details
                    # lab details section (Lens Treatement)(copy to new multi order)
                    values['default_tint_color_lab_details'] = lab_details_id.tint_color_lab_details
                    values['default_tint_sample_lab_details'] = lab_details_id.tint_sample_lab_details
                    values['default_mirror_coating_lab_details'] = lab_details_id.mirror_coating_lab_details
                    values['default_by_lab_details'] = lab_details_id.by_lab_details
                    # lab details section (Frame)(copy to new multi order)
                    # context['frame_rel'] = lab_details_id.frame_rel
                    values['default_edge_type'] = lab_details_id.edge_type
                    values['default_frame_type'] = lab_details_id.frame_type.id
                    values['default_a_lab_details'] = lab_details_id.a_lab_details
                    values['default_b_lab_details'] = lab_details_id.b_lab_details
                    values['default_dbl_lab_details'] = lab_details_id.dbl_lab_details
                    values['default_ed_lab_details'] = lab_details_id.ed_lab_details
                    # lab details section (Lab Information)(copy to new multi order)
                    values['default_lab_details'] = lab_details_id.lab_details.id
                    values['default_physician_id'] = lab_details_id.physician_id.id
                    values['default_ship_to'] = lab_details_id.ship_to.id

                    multi_order_type = self.env['multi.order.type'].with_context(context).create(values)
                    multi_order_type.hcpcs_frame_onchange();
                    multi_order_type.create_lines();

                new_sale_order.update({
                    'name': "REMK " + new_sale_order.name,
                    'post_sale_order_ref': self.sale_order_id.id,
                    # 'order_line': sale_order_line,
                    'post_sale_reasons_id': self.post_sale_reasons_id.id,
                })
                return {
                    'name': _('Remake Sale Order'),
                    'res_model': 'sale.order',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_id': new_sale_order.id,
                    'type': 'ir.actions.act_window',
                }
        elif self.type == "Warranty":
            pstl_id = {x: self.post_sale_lines_transactions_ids.filtered(
                        lambda y: y.check and y.return_qty > 0 and
                                  y.account_move_line_id.display_type != "line_section" and
                                  y.account_move_line_id.lab_details_id == x.account_move_line_id.lab_details_id)
                        for x in self.post_sale_lines_transactions_ids if x.account_move_line_id.display_type == "line_section"}
            pstl_id = [[k] + [line for line in v] for k, v in pstl_id.items() if len(v) > 0]
            pstl_id = [item for sublist in pstl_id for item in sublist]
            if len({x.account_move_line_id.lab_details_id.id for x in self.env['post.sale.transactions.lines'].search([('id', 'in', [x.id for x in pstl_id])])}) > 1:
                raise exceptions.ValidationError("Only 1 order type can be selected for warranty")

            current_sale_order = self.sale_order_id.copy_data()[0]
            current_sale_order['order_line'] = []
            current_sale_order['post_sale_type'] = 'Warranty'
            new_sale_order = self.env['sale.order']\
                .with_context(post_sale_transactions_lines_ids=pstl_id,
                              default_post_sale_type= 'Warranty',
                              default_post_sale_order_ref = self.sale_order_id.id)\
                .create(current_sale_order)

            if new_sale_order.id:
                sale_order_line = [(5, 0, 0)]
                # post_sale_transactions_lines_ids = pstl_id
                # for pstl_id in post_sale_transactions_lines_ids:
                #     name = "WTY " + pstl_id.name if pstl_id.display_type == 'line_section' else pstl_id.name
                #     current_sale_order_line = pstl_id.account_move_line_id.sale_line_ids.copy_data()[0]
                #     current_sale_order_line['product_uom_qty'] = pstl_id.return_qty * -1
                #     current_sale_order_line['name'] = name
                #     sale_order_line.append((0, 0, current_sale_order_line))

                new_sale_order.update({
                    'name': "WTY " + new_sale_order.name,
                    'post_sale_order_ref': self.sale_order_id.id,
                    'order_line': sale_order_line,
                    'post_sale_reasons_id': self.post_sale_reasons_id.id,
                })
                pstl_id = self.env['post.sale.transactions.lines'].search([('id', 'in', [x.id for x in pstl_id])])
                name = pstl_id.filtered(lambda x: x.display_type == "line_section").name

                frame = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Frames')
                lens = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens')
                lens_treatments = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Lens Treatment')
                miscellaneouss = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Accessory')
                services = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Services')
                contact_lenses = pstl_id.filtered(lambda x: x.account_move_line_id.product_id.product_tmpl_id.categ_id.name == 'Contact Lens')
                lab_details_id = pstl_id.account_move_line_id.lab_details_id
                if "Complete Pair" in name:
                    context = {'so_id': new_sale_order.id,
                               'order_ref': "Complete Pair",
                               'default_post_sale_type': 'Warranty',
                               'partner_id': new_sale_order.partner_id.id,
                               'domain_rx': 'glasses'}
                elif "Contact Lens" in name:
                    context = {'so_id': new_sale_order.id,
                               'order_ref': "Contact Lens",
                               'default_post_sale_type': 'Warranty',
                               'partner_id': new_sale_order.partner_id.id,
                               'domain_rx': 'soft,hard'}
                elif "Lenses Only" in name:
                    context = {'so_id': new_sale_order.id,
                               'order_ref': "Lenses Only",
                               'default_post_sale_type': 'Warranty',
                               'partner_id': new_sale_order.partner_id.id,
                               'domain_rx': 'glasses'}
                elif "Frame Only" in name:
                    context = {'so_id': new_sale_order.id,
                               'order_ref': "Frame Only",
                               'default_post_sale_type': 'Warranty',
                               'partner_id': new_sale_order.partner_id.id}
                elif "Services" in name:
                    context = {'so_id': new_sale_order.id,
                               'order_ref': "Services",
                               'default_post_sale_type': 'Warranty',
                               'partner_id': new_sale_order.partner_id.id}
                else:
                    context = {'so_id': new_sale_order.id,
                               'order_ref': "Miscellaneous",
                               'default_post_sale_type': 'Warranty',
                               'partner_id': new_sale_order.partner_id.id}
                context['default_is_post_sale'] = True
                if len(frame) >= 1:
                    context['default_frames_products_variants'] = frame.account_move_line_id.sale_line_ids.product_id.id
                    context['default_frames_products_variants_return_location'] = frame.return_location.id
                    context['default_frames_products_variants_post_sale_order_line_id'] = frame.account_move_line_id.sale_line_ids.id
                    context['frames_products_variants'] = 1
                if len(lens) >= 1:
                    context['default_lens_products'] = lens.account_move_line_id.sale_line_ids.product_id.id
                    context['default_lens_products_return_location'] = lens.return_location.id
                    context['default_lens_products_post_sale_order_line_id'] = lens.account_move_line_id.sale_line_ids.id
                    context['lens_products'] = 1
                if len(lens_treatments) >= 1:
                    lens_treatment = [(5, 0, 0)]
                    lenstreatment_products_ids = [(5, 0, 0)]
                    return_location = {}
                    for line in lens_treatments:
                        lens_treatment.append((4, line.account_move_line_id.sale_line_ids.product_id.id))
                        lenstreatment_products_ids.append((0, 0,
                                                              {'lenstreatment_products_id': line.account_move_line_id.sale_line_ids.product_id.id,
                                                               'return_location': line.return_location.id,
                                                               'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                    context['default_lenstreatment_products'] = lens_treatment
                    context['default_lenstreatment_products_ids'] = lenstreatment_products_ids
                    context['lenstreatment_products_return_location'] = return_location
                if len(miscellaneouss) >= 1:
                    miscellaneous = [(5, 0, 0)]
                    for line in miscellaneouss:
                        miscellaneous.append((0, 0, {'miscellaneous_products': line.account_move_line_id.sale_line_ids.product_id.id,
                                                     'qty': line.return_qty,
                                                     'return_location': line.return_location.id,
                                                     'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                    context['default_miscellaneous_products'] = miscellaneous
                if len(services) >= 1:
                    service = [(5, 0, 0)]
                    for line in services:
                        service.append((0, 0, {'service_products': line.account_move_line_id.sale_line_ids.product_id.id,
                                               'qty': line.return_qty,
                                               'return_location': line.return_location.id,
                                               'sale_order_line_id': line.account_move_line_id.sale_line_ids.id}))
                    context['default_service_products'] = service
                if len(contact_lenses) == 1:
                    post_sale_lines_transactions_ids = self.post_sale_lines_transactions_ids.filtered(lambda x: x.account_move_line_id.lab_details_id.id == lab_details_id.id and x.display_type != "line_section")
                    if post_sale_lines_transactions_ids[0].id == contact_lenses.id:
                        context['default_contact_lens_products_od'] = contact_lenses.account_move_line_id.sale_line_ids.product_id.id
                        context['default_contact_lens_products_od_return_location'] = contact_lenses.return_location.id
                        context['default_contact_lens_products_od_post_sale_order_line_id'] = contact_lenses.account_move_line_id.sale_line_ids.id
                        context['contact_lens_products_od'] = 1
                        context['default_od_qty'] = contact_lenses.account_move_line_id.sale_line_ids.product_uom_qty
                    else:
                        context['default_contact_lens_products_os'] = contact_lenses.account_move_line_id.sale_line_ids.product_id.id
                        context['default_contact_lens_products_os_return_location'] = contact_lenses.return_location.id
                        context['default_contact_lens_products_os_post_sale_order_line_id'] = contact_lenses.account_move_line_id.sale_line_ids.id
                        context['contact_lens_products_os'] = 1
                        context['default_os_qty'] = contact_lenses.account_move_line_id.sale_line_ids.product_uom_qty
                elif len(contact_lenses) > 1:
                    context['default_contact_lens_products_od'] = contact_lenses[0].account_move_line_id.sale_line_ids.product_id.id
                    context['default_contact_lens_products_od_return_location'] = contact_lenses[0].return_location.id
                    context['default_contact_lens_products_od_post_sale_order_line_id'] = contact_lenses[0].account_move_line_id.sale_line_ids.id
                    context['contact_lens_products_od'] = 1
                    context['default_od_qty'] = contact_lenses[0].account_move_line_id.sale_line_ids.product_uom_qty
                    context['default_contact_lens_products_os'] = contact_lenses[1].account_move_line_id.sale_line_ids.product_id.id
                    context['default_contact_lens_products_os_return_location'] = contact_lenses[1].return_location.id
                    context['default_contact_lens_products_os_post_sale_order_line_id'] = contact_lenses[1].account_move_line_id.sale_line_ids.id
                    context['contact_lens_products_os'] = 1
                    context['default_os_qty'] = contact_lenses[1].account_move_line_id.sale_line_ids.product_uom_qty
                # patients own frame (copy to new multi order)
                context['default_model_number'] = lab_details_id.model_number
                context['default_color_patient_frame'] = lab_details_id.color_patient_frame
                context['default_a'] = lab_details_id.a
                context['default_b'] = lab_details_id.b
                context['default_dbl'] = lab_details_id.dbl
                context['default_ed'] = lab_details_id.ed
                context['default_bridge'] = lab_details_id.bridge
                context['default_temple'] = lab_details_id.temple
                context['default_edge_id'] = lab_details_id.edge_id
                context['default_frame_id'] = lab_details_id.frame_id.id
                # prescription (copy to new multi order)
                context['default_prescription_id'] = lab_details_id.prescription_id.id
                # lab details section (Measurements)(copy to new multi order)
                context['default_dist_pd_lab_details'] = lab_details_id.dist_pd_lab_details
                context['default_near_pd_lab_details'] = lab_details_id.near_pd_lab_details
                context['default_oc_hit_lab_details'] = lab_details_id.oc_hit_lab_details
                context['default_seg_ht_lab_details'] = lab_details_id.seg_ht_lab_details
                context['default_bc_lab_details'] = lab_details_id.bc_lab_details
                context['default_dist_pd_lab_details_os'] = lab_details_id.dist_pd_lab_details_os
                context['default_near_pd_lab_details_os'] = lab_details_id.near_pd_lab_details_os
                context['default_oc_hit_lab_details_os'] = lab_details_id.oc_hit_lab_details_os
                context['default_seg_ht_lab_details_os'] = lab_details_id.seg_ht_lab_details_os
                context['default_bc_lab_details_os'] = lab_details_id.bc_lab_details_os
                context['default_panto_lab_details'] = lab_details_id.panto_lab_details
                context['default_thickness_lab_details'] = lab_details_id.thickness_lab_details
                context['default_wrap_lab_details'] = lab_details_id.wrap_lab_details
                context['default_vertex_mlab_details'] = lab_details_id.vertex_mlab_details
                # lab details section (Lens)(copy to new multi order)
                context['default_eye_lab_details'] = lab_details_id.eye_lab_details
                # lab details section (Lens Treatement)(copy to new multi order)
                context['default_tint_color_lab_details'] = lab_details_id.tint_color_lab_details
                context['default_tint_sample_lab_details'] = lab_details_id.tint_sample_lab_details
                context['default_mirror_coating_lab_details'] = lab_details_id.mirror_coating_lab_details
                context['default_by_lab_details'] = lab_details_id.by_lab_details
                # lab details section (Frame)(copy to new multi order)
                # context['default_frame_rel'] = lab_details_id.frame_rel
                context['default_edge_type'] = lab_details_id.edge_type
                context['default_frame_type'] = lab_details_id.frame_type.id
                context['default_a_lab_details'] = lab_details_id.a_lab_details
                context['default_b_lab_details'] = lab_details_id.b_lab_details
                context['default_dbl_lab_details'] = lab_details_id.dbl_lab_details
                context['default_ed_lab_details'] = lab_details_id.ed_lab_details
                # lab details section (Lab Information)(copy to new multi order)
                context['default_lab_details'] = lab_details_id.lab_details.id
                context['default_physician_id'] = lab_details_id.physician_id.id
                context['default_ship_to'] = lab_details_id.ship_to.id
                context['new_size'] = 'max-width_1180px'

                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'multi.order.type',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': context,
                }

    def delivery_move(self):
        if self.type == 'Remake':
            post_sale_lines_transactions_ids = self.post_sale_lines_transactions_ids
            delivery_order_lines = [x for x in post_sale_lines_transactions_ids if x.check and x.return_qty > 0 and
                                        x.account_move_line_id.display_type != "line_section"]
            done_picking_ids = self.stock_picking_ids.filtered(lambda x: x.state == 'done')
            not_done_picking_ids = self.stock_picking_ids.filtered(lambda x: x.state != 'done')

            for pslt_id in post_sale_lines_transactions_ids:
                uom_qty = pslt_id.uom_qty / pslt_id.account_move_line_id.quantity if pslt_id.uom_qty and pslt_id.account_move_line_id.quantity else 0
                picking_id = self.stock_picking_ids.move_lines.filtered(lambda x: x.product_id.id == pslt_id.product_id.id and
                                                                     x.product_qty >= (pslt_id.qty * uom_qty)).picking_id.id
                stock_scrap = self.env['stock.scrap'].create({
                    'picking_id': picking_id,
                    'product_id': pslt_id.product_id.id,
                    'product_uom_id': pslt_id.product_id.uom_id.id,
                    'company_id': pslt_id.company_id.id,
                    'scrap_qty': pslt_id.return_qty,
                    'scrap_location_id': pslt_id.return_location.id,
                })
                # stock_scrap._get_default_location_id()
                stock_scrap.action_validate()
        else:
            post_sale_lines_transactions_ids = self.post_sale_lines_transactions_ids
            delivery_order_lines = {x.return_location.id: post_sale_lines_transactions_ids.filtered(
                lambda y: y.check and y.return_qty > 0 and
                          y.account_move_line_id.display_type != "line_section" and
                          y.return_location == x.return_location )
                for x in post_sale_lines_transactions_ids if not x.return_location.scrap_location}
            delivery_order_lines = {k: v for k, v in delivery_order_lines.items() if len(v)}

            done_picking_ids = self.stock_picking_ids.filtered(lambda x: x.state == 'done')
            not_done_picking_ids = self.stock_picking_ids.filtered(lambda x: x.state != 'done')

            for pslt_id in post_sale_lines_transactions_ids.filtered(lambda x: x.return_location.scrap_location):
                uom_qty = pslt_id.uom_qty / pslt_id.account_move_line_id.quantity if pslt_id.uom_qty and pslt_id.account_move_line_id.quantity else 0
                picking_id = self.stock_picking_ids.move_lines.filtered(
                    lambda x: x.product_id.id == pslt_id.product_id.id and
                              x.product_qty >= (pslt_id.qty * uom_qty)).picking_id.id
                stock_scrap = self.env['stock.scrap'].create({
                    'picking_id': picking_id,
                    'product_id': pslt_id.product_id.id,
                    'product_uom_id': pslt_id.product_id.uom_id.id,
                    'company_id': pslt_id.company_id.id,
                    'scrap_qty': pslt_id.return_qty,
                    'scrap_location_id': pslt_id.return_location.id,
                })
                stock_scrap.action_validate()

            for done_picking_id in done_picking_ids:
                for delivery_order_line in delivery_order_lines:
                    reverse_delivery = self.env['stock.return.picking'] \
                        .with_context(post_sale_orderlines=delivery_order_lines[delivery_order_line]).create({
                        'picking_id': done_picking_id.id,
                        'location_id': delivery_order_line,
                    })
                    return_post_sale_orderlines = reverse_delivery._post_sale_onchange_picking_id()
                    if len(return_post_sale_orderlines) > 0:
                        post_sale_lines_transactions_ids = post_sale_lines_transactions_ids.filtered(
                            lambda x: x.id not in return_post_sale_orderlines.ids)
                        delivery_order_lines = {x.return_location.id: post_sale_lines_transactions_ids.filtered(
                            lambda y: y.check and y.return_qty > 0 and
                                      y.account_move_line_id.display_type != "line_section" and
                                      y.return_location == x.return_location)
                            for x in post_sale_lines_transactions_ids}
                        delivery_order_lines = {k: v for k, v in delivery_order_lines.items() if len(v)}
                        res_id = reverse_delivery.create_returns()['res_id']
                        stock_picking_id = self.env['stock.picking'].search([('id', '=', res_id)])
                        stock_picking_id.update({
                            'post_sale_order_ref': self.sale_order_id.id,
                            'post_sale_type': self.type,
                        })
                        # wiz_act = stock_picking_id.button_validate()
                        # wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
                        # wiz.process()
                    else:
                        reverse_delivery.unlink()

            for not_done_picking_ids in not_done_picking_ids:
                delivery_order_lines = [y for y in post_sale_lines_transactions_ids if y.check and y.return_qty > 0 and
                                        y.account_move_line_id.display_type != "line_section"]
                move_id = []
                return_post_sale_orderlines = self.env['post.sale.transactions.lines']
                for delivery_order_line in delivery_order_lines:
                    uom_qty = delivery_order_line.uom_qty / delivery_order_line.account_move_line_id.quantity if delivery_order_line.uom_qty and delivery_order_line.account_move_line_id.quantity else 0
                    for line in not_done_picking_ids.move_ids_without_package:
                        if line.product_id.id == delivery_order_line.product_id.id and line.id not in move_id \
                                and line.product_qty >= (delivery_order_line.qty * uom_qty) and \
                                (line.quantity_done == 0 or
                                 line.quantity_done >= (delivery_order_line.qty * uom_qty)):
                            return_post_sale_orderlines += delivery_order_line
                            line.product_uom_qty -= (delivery_order_line.return_qty * uom_qty)
                            if line.quantity_done > 0:
                                line.quantity_done -= (delivery_order_line.return_qty * uom_qty)
                            if line.reserved_availability > 0:
                                if line.reserved_availability >= (
                                        delivery_order_line.return_qty * uom_qty):
                                    line.reserved_availability -= (
                                                delivery_order_line.return_qty * uom_qty)
                                elif (
                                        delivery_order_line.return_qty * uom_qty) > line.reserved_availability > line.quantity_done:
                                    line.reserved_availability = line.quantity_done
                            move_id.append(line.id)

                if len(return_post_sale_orderlines) > 0:
                    post_sale_lines_transactions_ids = post_sale_lines_transactions_ids.filtered(
                        lambda x: x.id not in return_post_sale_orderlines.ids)


class PostSaleTransactionsLines(models.TransientModel):
    _name = 'post.sale.transactions.lines'
    _description = 'post sale transactions lines'

    processed_in_post_sale = fields.Boolean(string="post sale", default=False)
    post_sale_transactions_id = fields.Many2one('post.sale.transactions')
    type = fields.Selection([('Return', 'Return'), ('Remake', 'Remake'),
                             ('Exchange', 'Exchange'), ('Warranty', 'Warranty'),
                             ], related="post_sale_transactions_id.type")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    re_order = fields.Boolean(string="Re-order", default=False)
    name = fields.Char(string='Label', readonly=True)
    account_move_line_id = fields.Many2one('account.move.line', readonly=True)
    check = fields.Boolean(string="Return", default=False)
    product_id = fields.Many2one('product.product', readonly=True)
    qty = fields.Float(string="Qty", readonly=True)
    uom_qty = fields.Float(string="UOM Qty", readonly=True)
    return_qty = fields.Integer(string="Return Qty", default=0)
    return_location = fields.Many2one('stock.location', string="Return Location",
                                      domain="['|', '&', ('scrap_location', '=', True), \
                                               ('company_id', 'in', [False, company_id]), \
                                               '|', ('id', '=', original_location_id), \
                                               '|', '&', ('return_location', '=', True), ('company_id', '=', False), \
                                               '&', ('return_location', '=', True), \
                                               ('company_id', '=', company_id), \
                                               ]")
                                      # domain="['|', ('id', '=', original_location_id), '|', '&', "
                                      #        "('return_location', '=', True), ('company_id', '=', False),"
                                      #        "'&', ('return_location', '=', True), ('company_id', '=', company_id)]")
                                      # domain="["
                                      #        "('scrap_location', '=', True), ('company_id', 'in', [False,company_id]),"
                                      #        "]")
    original_location_id = fields.Many2one('stock.location')
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.")

    @api.onchange('return_qty')
    def onchange_return_qty(self):
        if self.return_qty > self.qty:
            self.return_qty = 0
            raise exceptions.ValidationError("Return Quantity can't be grater then actual quantity")
        elif self.return_qty < 0:
            self.return_qty = 0
            raise exceptions.ValidationError("Return Quantity can't be negative")

    @api.onchange('re_order', 'check')
    def onchange_re_order(self):
        return {
            'domain': {'return_location': ['|', '&', ('scrap_location', '=', True),
                                           ('company_id', 'in', [False, self.company_id.id]),
                                           '|', ('id', '=', self.original_location_id.id),
                                           '|', '&', ('return_location', '=', True), ('company_id', '=', False),
                                           '&', ('return_location', '=', True),
                                           ('company_id', '=', self.company_id.id),
                                           ]},
        }
