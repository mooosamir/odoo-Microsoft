from odoo import models, fields


class ClaimLineInherit(models.Model):
    _inherit = 'claim.line'

    diagnosis_code_sale_ids = fields.Many2many('sale.line.diagnosis.setup',
                                               string='Dx Pointers')