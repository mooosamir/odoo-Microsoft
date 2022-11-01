# -*- coding: utf-8 -*-
import odoo.exceptions
from odoo import models, fields, api, _
import json


# class CashBox(models.Model):
#     _name = 'cash.box'
#
#     cashbox_start_id = fields.Many2one('account.bank.statement.cashbox', string="Starting Cashbox")
#     cashbox_end_id = fields.Many2one('account.bank.statement.cashbox', string="Ending Cashbox")


class SaleOrderSession(models.Model):
    _name = 'sale.order.session'
    _description = 'post sale reasons'
    _order = 'closing_date desc'

    def _last_session_closing_date(self):
        for session in self:
            session.last_session_closing_date = self.env['sale.order.session'].search([("state", 'in', ['close'])],
                                                                                            order="closing_date", limit=1).closing_date

    def _get_order_count(self):
        for session in self:
            session.order_count = self.env['sale.order'].search_count([("sale_order_session_id", '=', session.id)])

    def _get_invoices_count(self):
        for session in self:
            session.invoices_count = self.env['account.move'].search_count([("sale_order_session_id", '=', session.id),
                                                                            ('type', '!=', 'entry')])

    def _get_payments_count(self):
        for session in self:
            # ids = []
            # invoice_payments_widgets = self.env['sale.order'].search([("sale_order_session_id", 'in', self.ids)]) \
            #     .mapped('invoice_payments_widget')
            # invoice_payments_widgets = [x for x in invoice_payments_widgets if x and x != 'false']
            # for invoice_payments_widget in invoice_payments_widgets:
            #     invoice_payments_widget = json.loads(invoice_payments_widget)
            #     ids += [x['move_id'] for x in invoice_payments_widget['content']]
            #
            # session.payments_count = len(ids)
            session.payments_count = self.env['account.payment'].search_count([("sale_order_session_id", '=', session.id)])

    def _get_payments_total(self):
        total = {
            "id": self.id,
            "journal_ids": [],
            "cash_register_balance_start": self.cash_register_balance_start,
            "cash_register_balance_end": self.cash_register_balance_end_real,
        }
        has_cash = False
        for session in self:
            journal_ids = self.env['account.payment'].search([("sale_order_session_id", '=', session.id)]).mapped('journal_id')

            for journal_id in journal_ids:
                _sum = sum(self.env['account.payment'].search([("sale_order_session_id", '=', session.id),("journal_id", '=', journal_id.id)]).mapped('amount'))
                total["journal_ids"].append({
                    "Id": journal_id.id,
                    "name": journal_id.name,
                    "total": _sum,
                    "type": journal_id.type,
                })
                if journal_id.name.lower() in ['bank']:
                    total["journal_ids"][-1]['counted'] = 0
                    total["journal_ids"][-1]['difference'] = _sum * -1
                elif journal_id.name.lower() in ['cash']:
                    has_cash = True
                    total["journal_ids"][-1]['counted'] = 0
                    total["journal_ids"][-1]['difference'] = (self.cash_register_balance_start + _sum) * -1
            if not has_cash:
                journal_id = self.env['account.journal'].search([('name', '=', 'Cash')], limit=1)
                total["journal_ids"].append({
                    "Id": journal_id.id,
                    "name": "Cash",
                    "total": 0,
                    "type": journal_id.type,
                })
                total["journal_ids"][-1]['counted'] = 0
                total["journal_ids"][-1]['difference'] = (self.cash_register_balance_start + 0) * -1

            session.payments_total = total

    def _get_invoices_total(self):
        for session in self:
            session.invoices_total = sum(self.env['account.move'].search([("sale_order_session_id", '=', session.id),
                                                                            ('type', '!=', 'entry')]).mapped('amount_total_signed'))

    def _get_payments_lines_count(self):
        for session in self:
            account_payment_ids = self.env['account.payment'].search([('sale_order_session_id', 'in', self.ids)]).ids
            session.payments_lines_count = self.env['account.move.line'].search_count([("payment_id", 'in', account_payment_ids)])

    def _get_invoices_lines_count(self):
        for session in self:
            line_ids = []
            account_move_ids = self.env['account.move'].search([('sale_order_session_id', 'in', self.ids),
                                                                ('type', '!=', 'entry')])
            for account_move_id in account_move_ids:
                line_ids += account_move_id.line_ids
            session.invoices_lines_count = len(line_ids)

    def _get_journal_lines_count(self):
        for session in self:
            line_ids = []
            # account_move_ids = self.env['account.move'].search([('sale_order_session_id', 'in', self.ids),
            #                                                     ('type', '!=', 'entry')])
            account_move_ids = self.env['account.move'].search([('sale_order_session_id', 'in', self.ids)])
            for account_move_id in account_move_ids:
                line_ids += account_move_id.line_ids
            session.journal_lines_count = len(line_ids)

    # def open_cashbox_pos(self):
    #     self.ensure_one()
    #     if not self.cash_register_id.id:
    #         self.cash_register_id = self.cash_register_id.create({'journal_id': self.env['account.journal'].search([],limit=1).id})
    #     action = self.cash_register_id.open_cashbox_id()
    #     action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
    #     # action['context']['pos_session_id'] = self.id
    #     # action['context']['default_pos_id'] = self.config_id.id
    #     return action
    #
    #     return {
    #         'name': 'Possible Values',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'account.bank.statement.cashbox',
    #         'target': 'new',
    #         'view_mode': 'form',
    #         'views': [(self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id, 'form')],
    #         # 'context': {'create': False},
    #         'help': _(u"See all possible values")}
    #
    #     action = self.cash_register_id.open_cashbox_id()
    #     action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
    #     return action

    name = fields.Char(required=1, default=lambda self: fields.date.today().strftime('%b %d,%Y'), readonly=True)
    closing_date = fields.Datetime(string="Session Close Datetime", copy=False)
    last_session_closing_date = fields.Datetime(compute='_last_session_closing_date')
    state = fields.Selection([('draft', 'draft'),
                              ('opening_control', 'Opening Control'), ('in_progress', 'In Progress'), ('closing_control', 'Closing Control'),
                              ('closed', 'Closed')
                              ], string="State", default='draft', required=True)
    order_count = fields.Integer(string='Customer Note', compute='_get_order_count', readonly=True)
    payments_count = fields.Integer(string='Sale Order Payments', compute='_get_payments_count', readonly=True)
    payments_lines_count = fields.Integer(string='Sale Order Payments', compute='_get_payments_lines_count', readonly=True)
    invoices_count = fields.Integer(string='Sale Order Invoices', compute='_get_invoices_count', readonly=True)
    invoices_lines_count = fields.Integer(string='Sale Order Invoices', compute='_get_invoices_lines_count', readonly=True)
    journal_lines_count = fields.Integer(string='Journal Enties', compute='_get_journal_lines_count', readonly=True)
    payments_total = fields.Char(string='Sale Order Invoices', compute='_get_payments_total', readonly=True)
    payments_total_widget = fields.Char(string='Sale Order Invoices')
    invoices_total = fields.Integer(string='Sale Order Invoices', compute='_get_invoices_total', readonly=True)
    opened_by = fields.Many2one('res.users', string="Opened By")
    closed_by = fields.Many2one('res.users', string="Closed By")
    # cashbox = fields.Many2one('cash.box', string="Closed By")
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(related="company_id.currency_id", string='Currency', readonly=False)

    # cash_register_id = fields.Many2one('account.bank.statement', string='Cash Register')

    cash_register_balance_end_real = fields.Monetary(
        # related='cash_register_id.balance_end_real',
        string="Ending Balance",
        help="Total of closing cash control lines.",
        readonly=True)
    cash_register_balance_start = fields.Monetary(
        # related='cash_register_id.balance_start',
        string="Starting Balance",
        help="Total of opening cash control lines.",
        readonly=True)

    # cash_control = fields.Boolean(compute='_compute_cash_all', string='Has Cash Control', compute_sudo=True)
    # cash_journal_id = fields.Many2one('account.journal', compute='_compute_cash_all', string='Cash Journal', store=True)
    # cash_register_id = fields.Many2one('account.bank.statement', compute='_compute_cash_all', string='Cash Register', store=True)
    # cash_register_balance_start = fields.Monetary(
    #     related='cash_register_id.balance_start',
    #     string="Starting Balance",
    #     help="Total of opening cash control lines.",
    #     readonly=True)

    @api.onchange('payments_total_widget')
    def set_cash_register_balance_start_end(self):
        if self.payments_total_widget:
            payments_total_widget = json.loads(self.payments_total_widget)
            if 'cash_register_balance_start' in payments_total_widget:
                self.cash_register_balance_start = payments_total_widget['cash_register_balance_start']
            if 'cash_register_balance_end' in payments_total_widget:
                self.cash_register_balance_end_real = payments_total_widget['cash_register_balance_end']

    @api.model
    def create(self, values):
        open_sessions = self.env['sale.order.session'].search_count([("state", 'in', ['draft', 'in_progress'])])
        res = super(SaleOrderSession, self).create(values)
        if open_sessions > 0:
            raise odoo.exceptions.ValidationError("Can't Create new session, while previous is open.")
        return res

    # def open_starting_cashbox(self):
    #     self.ensure_one()
    #     if not self.cash_register_id.id:
    #         self.cash_register_id = self.cash_register_id.create({'journal_id': self.env['account.journal'].search([],limit=1).id})
    #     action = self.cash_register_id.with_context(balance='start').open_cashbox_id()
    #     action['view_id'] = self.env.ref('point_of_sale.view_account_bnk_stmt_cashbox_footer').id
    #     return action

    def open_session(self):
        self.state = "opening_control"
        self.opened_by = self.env.user.id
        # return self.open_starting_cashbox()

    def start_session(self):
        self.state = "in_progress"
        self.opened_by = self.env.user.id

    def close_session(self):
        self.state = "closing_control"
        self.closing_date = fields.datetime.now()
        self.closed_by = self.env.user.id

    def close_and_post_session(self):
        payments_total_widget = json.loads(self.payments_total_widget)
        if len(payments_total_widget['journal_ids']) > 0:
            amount = sum([x['difference'] for x in payments_total_widget['journal_ids']])
            if amount < 0:
                account_move_id = self.env['account.move'].create({
                    'ref': "Session : " + self.name,
                    'date': fields.date.today(),
                    'journal_id': self.env['account.journal'].search([('name', '=', 'Cash')], limit=1).id,
                    'company_id': self.env.company.id,
                    'sale_order_session_id': self.id,
                })
                self.env['account.move.line'].create([
                    {
                        'account_id': self.env['account.account'].search([('name', '=', 'Cash Difference Loss')], limit=1).id,
                        'name': "Cash difference observed during the Sale Order counting (Loss)",
                        'debit': amount * -1,
                        'credit': 0,
                        'move_id': account_move_id.id,
                    },
                    {
                    'account_id': self.env['account.account'].search([('name', '=', 'Cash')], limit=1).id,
                    'name': "Cash difference observed during the Sale Order counting (Loss)",
                    'debit': 0,
                    'credit': amount * -1,
                    'move_id': account_move_id.id,
                    }
                ])
                account_move_id.action_post()
            elif amount > 0:
                account_move_id = self.env['account.move'].create({
                    'ref': "Session : " + self.name,
                    'date': fields.date.today(),
                    'journal_id': self.env['account.journal'].search([('name', '=', 'Cash')], limit=1).id,
                    'company_id': self.env.company.id,
                })
                self.env['account.move.line'].create([
                    {
                        'account_id': self.env['account.account'].search([('name', '=', 'Cash Difference Gain')], limit=1).id,
                        'name': "Cash difference observed during the Sale Order counting (Profit)",
                        'debit': 0,
                        'credit': amount,
                        'move_id': account_move_id.id,
                    },
                    {
                        'account_id': self.env['account.account'].search([('name', '=', 'Cash')], limit=1).id,
                        'name': "Cash difference observed during the Sale Order counting (Profit)",
                        'debit': amount,
                        'credit': 0,
                        'move_id': account_move_id.id,
                    }
                ])
                account_move_id.action_post()

        self.state = "closed"

    def action_view_order(self):
        return {
            'name': _('Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('sale.view_quotation_tree_with_onboarding').id, 'tree'),
                (self.env.ref('sale.view_order_form').id, 'form'),
                ],
            'type': 'ir.actions.act_window',
            'domain': [('sale_order_session_id', 'in', self.ids)],
        }

    def action_view_payments(self):
        return {
            'name': _('Payments'),
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('sale_order_session_id', 'in', self.ids)],
        }

    def action_view_payments_lines(self):
        account_payment_ids = self.env['account.payment'].search([('sale_order_session_id', 'in', self.ids)]).ids
        return {
            'name': _('Invoices Lines'),
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', account_payment_ids)],
        }

    def action_view_invoices(self):
        return {
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('sale_order_session_id', 'in', self.ids), ('type', '!=', 'entry')],
        }

    def action_view_invoices_lines(self):
        line_ids = []
        account_move_ids = self.env['account.move'].search([('sale_order_session_id', 'in', self.ids),
                                                            ('type', '!=', 'entry')])
        for account_move_id in account_move_ids:
            line_ids += account_move_id.line_ids.ids
        return {
            'name': _('Invoices Lines'),
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', line_ids)],
        }

    def action_view_journal_lines(self):
        line_ids = []
        # account_move_ids = self.env['account.move'].search([('sale_order_session_id', 'in', self.ids),
        #                                                     ('type', '!=', 'entry')])
        account_move_ids = self.env['account.move'].search([('sale_order_session_id', 'in', self.ids)])
        # for account_move_id in account_move_ids:
        #     line_ids += account_move_id.line_ids.ids

        return {
            'name': _('Journal Items'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'view_mode': 'tree',
            'view_id':self.env.ref('account.view_move_line_tree_grouped').id,
            'domain': [('id', 'in', account_move_ids.mapped('line_ids').ids)],
            'context': {
                'journal_type':'general',
                'search_default_group_by_move': 1,
                'group_by':'move_id', 'search_default_posted':1,
                'name_groupby':1,
            },
        }


        return {
            'name': _('Invoices Lines'),
            'res_model': 'account.move.line',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', line_ids)],
        }
