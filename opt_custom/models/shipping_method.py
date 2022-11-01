# -*- coding: utf-8 -*-

from odoo import fields, models


class ShippingMethods(models.Model):
    _inherit = 'delivery.carrier'
    _description = "shipping method"
    
    lead_time = fields.Integer(string="Lead Time (days)")
