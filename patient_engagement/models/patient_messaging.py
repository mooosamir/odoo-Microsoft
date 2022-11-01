# -*- coding: utf-8 -*-

import time
import lxml
import re
from twilio.rest import Client
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from twilio.base.exceptions import TwilioRestException

# Syntax of the data URL Scheme: https://tools.ietf.org/html/rfc2397#section-3
# Used to find inline images
image_re = re.compile(r"data:(image/[A-Za-z]+);base64,(.*)")


class AppointmentReminder(models.Model):
    _name = 'patient.messaging'
    _description = 'Sending notifications to patients.'
    _order = "create_date DESC"

    is_recall = fields.Boolean(string="Recall")
    is_no_show = fields.Boolean(string="No Show")
    is_thank_you = fields.Boolean(string="Thank You")
    is_overdue_recall = fields.Boolean(string="Overdue Recall")
    # is_glasses_order_ready = fields.Boolean(string="Glasses Order Ready")
    is_order_ready = fields.Boolean(string="Order Ready")
    is_contact_lens_reorder = fields.Boolean(string="Contact Lens Reorder")
    is_appointment_remainder = fields.Boolean(string="Appointment Reminder")
    is_contact_lens_order_ready = fields.Boolean(string="Contact Lens Order Ready")

    text_body = fields.Text(string="Text")
    text_length = fields.Integer(string="Text Length", compute="text_lengths")
    voice_body = fields.Text(string="Voice")
    # email_body = fields.Html(string="Email")
    email_body_arch = fields.Html(string='Body', translate=False)
    email_body_html = fields.Html(string='Body converted to be send by mail', sanitize_attributes=False)

    company_id = fields.Many2many('res.company', string="Company", default=lambda self: self.env.company, required=1)
    order_status = fields.Many2one('order.status')
    # Send By
    send_by_case_1 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Send By")
    send_by_case_2 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Send By")
    send_by_case_3 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Send By")
    send_by_case_4 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Send By")
    send_by_case_5 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Send By")
    # Backup
    backup_case_1 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Backup")
    backup_case_2 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Backup")
    backup_case_3 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Backup")
    backup_case_4 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Backup")
    backup_case_5 = fields.Selection([("Voice and Email", "Voice and Email"), ("Voice", "Voice"),
                                      ("Text and Email", "Text and Email"), ("Email", "Email"),
                                      ("Text", "Text")], default="Voice and Email", string="Backup")
    # Is Active
    is_active_case_1 = fields.Boolean(string="Schedule 1 - Active", default=1)
    is_active_case_2 = fields.Boolean(string="Schedule 2 - Active", default=1)
    is_active_case_3 = fields.Boolean(string="Schedule 3 - Active", default=1)
    is_active_case_4 = fields.Boolean(string="Schedule 4 - Active", default=1)
    is_active_case_5 = fields.Boolean(string="Schedule 5 - Active", default=1)

    def _convert_inline_images_to_urls(self, body_html):
        """
        Find inline base64 encoded images, make an attachement out of
        them and replace the inline image with an url to the attachement.
        """

        def _image_to_url(b64image: bytes):
            """Store an image in an attachement and returns an url"""
            attachment = self.env['ir.attachment'].create({
                'datas': b64image,
                'name': "cropped_image_mailing_{}".format(self.id),
                'type': 'binary',})

            attachment.generate_access_token()

            return '/web/image/%s?access_token=%s' % (
                attachment.id, attachment.access_token)

        modified = False
        root = lxml.html.fromstring(body_html)
        for node in root.iter('img'):
            match = image_re.match(node.attrib.get('src', ''))
            if match:
                mime = match.group(1)  # unsed
                image = match.group(2).encode()  # base64 image as bytes

                node.attrib['src'] = _image_to_url(image)
                modified = True

        if modified:
            return lxml.html.tostring(root)

        return body_html

    @api.model
    def create(self, values):
        if values.get('body_html'):
            values['email_body_html'] = self._convert_inline_images_to_urls(values['email_body_html'])
        return super(AppointmentReminder, self).create(values)

    def write(self, values):
        if values.get('body_html'):
            values['email_body_html'] = self._convert_inline_images_to_urls(values['email_body_html'])
        return super(AppointmentReminder, self).write(values)

    @api.onchange('text_body')
    def text_lengths(self):
        if self.text_body:
            self.text_length = len(self.text_body)
        else:
            self.text_length = 0

    def get_twilio_config(self):
        twilio_account_sid = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_account_sid')]).value
        twilio_auth_token = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_auth_token')]).value
        twilio_from_number = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_from_number')]).value
        twilio_message_outgoing_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_message_outgoing_webhook')]).value
        twilio_call_outgoing_webhook = self.env['ir.config_parameter'].sudo().search([('key', '=', 't_call_outgoing_webhook')]).value

        return twilio_account_sid, twilio_auth_token, twilio_from_number, twilio_message_outgoing_webhook, twilio_call_outgoing_webhook \
            if twilio_account_sid and twilio_auth_token and twilio_from_number and twilio_message_outgoing_webhook and twilio_call_outgoing_webhook else None

    def send_message(self, message_body, mobile, data, log):
        delivery_restrictions = self.env['pe.setting'].search([('company_id', '=', log.company_id.id)], limit=1)
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        stop_message = ""
        if log.condition == "is_appointment_remainder":
            stop_message = "Text STOP Optout"
        if delivery_restrictions.from_time.time() > fields.datetime.now().time() < delivery_restrictions.to_time.time() \
            or (delivery_restrictions.is_saturday and fields.datetime.now().weekday() == 5) \
                or (delivery_restrictions.is_sunday and fields.datetime.now().weekday() == 6) or\
                log.datetime_of_request > fields.datetime.today():
            log.update({
                'message_sid': 0,
                'message_status': 'to be send in future',
            })
            if log.condition == "is_recall" or log.condition == "is_overdue_recall":
                log.update({
                    'spec_recall_type_line_id': data,
                })
            elif log.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                log.update({
                    'multi_order_type_id': data,
                })
            else:
                log.update({
                    'appointment_id': data,
                })
        else:
            try:
                time.sleep(1)
                if log.condition == "is_recall" or log.condition == "is_overdue_recall":
                    data.patient_id = data.partner_id
                    body = message_body.format(patient_first_name=data.patient_id.first_name,
                                               patient_full_name=data.patient_id.name,
                                               recall_date=str(data.next_recall_date.strftime("%A, %B %d, %Y")),
                                               recall_name=data.name.name,
                                               company_phone=log.company_id.phone,
                                               company_name=log.company_id.name) + stop_message,
                    message = client.messages \
                        .create(
                            body=body,
                            status_callback=configuration[3],
                            from_=configuration[2],
                            to=mobile
                        )
                elif log.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                    data.patient_id = data.partner_id
                    body = message_body.format(patient_first_name=data.patient_id.first_name,
                                               patient_full_name=data.patient_id.name,
                                               name=data.display_name,
                                               company_phone=log.company_id.phone,
                                               company_name=log.company_id.name) + stop_message,
                    message = client.messages \
                        .create(
                            body=body,
                            status_callback=configuration[3],
                            from_=configuration[2],
                            to=mobile
                        )
                else:
                    body = message_body.format(patient_first_name=data.patient_id.first_name,
                                               patient_full_name=data.patient_id.name,
                                               appointment_date=str(data.start_datetime.date().strftime("%A, %B %d, %Y")),
                                               appointment_time=str(data.local_start_datetime.split(' ',1)[1][0:5]),
                                               company_phone=log.company_id.phone,
                                               company_name=log.company_id.name) + stop_message
                    message = client.messages \
                        .create(
                            body= body,
                            status_callback=configuration[3],
                            from_=configuration[2],
                            to=mobile
                        )
                log.update({
                    'message_body': body,
                    'message_sid': message.sid,
                    'message_status': message.status,
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

    def send_call(self, voice_body, mobile, data, log):
        delivery_restrictions = self.env['pe.setting'].search([('company_id', '=', log.company_id.id)], limit=1)
        configuration = self.get_twilio_config()
        account_sid = configuration[0]
        auth_token = configuration[1]
        client = Client(account_sid, auth_token)
        if delivery_restrictions.from_time.time() < fields.datetime.now().time() > delivery_restrictions.to_time.time() \
            or (delivery_restrictions.is_saturday and fields.datetime.now().weekday() == 5) \
                or (delivery_restrictions.is_sunday and fields.datetime.now().weekday() == 6):
            log.update({
                'voice_sid': 0,
                'voice_status': 'to be send in future',
            })
            if log.condition == "is_recall" or log.condition == "is_overdue_recall":
                log.update({
                    'spec_recall_type_line_id': data,
                })
            else:
                log.update({
                    'appointment_id': data,
                })
        else:
            try:
                time.sleep(1)
                if log.condition == "is_recall" or log.condition == "is_overdue_recall":
                    data.patient_id = data.partner_id
                    body = voice_body.format(patient_first_name=data.patient_id.first_name,
                                                                    patient_full_name=data.patient_id.name,
                                                                    recall_date=str(data.next_recall_date.strftime("%A, %B %d, %Y")),
                                                                    recall_name=data.name.name,
                                                                   company_phone=log.company_id.phone,
                                                                   company_name=log.company_id.name)
                    call = client.calls.create(
                        twiml='<Response><Say>' + body + '</Say></Response>',
                        status_callback=configuration[4],
                        from_=configuration[2],
                        to=mobile,
                    )
                elif log.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                    data.patient_id = data.partner_id
                    body = voice_body.format(patient_first_name=data.patient_id.first_name,
                                                                    patient_full_name=data.patient_id.name,
                                                                    name=data.display_name,
                                                                    company_phone=log.company_id.phone,
                                                                    company_name=log.company_id.name)
                    call = client.calls.create(
                        twiml='<Response><Say>' + body + '</Say></Response>',
                        status_callback=configuration[4],
                        from_=configuration[2],
                        to=mobile,
                    )
                else:
                    body = voice_body.format(patient_first_name=data.patient_id.first_name,
                                                                    patient_full_name=data.patient_id.name,
                                                                    appointment_date=str(data.start_datetime.date().strftime("%A, %B %d, %Y")),
                                                                    appointment_time=str(data.local_start_datetime.split(' ',1)[1][0:5]),
                                                                    company_phone=log.company_id.phone,
                                                                    company_name=log.company_id.name)
                    call = client.calls.create(
                        twiml='<Response><Say>' + body + '</Say></Response>',
                        status_callback=configuration[4],
                        from_=configuration[2],
                        to=mobile,
                    )
                log.update({
                    'voice_sid': call.sid,
                    'voice_status': call.status,
                    'message_body': body,
                })
            except TwilioRestException as e:
                type_ = "call error"
                self.env['logs.log'].sudo().create({
                    'type': type_,
                    'log': e,
                })
                log.update({
                    'voice_sid': 0,
                    'voice_status': 'not send',
                })

    def send_mail(self, email_body, email, data, log, name):
        delivery_restrictions = self.env['pe.setting'].search([('company_id', '=', log.company_id.id)], limit=1)
        template = self.env.ref('patient_engagement.patient_mail_template', False)
        template.subject = name
        if log.condition == "is_recall" or log.condition == "is_overdue_recall":
            data.patient_id = data.partner_id
            template.body_html = email_body.format(patient_first_name=data.patient_id.first_name,
                                                   patient_full_name=data.patient_id.name,
                                                   recall_date=str(data.next_recall_date.strftime("%A, %B %d, %Y")),
                                                   recall_name=data.name.name,
                                                   company_phone=log.company_id.phone,
                                                   company_name=log.company_id.name)
        elif log.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
            data.patient_id = data.partner_id
            template.body_html = email_body.format(patient_first_name=data.patient_id.first_name,
                                                   patient_full_name=data.patient_id.name,
                                                   name=data.display_name,
                                                   company_phone=log.company_id.phone,
                                                   company_name=log.company_id.name)
        else:
            template.body_html = email_body.format(patient_first_name=data.patient_id.first_name,
                                                   patient_full_name=data.patient_id.name,
                                                   appointment_date=str(data.start_datetime.date().strftime("%A, %B %d, %Y")),
                                                   appointment_time=str(data.local_start_datetime.split(' ',1)[1][0:5]),
                                                   company_phone=log.company_id.phone,
                                                   company_name=log.company_id.name)
        template.email_to = email
        log.update({
            'message_body': template.body_html,
        })
        # self.env['logs.log'].sudo().create({
        #     'type': "delivery.restrictions (Timezone Calculation)",
        #     'log': "delivery_restrictions.from_time : " + str(delivery_restrictions.from_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')) +
        #            "\nfields.datetime.now() : " + str(fields.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z%z')) +
        #             "\ndelivery_restrictions.to_time : " + str(delivery_restrictions.to_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')) +
        #             "\nServer Timezone : " + datetime.now(pytz.utc).astimezone().tzname(),
        # })
        if delivery_restrictions.from_time.time() < fields.datetime.now().time() > delivery_restrictions.to_time.time() \
            or (delivery_restrictions.is_saturday and fields.datetime.now().weekday() == 5) \
                or (delivery_restrictions.is_sunday and fields.datetime.now().weekday() == 6):
            log.update({
                'email': 0,
                'email_status': 'to be send in future',
            })
            if log.condition == "is_recall" or log.condition == "is_overdue_recall":
                log.update({
                    'spec_recall_type_line_id': data,
                })
            else:
                log.update({
                    'appointment_id': data,
                })
        else:
            try:
                template.send_mail(self.id, force_send=True)
                log.update({
                    'email': 1,
                    'email_status': 'sent',
                })
            except:
                log.update({
                    'email': 0,
                    'email_status': 'not send',
                })

    def send_past_notifications(self):
        company_id = self.env['res.company'].search([])
        for company in company_id:
            delivery_restrictions = self.env['pe.setting'].search([('company_id', '=', company.id)], limit=1)
            if delivery_restrictions.from_time and delivery_restrictions.to_time:
                if delivery_restrictions.from_time.time() < fields.datetime.now().time() > delivery_restrictions.to_time.time() \
                    or (delivery_restrictions.is_saturday and fields.datetime.now().weekday() == 5) \
                        or (delivery_restrictions.is_sunday and fields.datetime.now().weekday() == 6):
                    continue
                else:
                    messaging_history = self.env['messaging.history'].search(['|', '|', ('message_status', '=', 'to be send in future'),
                                                                              ('voice_status', '=', 'to be send in future'),
                                                                              ('email_status', '=', 'to be send in future'),
                                                                              ('company_id', '=', company.id),
                                                                              ])
                    for data in messaging_history:
                        appointment_remainder = self.env['patient.messaging'].search([
                            (data.condition, '=', True), ('company_id', '=', company.id)], limit=1)
                        if appointment_remainder:
                            if data.message_status == 'to be send in future':
                                phone = "+" + data.patient_id.formatted_phone
                                if data.condition == "is_recall" or data.condition == "is_overdue_recall":
                                    self.send_message(appointment_remainder.text_body, phone, data.spec_recall_type_line_id, data)
                                elif data.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                                    self.send_message(appointment_remainder.text_body, phone, data.multi_order_type_id, data)
                                else:
                                    self.send_message(appointment_remainder.text_body, phone, data.appointment_id, data)
                            if data.voice_status == 'to be send in future':
                                phone = "+" + data.patient_id.formatted_phone
                                if data.condition == "is_recall" or data.condition == "is_overdue_recall":
                                    self.send_call(appointment_remainder.voice_body, phone, data.spec_recall_type_line_id, data)
                                elif data.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                                    self.send_call(appointment_remainder.voice_body, phone, data.multi_order_type_id, data)
                                else:
                                    self.send_call(appointment_remainder.voice_body, phone, data.appointment_id, data)
                            if data.email_status == 'to be send in future':
                                if data.condition == "is_recall" or data.condition == "is_overdue_recall":
                                    self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data.spec_recall_type_line_id, data, data.message)
                                elif data.condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                                    self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data.multi_order_type_id, data, data.message)
                                else:
                                    self.send_mail(appointment_remainder.email_body_html, data.appointment_id.patient_id.email, data.appointment_id, data, data.message)

    def notifications_case_1(self, records, condition, name):
        for data in records:
            communication_id = 'Appointment'
            if condition == 'is_appointment_remainder':
                data.company_id = data.preferred_location_id
            if condition == 'is_order_status':
                communication_id = 'Order Pick-up'
                if "CL" in data.display_name:
                    condition = 'is_contact_lens_order_ready'
                    name = ' Contact Lens Order Ready'
                else:
                    condition = 'is_order_ready'
                data.patient_id = data.partner_id
                data.company_id = data.sale_order_id.company_id
            appointment_remainder = self.env['patient.messaging'].search([
                (condition, '=', True), ('company_id', 'in', data.company_id.ids)], limit=1)
            if appointment_remainder.id and condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                log = self.env['messaging.history'].create({
                    'patient_id': data.patient_id.id,
                    'message': name,
                    'condition': condition,
                    'company_id': data.company_id.id,
                    })
                log['datetime_of_request'] = fields.datetime.today() + relativedelta(days=3)
                self.notifications_case_2(data, condition, name, log)
                log = self.env['messaging.history'].create({
                    'patient_id': data.patient_id.id,
                    'message': name,
                    'condition': condition,
                    'company_id': data.company_id.id,
                })
                log['datetime_of_request'] = fields.datetime.today() + relativedelta(days=7)
                self.notifications_case_3(data, condition, name, log)
                log = self.env['messaging.history'].create({
                    'patient_id': data.patient_id.id,
                    'message': name,
                    'condition': condition,
                    'company_id': data.company_id.id,
                })
                log['datetime_of_request'] = fields.datetime.today() + relativedelta(days=12)
                self.notifications_case_4(data, condition, name, log)
            if appointment_remainder.is_active_case_1:
                if condition == "is_recall" or condition == "is_overdue_recall":
                    communication_id = 'Recall'
                    if not data.partner_id:
                        continue
                    data.patient_id = data.partner_id
                log = self.env['messaging.history'].create({
                    'datetime_of_request': fields.datetime.today(),
                    'patient_id': data.patient_id.id,
                    'message': name,
                    'condition': condition,
                    'company_id': data.patient_id.company_id.id,
                    })

                if appointment_remainder.send_by_case_1 == "Voice and Email":
                    if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).cell) and\
                            (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email):
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        log.update({'details': 'email opt out'})
                    elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                        log.update({'details': 'voice opt out'})
                    else:
                        log.update({'details': 'email and voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_1 == "Text and Email":
                    if condition == "is_appointment_remainder":
                        if (data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).opt_out) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'email and text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)
                    else:
                        if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).text) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_1 == "Voice":
                    if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                    else:
                        log.update({'details': 'voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_1 == "Email":
                    if data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,  log, name)
                    else:
                        log.update({'details': 'email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_1 == "Text":
                    if condition == "is_appointment_remainder":
                        if data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)
                    else:
                        if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_1, log, name, communication_id, condition)

    def notifications_case_2(self, records, condition, name, log=None):
        for data in records:
            communication_id = 'Appointment'
            # if condition == 'is_order_status':
            #     communication_id = 'Order Pick-up'
            #     if "CL" in data.display_name:
            #         condition = 'is_contact_lens_order_ready'
            #     else:
            #         condition = 'is_order_ready'
            if condition == 'is_appointment_remainder':
                data.company_id = data.preferred_location_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                communication_id = 'Order Pick-up'
                data.patient_id = data.partner_id
                data.company_id = data.sale_order_id.company_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                data.company_id = data.sale_order_id.company_id
            appointment_remainder = self.env['patient.messaging'].search([
                (condition, '=', True), ('company_id', 'in', data.company_id.ids)], limit=1)
            if appointment_remainder.is_active_case_2:
                if condition == "is_recall" or condition == "is_overdue_recall":
                    communication_id = 'Recall'
                    if not data.partner_id:
                        continue
                    data.patient_id = data.partner_id
                if log is None:
                    log = self.env['messaging.history'].create({
                        'datetime_of_request': fields.datetime.today(),
                        'patient_id': data.patient_id.id,
                        'message': name,
                        'condition': condition,
                        'company_id': data.patient_id.company_id.id,
                        })
                if appointment_remainder.send_by_case_2 == "Voice and Email":
                    if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).cell) and\
                            (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email):
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        log.update({'details': 'email opt out'})
                    elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                        log.update({'details': 'voice opt out'})
                    else:
                        log.update({'details': 'email and voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_2 == "Text and Email":
                    if condition == "is_appointment_remainder":
                        if (data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).opt_out) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)
                    else:
                        if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).text) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_2 == "Voice":
                    if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                    else:
                        log.update({'details': 'voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_2 == "Email":
                    if data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,  log, name)
                    else:
                        log.update({'details': 'email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_2 == "Text":
                    if condition == "is_appointment_remainder":
                        if data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)
                    else:
                        if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id).text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_2, log, name, communication_id, condition)

    def notifications_case_3(self, records, condition, name, log=None):
        for data in records:
            communication_id = 'Appointment'
            # if condition == 'is_order_status':
            #     communication_id = 'Order Pick-up'
            #     if "CL" in data.display_name:
            #         condition = 'is_contact_lens_order_ready'
            #     else:
            #         condition = 'is_order_ready'
            if condition == 'is_appointment_remainder':
                data.company_id = data.preferred_location_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                communication_id = 'Order Pick-up'
                data.patient_id = data.partner_id
                data.company_id = data.sale_order_id.company_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                data.company_id = data.sale_order_id.company_id
            appointment_remainder = self.env['patient.messaging'].search([
                (condition, '=', True), ('company_id', 'in', data.company_id.ids)], limit=1)
            if appointment_remainder.is_active_case_3:
                if condition == "is_recall" or condition == "is_overdue_recall":
                    communication_id = 'Recall'
                    if not data.partner_id:
                        continue
                    data.patient_id = data.partner_id
                if log is None:
                    log = self.env['messaging.history'].create({
                        'datetime_of_request': fields.datetime.today(),
                        'patient_id': data.patient_id.id,
                        'message': name,
                        'condition': condition,
                        'company_id': data.patient_id.company_id.id,
                        })
                if appointment_remainder.send_by_case_3 == "Voice and Email":
                    if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').cell) and\
                            (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email):
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        log.update({'details': 'email opt out'})
                    elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                        log.update({'details': 'voice opt out'})
                    else:
                        log.update({'details': 'voice and email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_3 == "Text and Email":
                    if condition == "is_appointment_remainder":
                        if (data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').opt_out) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)
                    else:
                        if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').text) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_3 == "Voice":
                    if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                    else:
                        log.update({'details': 'voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_3 == "Email":
                    if data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,  log, name)
                    else:
                        log.update({'details': 'email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_3 == "Text":
                    if condition == "is_appointment_remainder":
                        if data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)
                    else:
                        if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == 'Appointment').text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_3, log, name, communication_id, condition)

    def notifications_case_4(self, records, condition, name, log=None):
        for data in records:
            communication_id = 'Appointment'
            # if condition == 'is_order_status':
            #     communication_id = 'Order Pick-up'
            #     if "CL" in data.display_name:
            #         condition = 'is_contact_lens_order_ready'
            #     else:
            #         condition = 'is_order_ready'
            if condition == 'is_appointment_remainder':
                data.company_id = data.preferred_location_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                communication_id = 'Order Pick-up'
                data.patient_id = data.partner_id
                data.company_id = data.sale_order_id.company_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                data.company_id = data.sale_order_id.company_id
            appointment_remainder = self.env['patient.messaging'].search([
                (condition, '=', True), ('company_id', 'in', data.company_id.ids)], limit=1)
            if appointment_remainder.is_active_case_4:
                if condition == "is_recall" or condition == "is_overdue_recall":
                    communication_id = 'Recall'
                    if not data.partner_id:
                        continue
                    data.patient_id = data.partner_id
                if log is None:
                    log = self.env['messaging.history'].create({
                        'datetime_of_request': fields.datetime.today(),
                        'patient_id': data.patient_id.id,
                        'message': name,
                        'condition': condition,
                        'company_id': data.patient_id.company_id.id,
                        })
                if appointment_remainder.send_by_case_4 == "Voice and Email":
                    if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell) and\
                            (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        log.update({'details': 'email opt out'})
                    elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                        log.update({'details': 'voice opt out'})
                    else:
                        log.update({'details': 'voice and email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_4 == "Text and Email":
                    if condition == "is_appointment_remainder":
                        if (data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)
                    else:
                        if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_4 == "Voice":
                    if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                    else:
                        log.update({'details': 'voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_4 == "Email":
                    if data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,  log, name)
                    else:
                        log.update({'details': 'email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_4 == "Text":
                    if condition == "is_appointment_remainder":
                        if data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)
                    else:
                        if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_4, log, name, communication_id, condition)

    def notifications_case_5(self, records, condition, name, log=None):
        for data in records:
            communication_id = 'Appointment'
            # if condition == 'is_order_status':
            #     communication_id = 'Order Pick-up'
            #     if "CL" in data.display_name:
            #         condition = 'is_contact_lens_order_ready'
            #     else:
            #         condition = 'is_order_ready'
            if condition == 'is_appointment_remainder':
                data.company_id = data.preferred_location_id
            if condition in ['is_contact_lens_order_ready', 'is_order_ready']:
                communication_id = 'Order Pick-up'
                data.patient_id = data.partner_id
                data.company_id = data.sale_order_id.company_id
            appointment_remainder = self.env['patient.messaging'].search([
                (condition, '=', True), ('company_id', 'in', data.company_id.ids)], limit=1)
            if appointment_remainder.is_active_case_5:
                if condition == "is_recall" or condition == "is_overdue_recall":
                    communication_id = 'Recall'
                    if not data.partner_id:
                        continue
                    data.patient_id = data.partner_id
                if log is None:
                    log = self.env['messaging.history'].create({
                        'datetime_of_request': fields.datetime.today(),
                        'patient_id': data.patient_id.id,
                        'message': name,
                        'condition': condition,
                        'company_id': data.patient_id.company_id.id,
                        })
                if appointment_remainder.send_by_case_5 == "Voice and Email":
                    if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell) and\
                            (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                        log.update({'details': 'email opt out'})
                    elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                        log.update({'details': 'voice opt out'})
                    else:
                        log.update({'details': 'voice and email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)

                if appointment_remainder.send_by_case_5 == "Text and Email":
                    if condition == "is_appointment_remainder":
                        if (data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            log.update({'details': 'text and email opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)
                    else:
                        if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text) and\
                                (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data,log)
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,log, name)
                        elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                            log.update({'details': 'email opt out'})
                        elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                            self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                            log.update({'details': 'text opt out'})
                        else:
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)
                if appointment_remainder.send_by_case_5 == "Voice":
                    if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell:
                        phone = "+" + data.patient_id.formatted_phone
                        self.send_call(appointment_remainder.voice_body, phone, data, log)
                    else:
                        log.update({'details': 'voice opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)

                if appointment_remainder.send_by_case_5 == "Email":
                    if data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                        self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data,  log, name)
                    else:
                        log.update({'details': 'email opt out'})
                        self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)

                if appointment_remainder.send_by_case_5 == "Text":
                    if condition == "is_appointment_remainder":
                        if data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)
                    else:
                        if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text:
                            phone = "+" + data.patient_id.formatted_phone
                            self.send_message(appointment_remainder.text_body, phone, data, log)
                        else:
                            log.update({'details': 'text opt out'})
                            self.backup_send(data, appointment_remainder, appointment_remainder.backup_case_5, log, name, communication_id, condition)

    def backup_send(self, data, appointment_remainder, appointment_remainder_backup_case, log, name, communication_id, condition):
        log = self.env['messaging.history'].create({
            'datetime_of_request': fields.datetime.today(),
            'patient_id': data.patient_id.id,
            'message': "Backup method - " + name,
            'condition': condition,
            'company_id': data.patient_id.company_id.id,
        })
        if appointment_remainder_backup_case == "Voice and Email":
            if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell) and \
                    (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                phone = "+" + data.patient_id.formatted_phone
                self.send_call(appointment_remainder.voice_body, phone, data, log)
                self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
            elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell:
                phone = "+" + data.patient_id.formatted_phone
                self.send_call(appointment_remainder.voice_body, phone, data, log)
                log.update({'details': 'email opt out'})
            elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                log.update({'details': 'voice opt out'})
            else:
                log.update({'details': 'voice and email opt out'})

        if appointment_remainder_backup_case == "Text and Email":
            if condition == "is_appointment_remainder":
                if (data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out) and \
                        (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                    phone = "+" + data.patient_id.formatted_phone
                    self.send_message(appointment_remainder.text_body, phone, data, log)
                    self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                elif data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out:
                    phone = "+" + data.patient_id.formatted_phone
                    self.send_message(appointment_remainder.text_body, phone, data, log)
                    log.update({'details': 'email opt out'})
                elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                    self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    log.update({'details': 'text opt out'})
                else:
                    log.update({'details': 'text and email opt out'})
            else:
                if (data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text) and \
                        (data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email):
                    phone = "+" + data.patient_id.formatted_phone
                    self.send_message(appointment_remainder.text_body, phone, data, log)
                    self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                elif data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text:
                    phone = "+" + data.patient_id.formatted_phone
                    self.send_message(appointment_remainder.text_body, phone, data, log)
                    log.update({'details': 'email opt out'})
                elif data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                    self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
                    log.update({'details': 'text opt out'})
                else:
                    log.update({'details': 'text and email opt out'})

        if appointment_remainder_backup_case == "Voice":
            if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].cell:
                phone = "+" + data.patient_id.formatted_phone
                self.send_call(appointment_remainder.voice_body, phone, data, log)
            else:
                log.update({'details': 'voice opt out'})

        if appointment_remainder_backup_case == "Email":
            if data.patient_id.email and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].email:
                self.send_mail(appointment_remainder.email_body_html, data.patient_id.email, data, log, name)
            else:
                log.update({'details': 'email opt out'})

        if appointment_remainder_backup_case == "Text":
            if condition == "is_appointment_remainder":
                if data.patient_id.formatted_phone and not data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].opt_out:
                    phone = "+" + data.patient_id.formatted_phone
                    self.send_message(appointment_remainder.text_body, phone, data, log)
                else:
                    log.update({'details': 'text opt out'})
            else:
                if data.patient_id.formatted_phone and len(data.patient_id.communication_ids) > 0 and data.patient_id.communication_ids.filtered(lambda r: r.communication == communication_id)[0].text:
                    phone = "+" + data.patient_id.formatted_phone
                    self.send_message(appointment_remainder.text_body, phone, data, log)
                else:
                    log.update({'details': 'text opt out'})
