from odoo import models, fields, tools, api, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    processed_in_post_sale = fields.Boolean(copy=False)
    post_sale_type = fields.Selection([('Return', 'Return'), ('Remake', 'Remake'),
                                       ('Exchange', 'Exchange'), ('Warranty', 'Warranty'),
                                       ], related='order_id.post_sale_type')
    return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    post_sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line", copy=False)
