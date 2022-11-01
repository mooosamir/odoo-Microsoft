import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('patient_id')
    def _compute_invoice_balance(self):
        for data in self:
            invoices = self.env['account.move'].search([('partner_id', '=', data.id), ('type', '=', 'out_invoice')])
            data.patient_balance = sum([invoice.amount_residual for invoice in invoices])

    patient_balance = fields.Float(default=0.00, compute='_compute_invoice_balance')

    # @api.onchange('account_balance')
    # def _onchange_account_balance(self):
    #     for res in self:
    #         res.account_balance = "$ " + "{:.2f}".format(res.patient_balance)

    def open_credit_notes(self):
        self.ensure_one()
        action = self.env.ref('account.action_move_out_refund_type').read()[0]
        action['name'] = _('Credit Notes')
        action['domain'] = [('partner_id', '=', self.id), ('type', '=', 'out_refund')]
        return action
        # return {
        #     'name': _('Credit Notes'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'account.move',
        #     'view_type': 'list,form',
        #     'view_mode': 'list,form',
        #     'target': 'current',
        #     'views': [('account.view_invoice_tree', 'list'), (False, 'form')],
        #     'domain': [('partner_id', '=', self.id), ('type', '=', 'out_refund')],
        # }

    def sales_list_view(self):
        self.ensure_one()
        return {
            'name': _('Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'list,form',
            'view_mode': 'list,form',
            'target': 'current',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('partner_id', '=', self.id)],
        }

    def action_view_partner_invoices(self):
        self.ensure_one()
        # action = {
        #     'name': _('Invoices'),
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'account.move',
        #     'view_type': 'tree,kanban,form',
        #     'view_mode': 'tree,kanban,form',
        #     'target': 'current',
        #     'views': [(self.env.ref('account.view_invoice_tree').id, 'list'),
        #               (False, 'form'), (False, 'kanban')],
        #     'domain': [
        #         ('type', 'in', ('out_invoice', 'out_refund')),
        #         ('partner_id', '=', self.id),
        #     ],
        #     'context': {
        #         'default_type': 'out_invoice',
        #         'type': 'out_invoice',
        #         'journal_type': 'sale',
        #         # 'search_default_unpaid': 1
        #     }
        # }
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [
            ('type', 'in', ('out_invoice', 'out_refund')),
            ('partner_id', 'child_of', self.id),
        ]
        action['context'] = {
            'default_type': 'out_invoice',
            'type': 'out_invoice',
            'journal_type': 'sale',
        }
        return action
