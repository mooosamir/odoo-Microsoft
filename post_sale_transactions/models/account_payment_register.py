from odoo import api, fields, models, _, exceptions
MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'

    def manual_creation(self, amount):
        for invoices in self.invoice_ids:
            amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
            values = {
                'journal_id': self.journal_id.id,
                'payment_method_id': self.payment_method_id.id,
                'payment_date': self.payment_date,
                'communication': self._prepare_communication(invoices),
                'invoice_ids': [(6, 0, invoices.ids)],
                'payment_type': ('inbound' if amount > 0 else 'outbound'),
                'amount': abs(amount),
                'currency_id': invoices[0].currency_id.id,
                'partner_id': invoices[0].commercial_partner_id.id,
                'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
                'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
            }
            return values
