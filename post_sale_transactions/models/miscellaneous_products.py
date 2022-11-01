from odoo import fields, models


class MiscellaneousProducts(models.Model):
    _inherit = 'miscellaneous.products'

    return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
