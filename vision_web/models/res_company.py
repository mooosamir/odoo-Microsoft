# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = "credentials for VisionWeb server"

    # vw_bill_account = fields.Char(string="Bill Account")
    vw_ship_account = fields.Char(string="Ship Account")
