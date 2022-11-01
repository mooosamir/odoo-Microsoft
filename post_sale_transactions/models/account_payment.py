from odoo import api, fields, models, _, exceptions


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    from_sale_order = fields.Boolean(default=False)
    reference_number = fields.Char(copy=False, help="Sale, Eyecare payment reference", string='Reference #')
    so_balance = fields.Float(default=0, readonly=True, string="Balance")
    so_change = fields.Float(default=0, readonly=True, string="Change")
    so_cash = fields.Float(default=0, string="Cash")
    amount_remaining = fields.Float(default=0)
    sale_order_session_id = fields.Many2one('sale.order.session', readonly=True, copy=False)
    payment_token_brand = fields.Char(string="Brand", related="payment_token_id.brand")

    @api.onchange('so_cash')
    def so_cash_changed(self):
        # self.amount = self.so_cash
        default_so_balance = self.env.context.get('default_so_balance', False)
        if default_so_balance:
            self.so_balance = default_so_balance - self.so_cash
        if (default_so_balance - self.so_cash) < 0:
            self.so_change = (default_so_balance - self.so_cash) * -1
        else:
            self.so_change = 0

    @api.onchange('amount')
    def amount_changed(self):
        self.so_cash = self.amount

    def post(self):
        for data in self:
            data.amount_remaining = data.amount
            if data.so_cash:
                data.amount = data.so_cash
            return super(AccountPayment, data).post()

    def open_stripe_gateway(self):
        if self.so_cash <= 0:
            raise exceptions.UserError("Specify an amount greater then 0")
        return {
            'type': 'ir.actions.client',
            'name':'Stripe Checkout',
            'tag':'stripe_checkout',
            'target': 'new',
            'context': {
                'account_payment_id': self.id,
            },
        }

    def reopen_account_payment(self, id):
        return {
            'name': "Register Payment",
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'res_id': int(id),
            'views': [(self.env.ref("account.view_account_payment_invoice_form").id, 'form')],
            'target': 'new',
        }

    def action_view_balance_reporting_wizard(self):
        return {
            'name': _('Balance Reporting'),
            'res_model': 'balance.reporting.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('post_sale_transactions.balance_reporting_wizard_view').id,
            # 'context': {
            #     'default_sale_order_id': self.id,
            # },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
