# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'post sale transactions'

    post_sale_order_ref = fields.Many2one('sale.order', help="Post Sale ref", readonly=1)
    post_sale_type = fields.Selection([('Return', 'Return'), ('Remake', 'Remake'),
                             ('Exchange', 'Exchange'), ('Warranty', 'Warranty'),
                             ], required=False, default=None, readonly=1)
