
from odoo import models, fields


class OrderStatus(models.Model):
    _name = "order.status"
    _description = "Order Status"

    name = fields.Char(string="Order Status")
