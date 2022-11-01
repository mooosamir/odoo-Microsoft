# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PostSaleReasons(models.Model):
    _name = 'post.sale.reasons'
    _description = 'post sale reasons'

    name = fields.Char()
