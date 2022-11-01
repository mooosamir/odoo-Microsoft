
from odoo import models, fields


class SaleLineDiagnosis(models.Model):
    _name = 'sale.line.diagnosis.setup'
    _rec_name = 'seq'

    sale_id = fields.Many2one('sale.order')
    sale_line_id = fields.Many2one('sale.order.line')
    move_line_id = fields.Many2one('account.move.line')
    diagnosis_code_id = fields.Many2one('diagnosis.setup', string='Diagnosis')
    seq = fields.Char()
