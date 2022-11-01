from odoo import models, fields, api


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    @api.depends('co_pay', 'pt_resp', 'price_unit')
    def sum_pay_pt(self):
        for rec in self:
            rec.pt_total = rec.price_unit * rec.quantity
            if rec.insurance_id.id:
                rec.pt_total = rec.co_pay + rec.pt_resp if rec.co_pay > 0 or rec.pt_resp > 0 else rec.price_unit * rec.quantity
                rec.insur = rec.quantity * rec.price_unit - rec.pt_total if rec.quantity * rec.price_unit - rec.pt_total > 0 else 0
            else:
                rec.insur = 0

    prescription_id = fields.Many2one('spec.contact.lenses', string="Prescription")
    lab_details_id = fields.Many2one('multi.order.type', string='Lab Details')
    insurance_id = fields.Many2one('spec.insurance')
    authorization_id = fields.Many2one('spec.insurance.authorizations')
    co_pay = fields.Float(string='CO-PAY')
    pt_resp = fields.Float(string='PT RESP')
    pt_total = fields.Float(string='PT TOTAL', compute='sum_pay_pt')
    insur = fields.Float(string='INSUR', compute='sum_pay_pt')
    DX = fields.Many2many('sale.line.diagnosis.setup', 'move_line_id')
    actual_retail = fields.Float(string='Retails', String='Product Price')
