# -*- coding: utf-8 -*-

import time
import base64
from odoo import http
from twilio.rest import Client
from odoo import fields, http, _
from odoo.http import request, content_disposition
from twilio.base.exceptions import TwilioRestException


class PatientEngagement(http.Controller):

    @http.route('/patient_engagement/mor', auth="none", methods=['POST', 'GET'], csrf=False)
    def message_outgoing_response(self, **kw):
        type_ = "message_outgoing_response\n"
        template = ""
        for data in kw:
            template += str(data) + " -- " + str(kw[data]) + "\n"
        request.env['logs.log'].sudo().create({
            'type': type_,
            'log': template,
        })

        try:
            if kw.get('MessageSid', False) and kw.get('MessageStatus', False):
                twilio_message = request.env['messaging.history'].sudo().search(
                    [('message_sid', '=', kw['MessageSid'])])
                if twilio_message.id:
                    twilio_message.sudo().update({
                        'message_status': kw['MessageStatus'],
                    })
        except:
            return "Internal Server Error"

        # error = {
        #     'code': 200,
        #     'message': "Odoo Server Error",
        # }
        # return json.dumps(error)
        return ""

    @http.route('/patient_engagement/cor', auth="none", methods=['POST', 'GET'], csrf=False)
    def call_outgoing_response(self, **kw):
        type_ = "call_outgoing_response\n"
        template = ""
        for data in kw:
            template += str(data) + " -- " + str(kw[data]) + "\n"
        request.env['logs.log'].sudo().create({
            'type': type_,
            'log': template,
        })

        try:
            if kw.get('CallSid', False) and kw.get('CallStatus', False):
                twilio_message = request.env['messaging.history'].sudo().search([('voice_sid', '=', kw['CallSid'])])
                if twilio_message.id:
                    twilio_message.sudo().update({
                        'voice_status': kw['CallStatus'],
                    })
        except:
            return "Internal Server Error"

        return ""

    @http.route('/patient_engagement/mir', auth="none", methods=['POST', 'GET'], csrf=False)
    def message_incoming_response(self, **kw):
        type_ = "message_incoming_response\n"
        template = ""

        for data in kw:
            template += str(data) + " -- " + str(kw[data]) + "\n"
        request.env['logs.log'].sudo().create({
            'type': type_,
            'log': template,
        })

        try:
            if kw.get('From', False) and kw.get('Body', False) and kw.get('SmsSid', False) and kw.get('SmsStatus',
                                                                                                      False):
                user = request.env['res.partner'].sudo().search([('formatted_phone', '=', kw['From'])], limit=1)
                if user:
                    if kw['Body'].upper() == "STOP":
                        for communication_id in user.communication_ids:
                            communication_id.opt_out = True
                        # user.communication_ids.filtered(lambda r: r.communication == 'Appointment').opt_out = True
                    elif kw['Body'].upper() == "START":
                        for communication_id in user.communication_ids:
                            communication_id.opt_out = False
                            # user.communication_ids.filtered(lambda r: r.communication == 'Appointment').opt_out = False
                    elif kw['Body'].upper() in ["YES", "Y"]:
                        partner_ids = request.env['res.partner'].sudo().search([('formatted_phone', '=', kw['From'])])
                        if len(partner_ids.ids) > 0:
                            request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
                                [('patient_id', 'in', partner_ids.ids)],
                                order='start_datetime DESC', limit=1)
                    else:
                        messaging_history = request.env['messaging.history'].sudo().create({
                            'datetime_of_request': fields.datetime.today(),
                            'patient_id': user.id,
                            'company_id': user.company_id.id,
                            'message': "Incoming text message.",
                            'message_body': kw['Body'],
                            'message_sid': kw['SmsSid'],
                            'message_status': kw['SmsStatus'],
                            'received': True,
                            'is_chat': True,
                        })
                        request.env['bus.bus'].sendone((request._cr.dbname, 'res.partner', user.id),
                                                       {'type': 'twilio_notification_updated',
                                                        'message_received': True})
                        self.send_message(messaging_history)
        except Exception as e:
            return "Internal Server Error" + " ... " + str(e)
        return ""

    @http.route(['/two_way_chat/upload_document'], type='http', auth="user", csrf=False)
    def upload_document(self, **kw):
        if kw.get('image', False) != 'undefined' and kw.get('image', False):
            messaging_history_id = kw['messaging_history_id']
            messaging_history_id = int(messaging_history_id)
            if messaging_history_id:
                atts = request.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'messaging.history'),
                    ('res_field', '=', 'document'),
                    ('res_id', 'in', [messaging_history_id]),
                ])
                if atts:
                    atts.write({'datas': base64.b64encode(kw.get('image').read())})
                else:
                    atts.create([{
                        'name': 'document',
                        'res_model': 'messaging.history',
                        'res_field': 'document',
                        'res_id': messaging_history_id,
                        'type': 'binary',
                        'datas': base64.b64encode(kw.get('image').read()),
                    }])
            else:
                messaging_history_id = request.env['messaging.history'].sudo().create({
                    'datetime_of_request': fields.datetime.today(),
                    'is_chat': True,
                    'details': 'send via chat',
                }).id
                atts = request.env['ir.attachment'].sudo().create([{
                    'name': 'document',
                    'res_model': 'messaging.history',
                    'res_field': 'document',
                    'res_id': messaging_history_id,
                    'type': 'binary',
                    'datas': base64.b64encode(kw.get('image').read()),
                }])
            return str(messaging_history_id)
        return '0'

    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self, model, id, filename=None, **kw):
        atts = request.env['ir.attachment'].sudo().search([
            ('res_model', '=', model),
            ('res_field', '=', 'document'),
            ('res_id', 'in', [id]),
        ])
        filecontent = base64.b64decode(atts.datas)
        if not filecontent:
            return request.not_found()
        else:
            if not filename:
                filename = '%s_%s' % (model.replace('.', '_'), id)
                return request.make_response(filecontent,
                                             [('Content-Type', atts.mimetype),
                                              ('Content-Disposition', content_disposition(filename))])

    def send_message(self, messaging_history):
        pe_setting = request.env['pe.setting'].sudo().search([('company_id', '=', messaging_history.company_id.id)])
        week = {
            0: 'mo',
            1: 'tu',
            2: 'we',
            3: 'th',
            4: 'fr',
            5: 'sa',
            6: 'su',
        }
        if pe_setting.is_chat:
            if pe_setting.is_respond:
                timing = request.env['pe.setting.chat.schedule'].sudo().search(
                    [('day_select', '=', week[fields.datetime.today().weekday()]), ('setting_id', '=', pe_setting.id)])
                if timing.id:
                    if timing.opening_time and timing.closing_time and timing.opening_time.time() > fields.datetime.now().time() < timing.closing_time.time():
                        if pe_setting.is_respond:
                            message = pe_setting.auto_respond_message
                            configuration = request.env['messaging.history'].sudo().get_twilio_config()
                            account_sid = configuration[0]
                            auth_token = configuration[1]
                            client = Client(account_sid, auth_token)
                            log = self.env['messaging.history'].sudo().create({
                                'datetime_of_request': fields.datetime.today(),
                                'patient_id': messaging_history.patient_id.id,
                                'company_id': messaging_history.company_id.id,
                                'message': message,
                                'is_chat': True,
                                'details': 'send via auto respond',
                                'is_read': True,
                            })
                            try:
                                time.sleep(1)
                                response = client.messages.create(
                                    body=message,
                                    status_callback=configuration[3],
                                    from_=configuration[2],
                                    to=messaging_history.patient_id.formatted_phone
                                )
                                log.sudo().update({
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
