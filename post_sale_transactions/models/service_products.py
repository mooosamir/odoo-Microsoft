from odoo import fields, models


class ServiceProducts(models.Model):
    _inherit = 'service.products'

    return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
