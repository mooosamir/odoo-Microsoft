
from odoo import models, fields


class DiscountReason(models.Model):
    _name = "discount.reason"
    _description = "Discount Reason"

    name = fields.Char(string="Discount Reason")
