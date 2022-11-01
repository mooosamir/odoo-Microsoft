# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class PaymentToken(models.Model):
    _inherit = 'payment.token'
    _description = 'post sale transactions'

    brand = fields.Char(string="Brand")
