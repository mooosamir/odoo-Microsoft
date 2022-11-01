# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResBranch(models.Model):
    _inherit = "res.company"

    lat = fields.Char(string="Latitude")
    lng = fields.Char(string="Longitude")
    address = fields.Text('Address', compute='_compute_complete_address')

    def _compute_complete_address(self):
        for s in self:
            if not s.street:
                s.street = ''
            if not s.street2:
                s.street2 = ''
            if not s.zip:
                s.zip = ''
            if not s.city:
                s.city = ''
            s.address = str(s.street) + " " + str(s.street2) + " " + str(s.zip) + " " + str(s.city) + " " + str(
                s.state_id.name) + " " + str(s.country_id.name)
