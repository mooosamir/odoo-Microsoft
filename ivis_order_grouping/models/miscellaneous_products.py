import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)


class MiscellaneousProducts(models.Model):
    _name = 'miscellaneous.products'

    multi_order_type_id = fields.Many2one('multi.order.type')
    miscellaneous_products = fields.Many2one('product.product', string="Miscellaneous",
                                              domain="[('product_tmpl_id.categ_id.name','=','Accessory')]")
    qty = fields.Integer('Qty', default=1)
