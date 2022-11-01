import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MultiOrderTypeHistorical(models.Model):
    _name = "multi.order.type.historical"
    _description = "multi.order.type.historical"

    status = fields.Char(string="Status")
    multi_order_type_id = fields.Many2one('multi.order.type', required=1)