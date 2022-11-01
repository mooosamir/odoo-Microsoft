from odoo import models, fields


class UomInherit(models.Model):
    _inherit = 'uom.uom'

    code = fields.Char()

