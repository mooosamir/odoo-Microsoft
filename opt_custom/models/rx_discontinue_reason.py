# -*- coding: utf-8 -*-

from odoo import fields, models, api


class RxDiscontinueReason(models.Model):
    _name = 'rx.discontinue.reason'
    _description = 'Rx Discontinue Reason'

    name = fields.Char(string="Reason", required=True)
