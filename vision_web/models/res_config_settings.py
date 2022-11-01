# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "credentials for VisionWeb server"

    vw_username = fields.Char(string="username", config_parameter="VisionWeb.username")
    vw_password = fields.Char(string="password", config_parameter="VisionWeb.password")
    vw_sloid = fields.Char(string="sloid", config_parameter="VisionWeb.sloid")

    def get_values(self):
        res = super(GeneralSettings, self).get_values()
        vw_username = self.env["ir.config_parameter"].get_param("vw_username", default=None)
        vw_password = self.env["ir.config_parameter"].get_param("vw_password", default=None)
        vw_sloid = self.env["ir.config_parameter"].get_param("vw_sloid", default=None)
        res.update(
            vw_username=vw_username or False,
            vw_password=vw_password or False,
            vw_sloid=vw_sloid or False,
        )
        return res

    def set_values(self):
        super(GeneralSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].set_param("vw_username", record.vw_username or '')
            self.env['ir.config_parameter'].set_param('vw_password', record.vw_password or '')
            self.env['ir.config_parameter'].set_param('vw_sloid', record.vw_sloid or '')
