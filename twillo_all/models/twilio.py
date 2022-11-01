# -*- coding: utf-8 -*-

import os
import time
from twilio.rest import Client
from odoo import models, fields, api
from odoo.exceptions import UserError
from twilio.base.exceptions import TwilioRestException


class Twilio(models.Model):
    _name = 'twilio'
    _description = 'Module for using twilio api\'s'

    message_body = fields.Text(string="Message Body")
    mobile = fields.Char(string="Mobile Number")
    media_url = fields.Char(string="Media url")
    response_message = fields.Text(string="Response SMS")
    response_mms = fields.Text(string="Response MMS")
    response_call = fields.Text(string="Response Call")
    state = fields.Selection([('draft', 'draft'),
                              ('send', 'send')], default="draft")

    def get_twilio_config(self):
        twilio_account_sid = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_account_sid')]).value
        twilio_auth_token = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_auth_token')]).value
        twilio_from_number = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_from_number')]).value
        twilio_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_webhook')]).value

        return twilio_account_sid, twilio_auth_token, twilio_from_number, twilio_webhook \
            if twilio_account_sid and twilio_auth_token and twilio_from_number and twilio_webhook else None

    def send_message(self):
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        try:
            time.sleep(1)
            message = client.messages \
                .create(
                    body=self.message_body,
                    status_callback=configuration[3],
                    from_=configuration[2],
                    to=self.mobile
            )
            self.response_message = message
            # self.response = message.sid
        except TwilioRestException as e:
            raise UserError(e)

    def send_mms(self):
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        try:
            time.sleep(1)
            mms = client.messages \
                .create(
                    body=self.message_body,
                    media_url=[self.media_url],
                    status_callback=configuration[3],
                    from_=configuration[2],
                    to=self.mobile
            )
            self.response_message = mms
            # self.response = message.sid
        except TwilioRestException as e:
            raise UserError(e)

    def send_call(self):
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        try:
            time.sleep(1)
            call = client.calls.create(
                twiml='<Response><Say>' + self.message_body + '</Say></Response>',
                status_callback=configuration[3],
                from_=configuration[2],
                to=self.mobile,
                loop=2
            )
            self.response_call = call
            # self.response = message.sid
        except TwilioRestException as e:
            raise UserError(e)
