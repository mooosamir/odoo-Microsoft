from odoo import api, fields, models, _
from datetime import datetime


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    promotion_id = fields.Many2one('promotion.form',string='Promotion ID')