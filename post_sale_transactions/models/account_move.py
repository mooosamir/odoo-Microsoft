# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'post sale transactions'

    sale_order_session_id = fields.Many2one('sale.order.session', readonly=True, copy=False)

    @api.model
    def create(self, values):
        open_session = self.env['sale.order.session'].search([("state", 'in', ['in_progress'])])
        res = super(AccountMove, self).create(values)
        if open_session.id and not res.sale_order_session_id.id:
            res.sale_order_session_id = open_session.id
        return res

    def action_invoice_register_payment(self):
        # return self.env['account.payment']\
        #     .with_context(default_so_balance=self.amount_residual, default_from_sale_order=True,
        #                   active_ids=self.ids, active_model='account.move', active_id=self.id)\
        #     .action_register_payment()

        # inv = self.id
        # return self.env['account.payment'].with_context(default_so_balance=self.amount_residual,
        #                                                 default_from_sale_order=True,
        #                                                 active_ids=self.ids,
        #                                                 active_model='account.move',
        #                                                 active_id=self.id,
        #                                                 rec_id=self.id).action_register_payment()

        context = self.env.context.copy()
        if 'default_type' in context:
            del(context['default_type'])
        context['invoice_id'] = self.id
        return {
            'name': _('Register Payment'),
            'res_model': 'multi.invoice.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.multi_invoice_payment_form').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _post_sale_reverse_move_vals(self, default_values, post_sale_orderlines=None,  cancel=True):
        ''' Reverse values passed as parameter being the copied values of the original journal entry.
        For example, debit / credit must be switched. The tax lines must be edited in case of refunds.

        :param default_values:  A copy_date of the original journal entry.
        :param cancel:          A flag indicating the reverse is made to cancel the original journal entry.
        :return:                The updated default_values.
        '''
        self.ensure_one()

        def compute_tax_repartition_lines_mapping(move_vals):
            ''' Computes and returns a mapping between the current repartition lines to the new expected one.
            :param move_vals:   The newly created invoice as a python dictionary to be passed to the 'create' method.
            :return:            A map invoice_repartition_line => refund_repartition_line.
            '''
            # invoice_repartition_line => refund_repartition_line
            mapping = {}

            # Do nothing if the move is not a credit note.
            if move_vals['type'] not in ('out_refund', 'in_refund'):
                return mapping

            for line_command in move_vals.get('line_ids', []):
                line_vals = line_command[2]  # (0, 0, {...})

                if line_vals.get('tax_line_id'):
                    # Tax line.
                    tax_ids = [line_vals['tax_line_id']]
                elif line_vals.get('tax_ids') and line_vals['tax_ids'][0][2]:
                    # Base line.
                    tax_ids = line_vals['tax_ids'][0][2]
                else:
                    continue

                for tax in self.env['account.tax'].browse(tax_ids).flatten_taxes_hierarchy():
                    for inv_rep_line, ref_rep_line in zip(tax.invoice_repartition_line_ids, tax.refund_repartition_line_ids):
                        mapping[inv_rep_line] = ref_rep_line
            return mapping

        move_vals = self.with_context(include_business_fields=True).copy_data(default=default_values)[0]

        tax_repartition_lines_mapping = compute_tax_repartition_lines_mapping(move_vals)

        line_ids = []
        for line_id in move_vals.get('line_ids', []):
            if line_id[2]['lab_details_id'] in post_sale_orderlines:
                if line_id[2]["display_type"] == "line_section":
                    line_ids.append(line_id)
                for post_sale_orderline in post_sale_orderlines[line_id[2]['lab_details_id']]:
                    if post_sale_orderline.account_move_line_id.sale_line_ids.ids == line_id[2]["sale_line_ids"][0][2] and "Promotion~" in post_sale_orderline.name:
                        line_id[2]["quantity"] = post_sale_orderline.qty
                        line_id[2]["price_unit"] = float(post_sale_orderline.name.split("~")[1])
                        line_id[2]["pt_resp"] = float(post_sale_orderline.name.split("~")[1])
                        line_id[2]["price_total"] = float(post_sale_orderline.name.split("~")[1])
                        line_id[2]["price_subtotal"] = float(post_sale_orderline.name.split("~")[1])
                        line_id[2]["credit"] = 0
                        line_id[2]["debit"] = 0
                        line_ids.append(line_id)
                    elif post_sale_orderline.account_move_line_id.sale_line_ids.ids == line_id[2]["sale_line_ids"][0][2]:
                        price_total = line_id[2]['price_total']
                        price_subtotal = line_id[2]['price_subtotal']
                        # credit = line_id[2]['credit']
                        quantity = line_id[2]['quantity']
                        line_id[2]["quantity"] = post_sale_orderline.return_qty
                        line_id[2]["price_total"] = line_id[2]['price_total']/quantity * post_sale_orderline.return_qty
                        line_id[2]["price_subtotal"] = line_id[2]['price_subtotal']/quantity * post_sale_orderline.return_qty
                        line_id[2]["credit"] = 0
                        line_id[2]["debit"] = 0
                        line_ids.append(line_id)
        if 'line_ids' in move_vals:
            move_vals['line_ids'] = line_ids

        for line_command in move_vals.get('line_ids', []):
            line_vals = line_command[2]  # (0, 0, {...})

            # ==== Inverse debit / credit / amount_currency ====
            amount_currency = -line_vals.get('amount_currency', 0.0)
            balance = line_vals['credit'] - line_vals['debit']

            line_vals.update({
                'amount_currency': amount_currency,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
            })

            if move_vals['type'] not in ('out_refund', 'in_refund'):
                continue

            # ==== Map tax repartition lines ====
            if line_vals.get('tax_repartition_line_id'):
                # Tax line.
                invoice_repartition_line = self.env['account.tax.repartition.line'].browse \
                    (line_vals['tax_repartition_line_id'])
                if invoice_repartition_line not in tax_repartition_lines_mapping:
                    raise UserError \
                        (_("It seems that the taxes have been modified since the creation of the journal entry. You should create the credit note manually instead."))
                refund_repartition_line = tax_repartition_lines_mapping[invoice_repartition_line]

                # Find the right account.
                account_id = self.env['account.move.line']._get_default_tax_account(refund_repartition_line).id
                if not account_id:
                    if not invoice_repartition_line.account_id:
                        # Keep the current account as the current one comes from the base line.
                        account_id = line_vals['account_id']
                    else:
                        tax = invoice_repartition_line.invoice_tax_id
                        base_line = self.line_ids.filtered(lambda line: tax in line.tax_ids.flatten_taxes_hierarchy())[0]
                        account_id = base_line.account_id.id

                line_vals.update({
                    'tax_repartition_line_id': refund_repartition_line.id,
                    'account_id': account_id,
                    'tag_ids': [(6, 0, refund_repartition_line.tag_ids.ids)],
                })
            elif line_vals.get('tax_ids') and line_vals['tax_ids'][0][2]:
                # Base line.
                taxes = self.env['account.tax'].browse(line_vals['tax_ids'][0][2]).flatten_taxes_hierarchy()
                invoice_repartition_lines = taxes \
                    .mapped('invoice_repartition_line_ids') \
                    .filtered(lambda line: line.repartition_type == 'base')
                refund_repartition_lines = invoice_repartition_lines \
                    .mapped(lambda line: tax_repartition_lines_mapping[line])

                line_vals['tag_ids'] = [(6, 0, refund_repartition_lines.mapped('tag_ids').ids)]

        if not cancel:
            move_vals['line_ids'] = [vals for vals in move_vals['line_ids'] if not vals[2]['is_anglo_saxon_line']]
        return move_vals

    def _post_sale_reverse_moves(self, default_values_list=None, post_sale_orderlines= None, cancel=False):
        # OVERRIDE
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'campaign_id': move.campaign_id.id,
                'medium_id': move.medium_id.id,
                'source_id': move.source_id.id,
            })

        ''' Reverse a recordset of account.move.
        If cancel parameter is true, the reconcilable or liquidity lines
        of each original move will be reconciled with its reverse's.

        :param default_values_list: A list of default values to consider per move.
                                    ('type' & 'reversed_entry_id' are computed in the method).
        :return:                    An account.move recordset, reverse of the current self.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
        }

        move_vals_list = []
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'type': reverse_type_map[move.type],
                'reversed_entry_id': move.id,
            })
            move_vals_list.append(move.with_context(move_reverse_cancel=cancel)._post_sale_reverse_move_vals(default_values, post_sale_orderlines=post_sale_orderlines, cancel=cancel))

        reverse_moves = self.env['account.move'].with_context(check_move_validity=False).create(move_vals_list)
        for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False)):
            # Update amount_currency if the date has changed.
            if move.date != reverse_move.date:
                for line in reverse_move.line_ids:
                    if line.currency_id:
                        line._onchange_currency()
            reverse_move._recompute_dynamic_lines(recompute_all_taxes=True)
        reverse_moves._check_balanced()

        # Reconcile moves together to cancel the previous one.
        if cancel:
            reverse_moves.with_context(move_reverse_cancel=cancel).post()
            for move, reverse_move in zip(self, reverse_moves):
                accounts = move.mapped('line_ids.account_id') \
                    .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
                for account in accounts:
                    (move.line_ids + reverse_move.line_ids)\
                        .filtered(lambda line: line.account_id == account and line.balance)\
                        .reconcile()

        return reverse_moves
