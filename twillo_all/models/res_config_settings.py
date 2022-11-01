# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "credentials for Twilio server"

    account_sid = fields.Char(string="Account Sid", config_parameter="twilio.account_sid")
    auth_token = fields.Char(string="Auth Token", config_parameter="twilio.auth_token")
    from_number = fields.Char(string="From number", config_parameter="twilio.from_number")
    webhook = fields.Char(string="WebHook", config_parameter="twilio.webhook")

    def get_values(self):
        res = super(GeneralSettings, self).get_values()
        account_sid = self.env["ir.config_parameter"].get_param(
            "account_sid", default=None)
        auth_token = self.env["ir.config_parameter"].get_param(
            "auth_token", default=None)
        from_number = self.env["ir.config_parameter"].get_param(
            "from_number", default=None)
        webhook = self.env["ir.config_parameter"].get_param(
            "webhook", default=None)
        res.update(
            account_sid=account_sid or False,
            auth_token=auth_token or False,
            from_number=from_number or False,
            webhook=webhook or False,
        )
        return res

    def set_values(self):
        super(GeneralSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].set_param(
                "account_sid", record.account_sid or '')
            self.env['ir.config_parameter'].set_param(
                'auth_token', record.auth_token or '')
            self.env['ir.config_parameter'].set_param(
                'from_number', record.from_number or '')
            self.env['ir.config_parameter'].set_param(
                'webhook', record.webhook or '')
