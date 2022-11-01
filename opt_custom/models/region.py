# -*- coding: utf-8 -*-

from odoo import fields, models, api


class RegionRegion(models.Model):
    _name = 'spec.region'
    _description = 'Region'

    name = fields.Char(string="Region", required=True)
