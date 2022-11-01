# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import date,datetime

from odoo import api, fields, models
from logging import getLogger
from random import randint
from odoo.exceptions import AccessError
_logger = getLogger(__name__)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# try:
#     import twilio

# except ImportError as error:
#     _logger.debug(error)
# from twilio.rest import Client


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_sid = fields.Char("Account Sid")
    is_twilio = fields.Boolean("Twilio")
    account_token = fields.Char("Account Token")
    from_mobile = fields.Char("From Mobile")
    global_send = fields.Boolean("Security Enforce 2FA")
    email_from = fields.Char("Email From")
    api_email_key = fields.Char("Email key", default='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')

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('account_sid', self.account_sid)
        set_param('account_token', self.account_token)
        set_param('from_mobile', self.from_mobile)
        set_param('global_send', self.global_send)
        set_param('email_from', self.email_from)
        set_param('api_email_key', self.api_email_key)
        return res


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            account_sid = ICPSudo.get_param('account_sid'),
            account_token = ICPSudo.get_param('account_token'),
            from_mobile = ICPSudo.get_param('from_mobile'),
            global_send = ICPSudo.get_param('global_send'),
            email_from = ICPSudo.get_param('email_from'),
            api_email_key = ICPSudo.get_param('api_email_key')
        )
        return res