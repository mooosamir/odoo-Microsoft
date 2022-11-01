# -*- coding: utf-8 -*-

import time
from twilio.rest import Client
from odoo import fields, models
from twilio.base.exceptions import TwilioRestException


class ContactPatientWizard(models.TransientModel):
    _name = 'contact.patient.wizard'
    _order = "create_date DESC"

    patient_id = fields.Many2one('res.partner', string="Patient Name", required=True)
    patient_mobile = fields.Char(string="Mobile")
    text_body = fields.Text(string="Text")

    def get_twilio_config(self):
        twilio_account_sid = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_account_sid')]).value
        twilio_auth_token = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_auth_token')]).value
        twilio_from_number = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_from_number')]).value
        twilio_message_outgoing_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_message_outgoing_webhook')]).value
        twilio_call_outgoing_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_call_outgoing_webhook')]).value

        return twilio_account_sid, twilio_auth_token, twilio_from_number, twilio_message_outgoing_webhook, twilio_call_outgoing_webhook \
            if twilio_account_sid and twilio_auth_token and twilio_from_number and twilio_message_outgoing_webhook and twilio_call_outgoing_webhook else None

    def send_message(self):
        log = self.env['messaging.history'].create({
            'datetime_of_request': fields.datetime.today(),
            'patient_id': self.patient_id.id,
            'message': "Contact Patient",
            'company_id': self.patient_id.company_id.id,
        })
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        try:
            time.sleep(1)
            message = client.messages \
                .create(
                    body=self.text_body,
                    status_callback=configuration[3],
                    from_=configuration[2],
                    to=self.patient_mobile
                )
            log.update({
                'message_sid': message.sid,
                'message_status': message.status,
            })
        except TwilioRestException as e:
            type_ = "contact patient error"
            self.env['logs.log'].sudo().create({
                'type': type_,
                'log': e,
            })
            log.update({
                'message_sid': 0,
                'message_status': 'not send',
            })


