# # -*- coding: utf-8 -*-

from odoo import fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    vendor_picking_id = fields.Many2one('stock.picking', string='Picking vendor invoice', ondelete="restrict")


class Picking(models.Model):
    _inherit = "stock.picking"


    vendor_invoice = fields.Char('Vendor Invoice')
    invoice_date = fields.Datetime('Invoice Date')
    invoice_generated = fields.Boolean(string="Invoice Generated")

    def action_generate_vendor_bill(self):
        context = dict(self._context) or {}
        context.update({'create': False, 'delete': False})        
        bill_exist = self.env['account.move'].search([('vendor_picking_id', '=', self.id)])
        if not bill_exist:
            move_line_vals = []
            for moves in self.move_ids_without_package:
                move_line_vals.append((0, 0, {
                                            'product_id': moves.product_id.id,
                                            'quantity': moves.quantity_done,
                                                }))
            bill_vals = {'type': 'in_invoice',
                        'vendor_picking_id': self.id,
                        'partner_id': self.partner_id.id,
                        'invoice_line_ids': move_line_vals}
            bill_id = self.env['account.move'].create(bill_vals)
            self.invoice_generated = True
        else :
            bill_id = bill_exist

        return {'name': _('Vendor Bill'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'views': [(self.env.ref('account.view_move_form').id, 'form')],
                'domain': [('vendor_picking_id', '=', self.id)],
                'res_id': bill_id.id,
                'type': 'ir.actions.act_window',
                'context': context
                }

    def action_view_vendor_bill(self):
        context = dict(self._context) or {}
        context.update({'create': False, 'delete': False})        
        bill_exist = self.env['account.move'].search([('vendor_picking_id', '=', self.id)])        
        if bill_exist:
            return {'name': _('Vendor Bill'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'views': [(self.env.ref('account.view_move_form').id, 'form')],
                'domain': [('vendor_picking_id', '=', self.id)],
                'res_id': bill_exist.id,
                'type': 'ir.actions.act_window',
                'context': context
                }