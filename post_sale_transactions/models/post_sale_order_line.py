# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PostSaleOrderLine(models.Model):
    _name = 'post.sale.order.line'
    _description = 'post sale line'

    sale_order_id = fields.Many2one('sale.order')
    sale_order_line_id = fields.Many2one('sale.order.line')
    name = fields.Char()
    sol_name = fields.Text(string='Description', required=True, related='sale_order_line_id.name')
    sol_product_id = fields.Many2one(
        'product.product', string='Product', related='sale_order_line_id.product_id')
    sol_product_uom_qty = fields.Float(string='Quantity', related='sale_order_line_id.product_uom_qty')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
    # sol_price_subtotal = fields.Monetary(related='sale_order_line_id.price_subtotal')
    sol_pt_total = fields.Float(string='PT TOTAL')
    qty = fields.Float(string="Qty", readonly=True)
    currency_id = fields.Many2one(related='sale_order_id.currency_id', depends=['sale_order_id.currency_id'], store=True, string='Currency', readonly=True)
    return_location = fields.Many2one('stock.location', string="Return Location", readonly=1)
    # account_move_line_id = fields.Many2one('account.move.line', required=True, readonly=True)
    tax_id = fields.Many2many('account.tax', string="Taxes")
