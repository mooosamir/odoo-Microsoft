import base64

import werkzeug
from dateutil.relativedelta import relativedelta
from requests_unixsocket import request

from odoo import http, fields
from datetime import datetime
from odoo.http import request
from odoo.http import request, content_disposition
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import json


class PatientPortal(http.Controller):
    @http.route('/my/', website=True, auth='user')
    def default_homepage_redirect(self):
        return request.redirect('/patient_portal')

    @http.route('/patient_portal/', website=True, auth='user')
    def patient_portal(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        current_user = request.env['res.partner'].sudo().search([('id', '=', res.partner_id.id)])
        appointments = request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
            [('patient_id', '=', res.partner_id.id),
             ('start_datetime', '>', fields.Datetime.now())])
        # shop_res = request.env['pos.order'].sudo().search([('partner_id', '=', res.partner_id.id)])
        user_message = request.env['mail.message'].sudo().search(
            [('channel_ids.channel_partner_ids', 'in', res.partner_id.id), ('author_id', '!=', res.partner_id.id),
             ('author_id', '!=', 2), ('message_type', '=', 'comment'), ('is_delete', '=', False)],
            order="write_date DESC")
        sale_order_line_read_group = request.env['sale.order.line'].sudo().read_group(
            [('order_partner_id', '=', request.env.user.partner_id.id), ('order_id', '!=', None)], fields=['id'],
            groupby=['order_id'], limit=4)
        if len(sale_order_line_read_group) != 0:
            sale_order_id = request.env['sale.order'].sudo().browse(
                [x['order_id'][0] for x in sale_order_line_read_group])
            # sale_order_id = request.env['sale.order'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)],
            #                                                         order="write_date DESC", limit=1)
            order_lines = sale_order_id.order_line.filtered(lambda line: line.display_type == 'line_section')
        else:
            order_lines = []
        channels = request.env['mail.channel'].sudo().search([('channel_partner_ids', 'in', res.partner_id.id)],
                                                             limit=9)
        updated_channels = channels.filtered(lambda r: r.message_unread and r.message_unread_counter > 0)
        # appointments = []
        # for app in app_res:
        #     appointments.append(app)
        values = {'appointments': appointments,
                  'order': sale_order_id.ids,
                  'order_lines': order_lines,
                  'current_user': current_user,
                  'fields': fields,
                  'datetime': datetime,
                  'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,
                  'message': user_message,
                  'channels': updated_channels,
                  'len': len,
                  'type': type,
                  }

        return request.render('patient_portal.patient_portal_template', values)

    @http.route('/patient_portal/prescription', website=True, auth='user')
    def prescription(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        current_user = request.env['res.partner'].sudo().search([('id', '=', res.partner_id.id)])
        prescriptions = []
        for prescription in current_user.contact_lens_ids:
            if not prescription.expiration_date or prescription.expiration_date >= fields.datetime.now().date():
                prescriptions.append(prescription)
        return request.render('patient_portal.prescription_template',
                              {'current_user': current_user, 'prescriptions': prescriptions})

    @http.route('/patient_portal/appointments', website=True, auth='user')
    def appointment(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        current_user = request.env['res.partner'].sudo().search([('id', '=', res.partner_id.id)])
        upcoming_appointments = request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
            [('patient_id', '=', res.partner_id.id), ('start_datetime', '>', fields.Datetime.now())])
        past_appointments = request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
            [('patient_id', '=', res.partner_id.id), ('start_datetime', '<', fields.Datetime.now()),
             ('start_datetime', '>', fields.Datetime.now() + relativedelta(months=-12))])

        return request.render('patient_portal.appointment_template',
                              {'current_user': current_user,
                               'upcoming_appointments': upcoming_appointments,
                               'past_appointments': past_appointments,
                               'type': type,
                               'fields': fields,
                               'datetime': datetime,
                               'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,
                               })

    @http.route('/patient_portal/orders', website=True, auth='user')
    def order(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        current_user = request.env['res.partner'].sudo().search([('id', '=', res.partner_id.id)])

        return request.render('patient_portal.appointment_template',
                              {'current_user': current_user, 'type': type})

    @http.route('/patient_portal/prescription/view_report', methods=['POST', 'GET'], csrf=False, cors='*', type='http',
                auth="user", website=True)
    def print_report(self, id, **kw):

        report_template_id = request.env.ref(
            'patient_profile_revisions.action_prescription_report').sudo().render_qweb_pdf(int(id))
        filecontent = report_template_id[0]
        if not filecontent:
            return request.not_found()
        else:
            filename = '%s_%s.pdf' % ('spec.contact.lenses'.replace('.', '_'), id)
            return request.make_response(filecontent,
                                         [('Content-Type', 'application/x-pdf'),
                                          ('Content-Disposition', content_disposition(filename))])

    @http.route('/patient_portal/message', website=True, auth='user')
    def message(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        current_user = request.env['res.partner'].sudo().search([('id', '=', res.partner_id.id)])
        user_message = request.env['mail.message'].sudo().search([('author_id', '=', res.partner_id.id)],
                                                                 order="write_date")

        return request.render('patient_portal.message_template', {'current_user': current_user})

    @http.route('/patient_portal/message/inbox/seen', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def message_seen(self, partner_id, channel_id, message_id):
        if int(channel_id) and int(partner_id) and int(message_id):
            channel_partner_id = request.env['mail.channel.partner'].sudo().search(
                [('partner_id', '=', int(partner_id)),
                 ('channel_id', '=', int(channel_id))])
            seen_message_id = channel_partner_id.seen_message_id.id

            if seen_message_id < int(message_id):
                channel_partner_id.sudo().update({
                    'seen_message_id': int(message_id)
                })
        return "1"

    @http.route('/patient_portal/message/inbox', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def message_inbox(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        user_message = request.env['mail.message'].sudo().search(
            [('channel_ids.channel_partner_ids', 'in', res.partner_id.id), ('author_id', '!=', res.partner_id.id),
             ('author_id', '!=', 2), ('message_type', '=', 'comment'), ('is_delete', '=', False)],
            order="write_date DESC")

        return request.render('patient_portal.inbox_template',
                              {'messages': user_message,
                               'request': request,
                               'json': json}
                              )

    @http.route('/patient_portal/message/trash', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def message_trash(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        user_id = res.partner_id.id
        user_message = request.env['mail.message'].sudo().search(
            [('is_delete', '=', True), ('message_type', '=', 'comment')],
            order="write_date DESC")
        sent_message = []
        inbox_message = []

        for message in user_message:
            if message.author_id.id != res.partner_id.id:
                inbox_message.append(message)
            elif message.author_id.id == res.partner_id.id:
                sent_message.append(message)

        return request.render('patient_portal.trash_template',
                              {'messages': user_message, 'json': json, 'user_id': user_id})

    @http.route('/patient_portal/message/new_message', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def new_message(self, id):
        id = int(id)
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        user_message = request.env['mail.message'].sudo().search(
            [('channel_ids.channel_partner_ids', 'in', res.partner_id.id), ('author_id', '!=', res.partner_id.id),
             ('author_id', '!=', 2), ('message_type', '=', 'comment')], order="write_date DESC")

        if id:
            providers = request.env['hr.employee'].sudo().search([('user_partner_id', '=', id)])
            if not providers.id:
                return "0"

        else:
            providers = request.env['hr.employee'].sudo().search([('user_partner_id', '!=', False)])

        return request.render('patient_portal.new_message_template',
                              {'messages': user_message, 'json': json, 'drs': providers, 'id': int(id)})

    @http.route('/patient_portal/message/email_sent', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def sent_message_btn(self, id, to, subject, message, to_partner_id):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        to_partner_id = request.env['res.partner'].browse(int(to_partner_id))
        user_id = res.partner_id.id
        channel_id = request.env['mail.channel'].sudo().search([
            ('name', 'in', [to + "," + res.partner_id.name, res.partner_id.name + "," + to])], order="write_date DESC",
            limit=1)
        # ('channel_type', '=', 'chat')])
        # for channel_i in channel_id:
        #     channel_i.unlink()
        channel = channel_id
        if not channel_id.id:
            channel = request.env['mail.channel'].sudo().create({
                'name': to + "," + res.partner_id.name,
                'channel_partner_ids': [(4, to_partner_id.id), (4, res.partner_id.id)],
                # 'public': 'private',
                # 'channel_type': 'chat',
                # 'email_send': False,
            })

        message = request.env['mail.message'].sudo().create({
            'author_id': user_id,
            'message_type': 'comment',
            'is_delete': False,
            'create_uid': uid,
            'body': message,
            'subject': subject,
            'description': message,
            'date': fields.Datetime.now(),
            'create_date': fields.datetime.now(),
            'display_name': to + ", " + res.partner_id.name,
            'email_from': res.partner_id.name + " " + res.partner_id.email,
            'write_uid': uid,
            'write_date': fields.datetime.now(),
            'channel_ids': [(4, channel.id)]
        })
        # notif_create_values = [{
        #     'mail_message_id': message.id,
        #     'res_partner_id': to_partner_id.id,
        #     'notification_type': 'inbox',
        #     'notification_status': 'sent',
        # }]
        # self.env['mail.notification'].sudo().create(notif_create_values)
        request.env['bus.bus'].sendone((request._cr.dbname, 'res.partner', to_partner_id.id), {
            'body': "<span class='o_mail_notification'>" + message.body + "</span>",
            'channel_ids': [channel.id],
            'info': 'transient_message',
        })
        return

    @http.route('/patient_portal/message/sent', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def message_sent(self):
        uid = http.request.uid
        res = request.env['res.users'].sudo().browse(uid)
        user_message = request.env['mail.message'].sudo().search(
            [('channel_ids.channel_partner_ids', 'in', res.partner_id.id), ('author_id', '=', res.partner_id.id),
             ('message_type', '=', 'comment'), ('is_delete', '=', False)], order="write_date DESC")

        return request.render('patient_portal.sent_template', {'messages': user_message, 'json': json})

    @http.route('/patient_portal/message/get-id', website=True, auth='user', methods=['POST', 'GET'], csrf=False,
                cors='*')
    def get_id(self, id):
        user_message = request.env['mail.message'].sudo().search([('id', '=', int(id))])
        if not user_message.id:
            return False
        user_message.sudo().update({'is_delete': True})

        return 'True'

    @http.route('/patient_portal/forms', website=True, auth='user')
    def forms(self):
        appointment_id = request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
            [('patient_id', '=', request.env.user.partner_id.id),
             ('start_datetime', '<=', fields.Datetime.now() + relativedelta(days=30)),
             ('is_intake_submitted', '=', False)])
        forms_list = len(appointment_id)
        if len(appointment_id):
            appointment_id = appointment_id[0]

        appointment_selection_id = appointment_id.service_type
        setting_id = request.env['pe.setting'].sudo().search([('company_id', '=', request.env.company.id)])
        form_id = request.env['pe.setting.form'].sudo().search([('setting_id', '=', setting_id.id),
                                                                ('appointment_selection_id', '=',
                                                                 appointment_selection_id.id)],
                                                               limit=1)
        form_selection_ids = form_id.form_selection_ids.sorted(key=lambda m: m.sequence)
        acs_consent_forms = []
        if appointment_id.id:
            for data in form_selection_ids:
                if data.ir_model_id.model == 'acs.consent.form.template':
                    for templates in data.acs_consent_form_template_ids:
                        acs_consent_form_id = request.env['acs.consent.form'].sudo().search([
                            ('partner_id', '=', request.env.user.partner_id.id),
                            ('user_id', '=', request.env.user.id),
                            ('company_id', '=', appointment_id.preferred_location_id.id),
                            ('appointment_id', '=', appointment_id.id),
                            ('template_id', '=', templates.id),
                        ])
                        if not acs_consent_form_id:
                            acs_consent_form_id = request.env['acs.consent.form'].sudo().create({
                                'name': templates.name,
                                'subject': templates.name,
                                'partner_id': request.env.user.partner_id.id,
                                'user_id': request.env.user.id,
                                'company_id': appointment_id.preferred_location_id.id,
                                'date': fields.datetime.now(),
                                'template_id': templates.id,
                                'appointment_id': appointment_id.id,
                            })
                        acs_consent_forms.append(acs_consent_form_id.id)

        acs_consent_form_ids = request.env['acs.consent.form'].sudo().search([('id', 'in', acs_consent_forms)])
        forms = {a.ir_model_id.model.replace('.', '_'): '' for a in form_selection_ids}
        if None in forms:
            del forms[None]
        values = {
            'forms_list': forms_list,
            'appointment_id': appointment_id,
            'form_id': form_id,
            'form_selection_ids': form_selection_ids,
            'forms': forms,
            'request': request,
            'len': len,
            'json': json,
            'acs_consent_forms': acs_consent_form_ids
        }
        return request.render('patient_portal.intake_form_template', values)

    @http.route('/patient_portal/forms/body/return', website=True, auth='user', csrf=False, cors='*')
    def intake_response(self, appointment_id, **kwargs):
        try:
            records = {}
            for data in kwargs:
                if not data[0:data.rfind('~')] in records:
                    records[data[0:data.rfind('~')]] = {}
                if not data[data.rfind('~') + 1:data.rfind('___')] in records[data[0:data.rfind('~')]]:
                    records[data[0:data.rfind('~')]][data[data.rfind('~') + 1:data.rfind('___')]] = {}
                if str(type(kwargs[data])) == "<class 'werkzeug.datastructures.FileStorage'>":
                    records[data[0:data.rfind('~')]][data[data.rfind('~') + 1:data.rfind('___')]][
                        data[data.rfind('___') + 3:]] = base64.b64encode(kwargs[data].stream.read())
                else:
                    records[data[0:data.rfind('~')]][data[data.rfind('~') + 1:data.rfind('___')]][
                        data[data.rfind('___') + 3:]] = kwargs[data]
                print(data[0:data.rfind('~')], data[data.rfind('~') + 1:data.rfind('___')],
                      data[data.rfind('___') + 3:],
                      kwargs[data])

            for data in records:
                if data == 'res.partner':
                    request.env[data].sudo().browse(request.env.user.partner_id.id) \
                        .sudo().update(records[data][''])
                elif data == 'spec.insurance':
                    for more_records in records[data]:
                        if more_records.lower() == 'vision':
                            records[data][more_records]['insurance_type'] = 'vision'
                        else:
                            records[data][more_records]['insurance_type'] = 'medical'
                        records[data][more_records]['partner_id'] = request.env.user.partner_id.id
                        request.env[data].sudo().create(records[data][more_records])
                else:
                    request.env[data].sudo().create(records[data][''])
            request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
                [('id', '=', int(appointment_id))]).update(
                {'is_intake_submitted': True})
            return '/patient_portal'
        except:
            return '0'

    @http.route('/patient_portal/orders', website=True, auth='user')
    def orders(self):
        return "this is orders page"

    @http.route('/patient_portal/shop', website=True, auth='user')
    def shop(self):
        return "this is shops"

    @http.route('/patient_portal/appointment/confirm_appointment', website=True, auth='user', methods=['POST', 'GET'],
                csrf=False, cors='*')
    def confirm_appointment(self, id):
        appointment = request.env['calendar.event'].sudo().with_context(virtual_id=False).browse((int(id)))
        if appointment.id:
            appointment.update({'confirmation_status': 'confirmed'})
            return 'Appointment Confirmed.'
        else:
            return 'No Appointment found to confirm.'
