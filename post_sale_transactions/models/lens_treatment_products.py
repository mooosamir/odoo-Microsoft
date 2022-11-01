import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)


class LensTreatmentProducts(models.Model):
    _name = 'lens_treatment.products'

    multi_order_type_id = fields.Many2one('multi.order.type')
    lenstreatment_products_id = fields.Many2one('product.product')
    return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
