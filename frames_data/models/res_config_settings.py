# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "credentials for FramesData server"

    fd_username = fields.Char(string="username", config_parameter="FramesData.username")
    fd_szipcode = fields.Char(string="szipcode", config_parameter="FramesData.szipcode")
    fd_bzipcode = fields.Char(string="bzipcode", config_parameter="FramesData.bzipcode")
    fd_locations = fields.Char(string="locations", config_parameter="FramesData.locations")

    def get_values(self):
        res = super(GeneralSettings, self).get_values()

        fd_username = self.env["ir.config_parameter"].get_param("fd_username", default=None)
        fd_szipcode = self.env["ir.config_parameter"].get_param("fd_szipcode", default=None)
        fd_bzipcode = self.env["ir.config_parameter"].get_param("fd_bzipcode", default=None)
        fd_locations = self.env["ir.config_parameter"].get_param("fd_locations", default=None)

        res.update(
            fd_username=fd_username or False,
            fd_szipcode=fd_szipcode or False,
            fd_bzipcode=fd_bzipcode or False,
            fd_locations=fd_locations or False,
        )
        return res

    def set_values(self):
        super(GeneralSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].set_param("fd_username", record.fd_username or '')
            self.env['ir.config_parameter'].set_param("fd_szipcode", record.fd_szipcode or '')
            self.env['ir.config_parameter'].set_param("fd_bzipcode", record.fd_bzipcode or '')
            self.env['ir.config_parameter'].set_param("fd_locations", record.fd_locations or '')