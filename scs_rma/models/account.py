# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    rma_id = fields.Many2one('rma.ret.mer.auth', string='RMA')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            rec.rma_id.rma_close()
        return res

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def post(self):
        '''Method to change state to paid when state in invoice is paid'''
        res = super(AccountPayment, self).post()
        for rec in self:
            for invoice in rec.invoice_ids:
                if invoice.invoice_payment_state == 'paid':
                    invoice.rma_id.write({'invoice_status': 'paid'})
                else:
                    invoice.rma_id.write({'invoice_status': 'pending'})
        return res
