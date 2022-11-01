# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "credentials for Twilio server"

    t_account_sid = fields.Char(string="Account Sid", config_parameter="twilio.t_account_sid")
    t_auth_token = fields.Char(string="Auth Token", config_parameter="twilio.t_auth_token")
    t_from_number = fields.Char(string="From number", config_parameter="twilio.t_from_number")
    t_website_address = fields.Char(string="Website Address", config_parameter="twilio.t_website_address")
    t_message_outgoing_webhook = fields.Char(string="Message Outgoing WebHook", config_parameter="twilio.t_message_outgoing_webhook")
    t_call_outgoing_webhook = fields.Char(string="Call Outgoing WebHook", config_parameter="twilio.t_call_outgoing_webhook")
    t_message_incoming_webhook = fields.Char(string="Message Incoming WebHook", config_parameter="twilio.t_message_incoming_webhook")
    t_call_incoming_webhook = fields.Char(string="Call Incoming WebHook", config_parameter="twilio.t_call_incoming_webhook")

    def get_values(self):
        res = super(GeneralSettings, self).get_values()
        t_account_sid = self.env["ir.config_parameter"].get_param(
            "t_account_sid", default=None)
        t_auth_token = self.env["ir.config_parameter"].get_param(
            "t_auth_token", default=None)
        t_from_number = self.env["ir.config_parameter"].get_param(
            "t_from_number", default=None)
        t_website_address = self.env["ir.config_parameter"].get_param(
            "t_website_address", default=None)
        t_message_outgoing_webhook = self.env["ir.config_parameter"].get_param(
            "t_message_outgoing_webhook", default=None)
        t_call_outgoing_webhook = self.env["ir.config_parameter"].get_param(
            "t_call_outgoing_webhook", default=None)
        t_message_incoming_webhook = self.env["ir.config_parameter"].get_param(
            "t_message_incoming_webhook", default=None)
        t_call_incoming_webhook = self.env["ir.config_parameter"].get_param(
            "t_call_incoming_webhook", default=None)
        res.update(
            t_account_sid=t_account_sid or False,
            t_auth_token=t_auth_token or False,
            t_from_number=t_from_number or False,
            t_website_address=t_website_address or False,
            t_message_outgoing_webhook=t_message_outgoing_webhook or False,
            t_call_outgoing_webhook=t_call_outgoing_webhook or False,
            t_message_incoming_webhook=t_message_incoming_webhook or False,
            t_call_incoming_webhook=t_call_incoming_webhook or False,
        )
        return res

    def set_values(self):
        super(GeneralSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].set_param(
                "t_account_sid", record.t_account_sid or '')
            self.env['ir.config_parameter'].set_param(
                't_auth_token', record.t_auth_token or '')
            self.env['ir.config_parameter'].set_param(
                't_from_number', record.t_from_number or '')
            self.env['ir.config_parameter'].set_param(
                't_website_address', record.t_website_address or '')
            self.env['ir.config_parameter'].set_param(
                't_message_outgoing_webhook', record.t_message_outgoing_webhook or '')
            self.env['ir.config_parameter'].set_param(
                't_call_outgoing_webhook', record.t_call_outgoing_webhook or '')
            self.env['ir.config_parameter'].set_param(
                't_message_incoming_webhook', record.t_message_incoming_webhook or '')
            self.env['ir.config_parameter'].set_param(
                't_call_incoming_webhook', record.t_call_incoming_webhook or '')