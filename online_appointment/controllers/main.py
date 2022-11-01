# -*- coding: utf-8 -*-

import math
import json
import html
from odoo import fields, http, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ...opt_custom import models as timestamp_UTC
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class OnlineAppointment(http.Controller):

    def sitemap_event(env, rule, qs):
        if not qs or qs.lower() in '/online_appointment':
            yield {'loc': '/online_appointment'}

    @http.route(['/online_appointment'], type='http', auth="public", website=True)
    def online_appointment(self, **post):
        today = fields.date.today()

        branch_ids = request.env['res.company'].sudo().search([])
        # week_timings = request.env['appointments.open.close']
        # if post.get('branch', False):
        #     appointments_hours = request.env['appointments.hours'].sudo().search([('branch_id', '=', int(post['branch']))])
        #     if appointments_hours:
        #         week_timings = appointments_hours.appointments_close_open_ids

        values = {
            'today': today,
        }
        return request.env['ir.ui.view'].render_template("online_appointment.online_scheduling_locations", values)

    @http.route(['/online_appointment/markers_search_based'], type='http', auth="public", website=True, cors='*',
                csrf=False)
    def online_appointment_markers_search_based(self, **post):
        branches = request.env['res.company']
        zip_code = post.get('postal_code', False)
        city = post.get('locality', False)
        state = post.get('region', False)
        country = post.get('country_name', False)
        if zip_code and zip_code != '':
            zip_code = html.unescape(post.get('postal_code', False))
            branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.zip in str(zip_code))
        elif city and city != '':
            city = html.unescape(post.get('locality', False))
            branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.city.lower() in city.lower())

        elif state and state != '':
            state = html.unescape(post.get('region', False))
            state_id = request.env['res.country.state'].sudo().search([('name', '=ilike', state)])
            if state_id:
                branches = request.env['res.company'].sudo().search([('state_id', '=', state_id.id), ('lat', '!=', 0), ('lng', '!=', 0)])
            else:
                branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.city.lower() in state.lower())

        elif country and country != '':
            country = html.unescape(post.get('country_name', False))
            state_id = request.env['res.country.state'].sudo().search([('name', '=ilike', country)])
            if state_id:
                branches = request.env['res.company'].sudo().search([('state_id', '=', state_id.id), ('lat', '!=', 0), ('lng', '!=', 0)])
            else:
                branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.country_id.name.lower() in country.lower())

        result = []
        for data in branches:
            result += [[{'lat': float(data.lat), 'lng': float(data.lng)}, data.id]]
        return json.dumps(result)

    @http.route(['/online_appointment/markers_location_based'], type='http', auth="public", website=True, cors='*',
                csrf=False)
    def online_appointment_markers_location_based(self, **post):
        search_results = []
        for key, value in post.items():
            search_results.append(html.unescape(value))
        branches = request.env['res.company']
        for keys in search_results:
            branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.zip in str(keys))
            if branches.ids != []:
                branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.city.lower() in keys.lower())
                if branches.ids != []:
                    state_id = request.env['res.country.state'].sudo().search([('name', '=ilike', keys)])
                    if state_id:
                        branches = request.env['res.company'].sudo().search([('state_id', '=', state_id.id), ('lat', '!=', 0), ('lng', '!=', 0)])
            if branches.ids != []:
                break
        result = []
        for data in branches:
            result += [[{'lat': float(data.lat), 'lng': float(data.lng)}, data.id]]
        return json.dumps(result)

    @http.route(['/online_appointment/branches_show'], type='http', auth="public", website=True, cors='*', csrf=False)
    def online_appointment_branches_show(self, **post):
        branches = request.env['res.company']
        zip_code = post.get('postal_code', False)
        city = post.get('locality', False)
        state = post.get('region', False)
        country = post.get('country_name', False)
        if zip_code and zip_code != '':
            zip_code = html.unescape(post.get('postal_code', False))
            branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.zip in str(zip_code))

        elif city and city != '':
            city = html.unescape(post.get('locality', False))
            branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.city.lower() in country.lower())
        elif state and state != '':
            state = html.unescape(post.get('region', False))
            state_id = request.env['res.country.state'].sudo().search([('name', '=ilike', state)])
            if state_id.id:
                branches = request.env['res.company'].sudo().search([('state_id', '=', state_id.id), ('lat', '!=', 0), ('lng', '!=', 0)])
            else:
                branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.country_id.name.lower() in country.lower() or x.city.lower() in country.lower())
        elif country and country != '':
            country = html.unescape(post.get('country_name', False))
            state_id = request.env['res.country.state'].sudo().search([('name', '=ilike', country)])
            if state_id.id:
                branches = request.env['res.company'].sudo().search([('state_id', '=', state_id.id), ('lat', '!=', 0), ('lng', '!=', 0)])
            else:
                branches = request.env['res.company'].sudo().search([('lat', '!=', 0), ('lng', '!=', 0)]).filtered(lambda x: x.country_id.name.lower() in country.lower())

        result = {}
        json_results = json.loads(post['rows'])
        i = 0
        for data in branches:
            result[i] = {'branch': data}
            i = i + 1
        i = 0
        for data in json_results:
            if data['status'] == 'OK':
                result[i]['distance'] = data['distance']['text']
                result[i]['duration'] = data['duration']['text']
                result[i]['duration_in_traffic'] = data['duration_in_traffic']['text']
            else:
                result[i]['distance'] = 'N/A'
                result[i]['duration'] = 'N/A'
                result[i]['duration_in_traffic'] = 'N/A'
            i = i + 1

        results = {}
        for a, b in sorted(result.items(), key=lambda x: x[1]['distance']):
            results[a] = b
        return request.env['ir.ui.view'].render_template("online_appointment.branches", {'branch_ids': results})

    @http.route(['/online_appointment/location'], type='http', auth="public", website=True)
    def online_appointment_location(self, **post):
        today = fields.date.today()
        branch_location = False
        insurance_companies = request.env['res.partner'].sudo().search(
            [('is_company', '=', True), ('is_insurance', '=', True)])
        week_timings = request.env['appointments.open.close']
        online_services = request.env['pe.setting.services']
        doctor_domain = []
        selected_doctor = 0
        if post.get('doctor', False):
            selected_doctor = int(post['doctor'])
            # doctor_domain = [('id', '=', int(post['doctor']))]
        doctors = request.env['pe.setting.provider'].sudo().search(doctor_domain)
        if not post.get('branch', False):
            post['branch'] = 2
        if post.get('branch', False):
            branch_id = request.env['res.company'].sudo().search([('id', '=', int(post['branch']))])
            appointments_hours = request.env['appointments.hours'].sudo().search(
                [('company_id', '=', int(post['branch']))])
            if appointments_hours:
                week_timings = appointments_hours.appointments_close_open_ids
            if branch_id:
                pe_setting = request.env['pe.setting'].sudo().search([('company_id', '=', branch_id.id)])
                if pe_setting:
                    online_services = request.env['pe.setting.services'].sudo().search(
                        [('setting_id', '=', pe_setting.id), ('show_online', '=', True)])
                    doctor_domain.append(('setting_id', '=', pe_setting.id))
                    doctor_domain.append(('show_online', '=', True))
                    doctors = request.env['pe.setting.provider'].sudo().search(doctor_domain, order='sequence')

        values = {
            'today': today,
            'week_timings': week_timings,
            'branch_id': branch_id,
            'online_services': online_services,
            'doctors': doctors,
            'selected_doctor': selected_doctor,
            'insurance_companies': insurance_companies,
        }
        return request.env['ir.ui.view'].render_template("online_appointment.online_scheduling_index", values)

    @http.route(['/online_appointment/registration'], type='json', auth="public", website=True)
    def online_appointment_registered(self, **post):
        if not post.get('csrf_token', None):
            return request.env['ir.ui.view'].render_template("online_appointment.not_allowed_page")
        try:
            patient = request.env['res.partner'].sudo().search(
                [('email', '=', post['email']), ('date_of_birth', '=', post['dob']),
                 ('first_name', '=ilike', post['first_name']), ('last_name', '=ilike', post['last_name'])], limit=1)
            new_patient = 'No'
            if not patient:
                new_patient = 'Yes'
                patient = request.env['res.partner'].sudo().create({
                    'email': post['email'],
                    'phone': post['mobile'],
                    # 'date_of_birth': post['dob'],
                    'date_of_birth': datetime.strptime(post['dob'], '%Y-%m-%d'),
                    'first_name': post['first_name'],
                    'last_name': post['last_name'],
                    'gender': post['gender'],
                    'name': post['first_name'] + " " + post['last_name'],
                    'patient': True,
                    'company_id': post['branch'],
                    'disabled_email': True,
                })
                spec_communication_table = request.env['spec.communication.table'].sudo().search(
                    [('communication', '=', 'Appointment'),
                     ('partner_id', '=', patient.id)])
                if 'acknowledge' in post and post['acknowledge'] == 'Y':
                    spec_communication_table.sudo().update({
                        'text': True,
                        # 'cell': post['insured_gender'],
                        'email': True,
                        # 'mail': post['insurance'],
                    })
            if 'insurance_q' in post and post['insurance_q'] == 'Y':
                spec_insurance = request.env['spec.insurance'].sudo().create({
                    'name': post['primary_insured'],
                    'gender': post['insured_gender'],
                    # 'date': post['insured_dob'],
                    'date': datetime.strptime(post['insured_dob'], '%Y-%d-%m').strftime('%m/%d/%Y'),
                    'carrier_id': post['insurance'],
                    'sequence': post['ssn'],
                    'partner_id': patient.id,
                })

            if 'not_sure' in post and post['not_sure'] == '1':
                new_patient = 'No'

            branch = request.env['res.company'].sudo().search([('id', '=', int(post['branch']))])
            company_event_tz = branch.timezone

            online_schedule = request.env['pe.setting'].sudo().search(
                [('company_id', '=', int(post['branch']))]).online_schedule
            online_requests = 0
            appointment = 0
            if not online_schedule:
                close_datetime = datetime.strptime(post['date_time'], '%I:%M %p')
                appointment_datetime = datetime.strptime(post['date'], '%m/%d/%Y')
                # appointment_datetime = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(branch, close_datetime,
                #                                                                                      _date=datetime.strptime(
                #                                                                                          post['date'],
                #                                                                                          '%m/%d/%Y'),
                #                                                                                      _tz_name=company_event_tz)
                online_requests = request.env['online.requests'].sudo().create({
                    'date_of_request': fields.date.today().strftime('%Y-%m-%d'),
                    'time_of_request': fields.datetime.today().strftime('%I:%M %p'),
                    'patient_name': patient.id,
                    'patient_status': new_patient,
                    'contacts_status': post['contacts'],
                    'appointment_date': appointment_datetime.strftime('%Y-%m-%d'),
                    # 'appointment_date': datetime.strptime(post['date'], '%m/%d/%Y').strftime('%Y-%m-%d'),
                    # 'appointment_time': post['date_time'],
                    'appointment_time': close_datetime.strftime('%I:%M %p'),
                    'appointment_doctor': int(post['doctor']),
                    'service_id': int(post['online_service']),
                    # 'branch_id': int(post['branch']),
                    'company_id': branch.id,
                })
                online_requests = online_requests.id
            else:
                close_datetime = datetime.strptime(post['date_time'], '%I:%M %p')
                appointment_datetime = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(branch, close_datetime,
                                                                                                     _date=datetime.strptime(
                                                                                                         post['date'],
                                                                                                         '%m/%d/%Y'),
                                                                                                     _tz_name=company_event_tz)

                service_id = request.env['pe.setting.services'].sudo().search([('id', '=', int(post['online_service']))])
                appointment = request.env['calendar.event'].sudo().create({
                    'start': appointment_datetime.strftime('%m/%d/%Y '),
                    'stop': (appointment_datetime + relativedelta(minutes=service_id.service_id.duration)).strftime('%m/%d/%Y '),
                    'local_start_datetime': datetime.strptime(post['date'], '%m/%d/%Y').strftime('%m/%d/%Y ') + post[
                        'date_time'],
                    'start_datetime': appointment_datetime.strftime('%m/%d/%Y '),
                    'stop_datetime': (appointment_datetime + relativedelta(minutes=service_id.service_id.duration)).strftime('%m/%d/%Y '),
                    'appointment_type': 'appointment',
                    'employee_id': request.env['pe.setting.provider'].sudo().search(
                        [('id', '=', int(post['doctor']))]).provider_id.id,
                    'service_type': service_id.service_id.id,
                    'preferred_location_id': branch.id,
                    'patient_id': patient.id,
                    'duration': (divmod(float(service_id.service_id.duration), 60))[1] / 60
                })
                appointment = appointment.id
        except Exception as e:
            return 0
            return request.env['ir.ui.view'].render_template("online_appointment.error_page")
        return '/online_appointment/registration_box?branch=' + post['branch'] + '&patient=' + str(
            patient.id) + '&online_requests=' + str(online_requests) + '&appointment_id=' + str(appointment)
        # return request.redirect('/online_appointment/registration_box?patient='+str(patient.id)+'&online_requests='+str(online_requests.id))

    @http.route(['/online_appointment/patient_check'], type='json', auth="public", website=True)
    def online_appointment_patient_check(self, **post):
        patient = request.env['res.partner'].sudo().search_count(
            [('email', '=', post['email']), ('date_of_birth', '=', post['dob']),
             ('first_name', '=ilike', post['first_name']), ('last_name', '=ilike', post['last_name'])])

        if not patient:
            patient_01 = request.env['res.partner'].sudo().search_count(
                [('email', '=', post['email']), ('date_of_birth', '=', post['dob']),
                 ('first_name', '=ilike', post['first_name'])])
            patient_02 = request.env['res.partner'].sudo().search_count(
                [('email', '=', post['email']), ('date_of_birth', '=', post['dob']),
                 ('last_name', '=ilike', post['last_name'])])
            patient_03 = request.env['res.partner'].sudo().search_count(
                [('email', '=', post['email']), ('first_name', '=ilike', post['first_name']),
                 ('last_name', '=ilike', post['last_name'])])
            patient_04 = request.env['res.partner'].sudo().search_count(
                [('date_of_birth', '=', post['dob']), ('first_name', '=ilike', post['first_name']),
                 ('last_name', '=ilike', post['last_name'])])

            if patient_01 | patient_02 | patient_03 | patient_04:
                return 'maybe'
            return 'no'
        return 'yes'

    @http.route(['/online_appointment/registration_box'], type='http', auth="public", website=True)
    def online_appointment_register_box(self, branch, patient, online_requests, appointment_id, **post):
        online_schedule = request.env['pe.setting'].sudo().search([('company_id', '=', int(branch))]).online_schedule
        branch_id = request.env['res.company'].sudo().search([('id', '=', int(branch))])
        if not online_schedule:
            appointment = 'no_add'
        else:
            appointment = 'add'
        values = {
            'datetime': datetime,
            'branch': branch_id,
            'patient': request.env['res.partner'].sudo().search([('id', '=', int(patient))]),
            'online_requests': request.env['online.requests'].sudo().search([('id', '=', int(online_requests))]),
            'appointment_id': request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
                [('id', '=', int(appointment_id))]),
            'appointment': appointment,
        }
        return request.env['ir.ui.view'].render_template("online_appointment.online_scheduling_confirmation", values)

    @http.route(['/online_appointment/doctor_calender'], type='json', auth="public", website=True)
    def online_appointment_doctor_calender(self, branch, **post):
        today = fields.date.today()
        start_date = today
        pre_date = False
        if post.get('start_date', False):
            start_date = datetime.strptime(post['start_date'], '%m/%d/%Y')
            pre_date = True
        if post.get('end_date', False):
            start_date = datetime.strptime(post['end_date'], '%m/%d/%Y') - timedelta(days=7)
            if today != start_date.date():
                pre_date = True

        branch = request.env['res.company'].sudo().search([('id', '=', int(branch))])

        appointments_hours = request.env['appointments.hours'].sudo().search([('company_id', '=', branch.id)])

        company_event_tz = branch.timezone
        week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        day = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        date = [start_date.strftime('%b %d'), (start_date + timedelta(days=1)).strftime('%b %d'),
                (start_date + timedelta(days=2)).strftime('%b %d'),
                (start_date + timedelta(days=3)).strftime('%b %d'), (start_date + timedelta(days=4)).strftime('%b %d'),
                (start_date + timedelta(days=5)).strftime('%b %d'),
                (start_date + timedelta(days=6)).strftime('%b %d')]
        date_record = [start_date.strftime('%m/%d/%Y'), (start_date + timedelta(days=1)).strftime('%m/%d/%Y'),
                       (start_date + timedelta(days=2)).strftime('%m/%d/%Y'),
                       (start_date + timedelta(days=3)).strftime('%m/%d/%Y'),
                       (start_date + timedelta(days=4)).strftime('%m/%d/%Y'),
                       (start_date + timedelta(days=5)).strftime('%m/%d/%Y'),
                       (start_date + timedelta(days=6)).strftime('%m/%d/%Y'),
                       (start_date + timedelta(days=7)).strftime('%m/%d/%Y')]
        duration_block = int(
            request.env['appointments.hours'].sudo().search([('company_id', '=', branch.id)]).duration_block)
        calendar_events = request.env['calendar.event'].sudo().with_context(virtual_id=False).search(
            [('employee_id', '=', request.env[
                'pe.setting.provider'].sudo().search([('id', '=', int(post['doctor']))]).provider_id.id),
             ('start_datetime', '>',
              start_date + timedelta(days=-1)),
             ('start_datetime', '<',
              start_date + timedelta(days=7)),
             ('preferred_location_id', '=', branch.id)],
            order="start_datetime DESC")
        appointments_holidays_id = request.env['appointments.holidays'].sudo().search([('is_original', '=', False),
                                                                                       ('opening_time', '>',
                                                                                        start_date + timedelta(
                                                                                            days=-1)),
                                                                                       ('closing_time', '<',
                                                                                        start_date + timedelta(days=7)),
                                                                                       ('company_id', '=', branch.id)],
                                                                                      order="opening_time DESC")
        appointments_off_ids = request.env['schedule.appointment'].sudo().search([('employee_id', '=', request.env[
            'pe.setting.provider'].sudo().search([('id', '=', int(post['doctor']))]).provider_id.id),
                                                                                  ('opening_time', '>',
                                                                                   start_date + timedelta(days=-1)),
                                                                                  ('closing_time', '<',
                                                                                   start_date + timedelta(days=7)),
                                                                                  ('company_id', '=', branch.id)],
                                                                                 order="opening_time DESC")
        online_appointment = request.env['online.adjustment'].sudo().search([('employee_id', '=', request.env[
            'pe.setting.provider'].sudo().search([('id', '=', int(post['doctor']))]).provider_id.id),
                                                                             ('opening_time', '>',
                                                                              start_date + timedelta(days=-1)),
                                                                             ('closing_time', '<',
                                                                              start_date + timedelta(days=7)),
                                                                             ('company_id', '=', branch.id)],
                                                                            order="opening_time DESC")
        day0 = []
        day1 = []
        day2 = []
        day3 = []
        day4 = []
        day5 = []
        day6 = []
        day00 = []
        day11 = []
        day22 = []
        day33 = []
        day44 = []
        day55 = []
        day66 = []
        if calendar_events:
            for data in calendar_events:
                appointment_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                         datetime.strptime(str(data.start_datetime),
                                                                                           DEFAULT_SERVER_DATETIME_FORMAT))
                appointment_close_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                               datetime.strptime(
                                                                                   str(data.stop_datetime),
                                                                                   DEFAULT_SERVER_DATETIME_FORMAT))
                if start_date.strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day0.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day0.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=1)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day1.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day1.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=2)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day2.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day2.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=3)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day3.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day3.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=4)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day4.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day4.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=5)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day5.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day5.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=6)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day6.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day6.append(opening_time.strftime('%I:%M %p'))

        if appointments_holidays_id:
            for data in appointments_holidays_id:
                if data.holiday_closed:
                    appointment_datetime = datetime.strptime(str(data.date) + ' 12:00 am',
                                                             DEFAULT_SERVER_DATE_FORMAT + " %I:%M %p")
                    appointment_close_datetime = datetime.strptime(str(data.date) + ' 11:59 pm',
                                                                   DEFAULT_SERVER_DATE_FORMAT + " %I:%M %p")
                else:
                    appointment_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                             datetime.strptime(str(data.opening_time),
                                                                                               DEFAULT_SERVER_DATETIME_FORMAT))
                    appointment_close_datetime = fields.Datetime.context_timestamp(
                        data.with_context(tz=company_event_tz),
                        datetime.strptime(str(data.closing_time),
                                          DEFAULT_SERVER_DATETIME_FORMAT))
                if start_date.strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day0.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day0.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=1)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day1.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day1.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=2)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day2.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day2.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=3)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day3.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day3.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=4)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day4.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day4.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=5)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day5.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day5.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=6)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day6.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day6.append(opening_time.strftime('%I:%M %p'))

        if appointments_off_ids:
            for data in appointments_off_ids:
                if not data.is_available:
                    appointment_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                             datetime.strptime(str(data.opening_time),
                                                                                               DEFAULT_SERVER_DATETIME_FORMAT))
                    appointment_close_datetime = fields.Datetime.context_timestamp(
                        data.with_context(tz=company_event_tz),
                        datetime.strptime(str(data.closing_time),
                                          DEFAULT_SERVER_DATETIME_FORMAT))
                    if start_date.strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                        day0.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day0.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=1)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day1.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day1.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=2)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day2.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day2.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=3)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day3.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day3.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=4)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day4.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day4.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=5)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day5.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day5.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=6)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day6.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day6.append(opening_time.strftime('%I:%M %p'))
                else:
                    appointment_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                             datetime.strptime(str(data.opening_time),
                                                                                               DEFAULT_SERVER_DATETIME_FORMAT))
                    appointment_close_datetime = fields.Datetime.context_timestamp(
                        data.with_context(tz=company_event_tz),
                        datetime.strptime(str(data.closing_time),
                                          DEFAULT_SERVER_DATETIME_FORMAT))
                    if start_date.strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                        day00.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day00.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=1)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day11.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day11.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=2)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day22.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day22.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=3)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day33.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day33.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=4)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day44.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day44.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=5)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day55.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day55.append(opening_time.strftime('%I:%M %p'))
                    elif (start_date + timedelta(days=6)).strftime('%m,%d,%y') == appointment_datetime.strftime(
                            '%m,%d,%y'):
                        day66.append(appointment_datetime.strftime('%I:%M %p'))
                        opening_time = appointment_datetime
                        minutes = math.ceil(
                            ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                                duration_block)) - 1
                        for more_slots in range(minutes):
                            opening_time = opening_time + relativedelta(minutes=int(duration_block))
                            day66.append(opening_time.strftime('%I:%M %p'))

        if online_appointment:
            for data in online_appointment:
                appointment_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                         datetime.strptime(str(data.opening_time),
                                                                                           DEFAULT_SERVER_DATETIME_FORMAT))
                appointment_close_datetime = fields.Datetime.context_timestamp(data.with_context(tz=company_event_tz),
                                                                               datetime.strptime(str(data.closing_time),
                                                                                                 DEFAULT_SERVER_DATETIME_FORMAT))
                if start_date.strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day0.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day0.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=1)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day1.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day1.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=2)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day2.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day2.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=3)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day3.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day3.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=4)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day4.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day4.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=5)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day5.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day5.append(opening_time.strftime('%I:%M %p'))
                elif (start_date + timedelta(days=6)).strftime('%m,%d,%y') == appointment_datetime.strftime('%m,%d,%y'):
                    day6.append(appointment_datetime.strftime('%I:%M %p'))
                    opening_time = appointment_datetime
                    minutes = math.ceil(
                        ((appointment_close_datetime - appointment_datetime).total_seconds() / 60.0) / int(
                            duration_block)) - 1
                    for more_slots in range(minutes):
                        opening_time = opening_time + relativedelta(minutes=int(duration_block))
                        day6.append(opening_time.strftime('%I:%M %p'))

        for i in range(today.weekday()):
            week.append(week.pop(0))
            day.append(day.pop(0))

        values = {
            'fields': fields,
            'datetime': datetime,
            'relativedelta': relativedelta,
            'duration_block': duration_block,
            'company_event_tz': company_event_tz,
            'appointments_hours': appointments_hours.id,
            'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,

            'today': today,
            'doctor': int(post['doctor']),
            'week': week,
            'date': date,
            'date_record': date_record,
            'day': day,
            'day0': day0,
            'day1': day1,
            'day2': day2,
            'day3': day3,
            'day4': day4,
            'day5': day5,
            'day6': day6,
            'day00': day00,
            'day11': day11,
            'day22': day22,
            'day33': day33,
            'day44': day44,
            'day55': day55,
            'day66': day66,
            'pre_date': pre_date,
        }
        return request.env['ir.ui.view'].render_template("online_appointment.doctor_calender_view", values)
