import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)


class ServiceProducts(models.Model):
    _name = 'service.products'
    _description = 'service.products'

    multi_order_type_id = fields.Many2one('multi.order.type')
    service_products = fields.Many2one('product.product', string="Service",
                                        domain="[('product_tmpl_id.categ_id.name','=','Services')]")
    qty = fields.Integer('Qty', default=1)
