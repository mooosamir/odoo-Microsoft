# -*- coding: utf-8 -*-

import os
import time
import pytz
import base64
import operator
from typing import re
from dateutil import tz
from twilio.rest import Client
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from twilio.base.exceptions import TwilioRestException


class MessagingHistory (models.Model):
    _name = 'messaging.history'
    _description = 'Appointment Requests For Online Patients'
    _order = "create_date DESC"

    def _compute_method(self):
        for res in self:
            res.method = ''
            res.method = 'Text, ' if res.message_sid else ''
            res.method += 'Voice, ' if res.voice_sid else ''
            res.method += 'Email, ' if res.email else ''
            if len(res.method) > 1 and res.method[-2] == ',':
                res.method = res.method[:-2]

    def _compute_status(self):
        for res in self:
            res.status = ''
            res.status = 'Successful,' if res.message_status in ['in progress', 'sent', 'sending', 'queued', 'scheduled', 'accepted', 'delivered'] \
                                            else ('Failed,' if res.message_status in ['undelivered']
                                                else ('Error,' if res.message_status in ['failed', 'not send'] else ''))
            res.status += 'Successful,' if res.voice_status in ['queued', 'initiated', 'ringing', 'in-progress', 'completed'] \
                                            else ('Failed,' if res.voice_status in ['busy','no-answer']
                                                  else ('Error,' if res.voice_status in ['canceled', 'failed', 'not send'] else ''))
            res.status += 'Successful,' if res.email_status == 'sent' else ('Error,' if res.email_status == 'not send' else '')
            if len(res.status) > 0 and res.status[-1] == ',':
                res.status = res.status[:-1]

    received = fields.Boolean(default=False)
    is_chat = fields.Boolean(default=False)
    is_read = fields.Boolean(default=False)

    document = fields.Binary(attachment=True)

    datetime_of_request = fields.Datetime(string="DateTime")
    message_sid = fields.Char(string="Message sid")
    voice_sid = fields.Char(string="voice sid")
    email = fields.Char(string="Email")

    message_status = fields.Char(string="Message status")
    voice_status = fields.Char(string="Voice status")
    email_status = fields.Char(string="Email status")

    patient_id = fields.Many2one('res.partner', string="Patient")
    patient_phone = fields.Char(related='patient_id.formatted_phone', store=True)

    message = fields.Text(string="Message")
    message_body = fields.Text(string="Message")
    details = fields.Text(string="Details")
    condition = fields.Char(string="condition")

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    appointment_id = fields.Many2one('calendar.event', string="Appointment")
    spec_recall_type_line_id = fields.Many2one('spec.recall.type.line', string="Recall line")
    multi_order_type_id = fields.Many2one('multi.order.type', string="Multi Order Type")

    method = fields.Char(string="Method", compute='_compute_method')
    status = fields.Char(string="Status", compute='_compute_status')

    def systray_get_notifications(self):
        return self.search_count([('company_id', '=', self.env.company.id), ("message_sid", "!=", ""), ('is_chat', '=', True), ('is_read', '=', False)])

    def set_patient_archive(self, id):
        partner = self.env['res.partner'].browse(int(id))
        partner.update({
            'is_archived': True
        })
        return True

    def set_patient_un_archive(self, id):
        partner = self.env['res.partner'].browse(int(id))
        partner.update({
            'is_archived': False
        })
        return True

    def get_quick_response(self, company_id):
        result = []
        branch_setting = self.env['pe.setting'].search([('company_id', '=', int(company_id))])
        if branch_setting:
            if branch_setting.is_chat:
                for data in branch_setting.quick_response:
                    result.append({
                        'name': data.name,
                        'message': data.message,
                    })
        return result

    def unread(self, id):
        self.browse(int(id)).update({
            'is_read': False,
        })
        return self.browse(int(id)).is_read

    def get_branches(self):
        result = []
        branch = []
        # user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        company = self.env['res.company'].search([('id', 'in', self.env.user.company_ids.ids)])
        if company:
            # if user.branch_ids:
            for data in company:
                result.append({
                    'name': data.name,
                    'id': data.id,
                })
            if self.env.user.company_id.id:
                branch.append({
                    'branch': self.env.user.company_id.name,
                    'id': self.env.user.company_id.id,
                })
        return result, branch

    def set_branch(self, _id):
        user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if user:
            user.update({
                'company_id': int(_id),
            })
            return True
        return False

    def get_patient_box(self, archived, search, company_id, _id=0):
        result = []
        if _id == 0:
            if search != "":
                patients_list = self.read_group([("message_sid", "!=", ""), ('is_chat', '=', True), ('company_id', '=', int(company_id))],
                                                fields=['patient_id'], groupby=['patient_id'])
                ids = []
                for data in patients_list:
                    ids.append(data['patient_id'][0])
                patients_list = self.env['res.partner'].search([('id', 'in', ids), ('is_archived', '=', archived), ('company_id', '=', int(company_id)), '|', ('phone', 'ilike', search), ('name', 'ilike', search)])
                for data in patients_list:
                    patient = self.search(
                        [('patient_phone', '=', data.formatted_phone), ("message_sid", "!=", ""), ('is_chat', '=', True)],
                        order="create_date DESC", limit=1)
                    patient_name = self.env['res.partner'].search([('formatted_phone', '=', data.formatted_phone)],
                        order="name", limit=1)
                    unread = self.search_count(
                        [('patient_phone', '=', data.formatted_phone), ("message_sid", "!=", ""), ('is_chat', '=', True), ('is_read', '=', False)])

                    result.append({
                        'id': data.id,
                        'name': patient_name.name,
                        'mobile': data.phone,
                        'last_message': patient.message,
                        'is_archived': data.is_archived,
                        'unread': unread,
                    })
            else:
                patients_list = self.read_group([("message_sid", "!=", ""), ('is_chat', '=', True), ('company_id', '=', int(company_id))],
                                                fields=['patient_id'], groupby=['patient_id'])
                for data in patients_list:
                    _patient = self.env['res.partner'].search([('id', '=', data['patient_id'][0])],
                        order="name", limit=1)
                    patient = self.search(
                        [('patient_phone', '=', _patient.formatted_phone), ("message_sid", "!=", ""), ('is_chat', '=', True)],
                        order="create_date DESC", limit=1)
                    patient_name = self.env['res.partner'].search([('formatted_phone', '=', _patient.formatted_phone)],
                        order="name", limit=1)
                    unread = self.search_count(
                        [('patient_phone', '=', _patient.formatted_phone), ("message_sid", "!=", ""), ('is_chat', '=', True), ('is_read', '=', False)])
                    if self.env['res.partner'].browse(data['patient_id'][0]).is_archived == archived:
                        result.append({
                            'id': data['patient_id'][0],
                            'name': patient_name.name,
                            'mobile': patient.patient_id.phone,
                            'last_message': patient.message,
                            'is_archived': patient.patient_id.is_archived,
                            'unread': unread,
                        })
        if _id != 0:
            patients_list = self.env['res.partner'].search([('id', '=', int(_id))])
            unread = self.search_count(
                [('patient_phone', '=', patients_list.formatted_phone), ("message_sid", "!=", ""), ('is_chat', '=', True),
                 ('is_read', '=', False)])
            patient_name = self.env['res.partner'].search([('formatted_phone', '=', patients_list.formatted_phone)],
                                                          order="name", limit=1)
            result.append({
                'id': patients_list.id,
                'name': patient_name.name,
                'mobile': patients_list.phone,
                'last_message': "",
                'is_archived': patients_list.is_archived,
                'unread': unread,
            })

        return result

    def add_update_patient(self, company_id, search=""):
        patients_list = self.read_group([("message_sid", "!=", ""), ('is_chat', '=', True), ('company_id', '=', int(company_id))], fields=['patient_id'], groupby=['patient_id'])
        result = []
        records = []
        for data in patients_list:
            result.append(data['patient_id'][0])
        domain = [('id', 'not in', result)]
        if search != "":
            domain.append('|')
            domain.append(('date_of_birth', 'ilike', search))
            domain.append(('name', 'ilike', search))
            domain.append(('company_id', '=', int(company_id)))

        patients = self.env['res.partner'].search(domain)
        for data in patients:
            records.append({
                'id': data.id,
                'name': data.name,
                'date_of_birth': data.date_of_birth.strftime("%m/%d/%Y") if data.date_of_birth else 'N/A',
            })
        return records

    def get_chat_box(self, id):
        patient = self.env['res.partner'].search([('id', '=', int(id))])
        patients_list = self.search([('patient_phone', '=', patient.formatted_phone), ("message_sid", "!=", ""), ('is_chat', '=', True)], order="create_date")
        patient_name = self.env['res.partner'].search([('formatted_phone', '=', patient.formatted_phone)],
                                                      order="name", limit=1)
        result = []
        is_read_count = 0
        patient_list = {
            'name': patient_name.name,
            'mobile': patient.phone,
            'branch': patient.company_id.name
        }
        for data in patients_list:
            if not data.is_read:
                self.browse(data.id).update({
                    'is_read': True,
                })
                is_read_count = is_read_count + 1
            result.append({
                'name': data.patient_id.name,
                'message': data.message,
                'status': data.message_status,
                'received': data.received,
                'datetime': data.datetime_of_request,
                'read': data.is_read,
                'id': data.id,
            })

        return patient_list, result, is_read_count

    def get_twilio_config(self):
        twilio_account_sid = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_account_sid')]).value
        twilio_auth_token = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_auth_token')]).value
        twilio_from_number = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_from_number')]).value
        twilio_message_outgoing_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_message_outgoing_webhook')]).value
        twilio_call_outgoing_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_call_outgoing_webhook')]).value
        twilio_website_address = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_website_address')]).value

        return twilio_account_sid, twilio_auth_token, twilio_from_number, twilio_message_outgoing_webhook, twilio_call_outgoing_webhook, twilio_website_address \
            if twilio_account_sid and twilio_auth_token and twilio_from_number and twilio_message_outgoing_webhook and twilio_call_outgoing_webhook and twilio_website_address else None

    def send_message(self, id, message, messaging_history_id):
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        patient = self.env['res.partner'].search([('id', '=', int(id))])
        log = self.env['messaging.history']
        if messaging_history_id and messaging_history_id != '0':
            log = self.env['messaging.history'].browse(int(messaging_history_id))
            log.sudo().update({
                'datetime_of_request': fields.datetime.today(),
                'patient_id': patient.id,
                'company_id': patient.company_id.id,
                'message': 'send via chat',
                'message_body': message,
                'is_chat': True,
                'details': 'send via chat',
                'is_read': True,
            })
            try:
                time.sleep(1)
                response = client.messages.create(
                    body=message,
                    status_callback=configuration[3],
                    media_url=[configuration[5] + "/web/binary/download_document?model=messaging.history&id=" + str(log.id)],
                    from_=configuration[2],
                    to=patient.formatted_phone
                )
                log.update({
                    'message_sid': response.sid,
                    'message_status': response.status,
                })
            except TwilioRestException as e:
                type_ = "message error"
                self.env['logs.log'].sudo().create({
                    'type': type_,
                    'log': e,
                })
                log.update({
                    'message_sid': 0,
                    'message_status': 'not send',
                })
        else:
            log = self.env['messaging.history'].sudo().create({
                'datetime_of_request': fields.datetime.today(),
                'patient_id': patient.id,
                'company_id': patient.company_id.id,
                'message': 'send via chat',
                'message_body': message,
                'is_chat': True,
                'details': 'send via chat',
                'is_read': True,
            })
            try:
                time.sleep(1)
                response = client.messages.create(
                    body=message,
                    status_callback=configuration[3],
                    from_=configuration[2],
                    to=patient.formatted_phone
                )
                log.update({
                    'message_sid': response.sid,
                    'message_status': response.status,
                })
            except TwilioRestException as e:
                type_ = "message error"
                self.env['logs.log'].sudo().create({
                    'type': type_,
                    'log': e,
                })
                log.sudo().update({
                    'message_sid': 0,
                    'message_status': 'not send',
                })

        result = []
        patient_list = {
            'name': patient.name,
            'mobile': patient.phone,
            'branch': patient.company_id.name
        }
        result.append({
            'name': patient.name,
            'message': log.message,
            'status': log.message_status,
            'received': log.received,
            'datetime': log.datetime_of_request,
        })

        return patient_list, result
