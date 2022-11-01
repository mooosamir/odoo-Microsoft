# -*- coding: utf-8 -*-

import pytz
from typing import re
from dateutil import tz
from datetime import datetime, date
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from ...opt_custom import models as timestamp_UTC
from odoo.http import content_disposition, request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError


class OnlineRequests(models.Model):
    _name = 'online.requests'
    _description = 'Appointment Requests For Online Patients'
    _order = "create_date DESC"

    def _compute_auto_add(self):
        for rec in self:
            rec.online_schedule = self.env['pe.setting'].search([('company_id', '=', self.env.company.id)]).online_schedule

    online_schedule = fields.Boolean(string='Auto Add', compute='_compute_auto_add')
    active = fields.Boolean(default=True)

    re_schedule_id = fields.Many2one('calendar.event', string="Reschedule Appointment")
    state = fields.Selection([('new', 'new'), ('reschedule', 'reschedule'), ('cancel', 'cancel'),
                              ('scheduled', 'scheduled'), ('rescheduled', 'rescheduled'), ('deleted', 'deleted')
                              ], default="new")

    type = fields.Selection([('New Appointment Request', 'New Appointment Request'),
                              ('Appointment Reschedule Request', 'Appointment Reschedule Request'),
                              ('Cancel Appointment Request', 'Cancel Appointment Request'),
                               ], default="New Appointment Request", string="Type")
    date_of_request = fields.Date(string="Date", required=True)
    time_of_request = fields.Char(string="Time", required=True)
    datetime_of_request = fields.Datetime(string="DateTime")

    patient_name = fields.Many2one('res.partner', string="Patient Name", required=True,
                                   domain="[('patient', '=', True)]")
    patient_mobile = fields.Char(string="Mobile", related="patient_name.phone")
    patient_dob = fields.Char(string="DOB", related="patient_name.age")
    patient_email = fields.Char(string="Email", related="patient_name.email")
    patient_status = fields.Selection([("Yes", "Yes"), ("No", "No")], defaut="Yes", string="New Patient?")
    contacts_status = fields.Selection([("Yes", "Yes"), ("No", "No"), ('Interested', 'Interested')], defaut="Yes", string="Contacts?")

    appointment_date = fields.Date(string="Date Requested", required=True)
    appointment_time = fields.Char(string="Time Requested", required=True)
    appointment_datetime = fields.Datetime(string="DateTime Requested")
    appointment_doctor = fields.Many2one('pe.setting.provider', string="Provider", required=True,
                                         domain=lambda self: [('id', 'in', self.env['pe.setting'].
                                                               search([('company_id', '=', self.env.company.id)]).provider_id.ids)])
    service_id = fields.Many2one('pe.setting.services', string="Service", required=True,
                                 domain=lambda self: [('id', 'in', self.env['pe.setting'].
                                                       search([('company_id', '=', self.env.company.id)]).services_id.ids)])

    # From appointment (calendar.event)(opt_appointment)
    appointment_type = fields.Selection([('appointment', 'Appointment')], string="Appointment Requested", default='appointment')

    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company)

    def systray_get_notifications(self):
        return self.search_count([('company_id', '=', self.env.company.id), ("state", "=", "new")])

    @api.model
    def create(self, values):
        if not values.get('time_of_request'):
            values['time_of_request'] = self.time_of_request
        if not values.get('date_of_request'):
            values['date_of_request'] = self.date_of_request
        else:
            values['date_of_request'] = datetime.strptime(values['date_of_request'], '%Y-%m-%d').date()
        if not values.get('appointment_time'):
            values['appointment_time'] = self.appointment_time
        if not values.get('appointment_date'):
            values['appointment_date'] = self.appointment_date
        else:
            values['appointment_date'] = datetime.strptime(values['appointment_date'], '%Y-%m-%d').date()
        if values.get('company_id'):
            company_event_tz = self.env['res.company'].search([('id', '=', values['company_id'])]).timezone
        if values.get('time_of_request') and values.get('date_of_request'):
            open_datetime = datetime.strptime(values['time_of_request'], '%I:%M %p')
            values['datetime_of_request'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime, _date=values['date_of_request'], _tz_name=company_event_tz))
        if values.get('appointment_time') and values.get('appointment_date'):
            close_datetime = datetime.strptime(values['appointment_time'], '%I:%M %p')
            values['appointment_datetime'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime, _date=values['appointment_date'], _tz_name=company_event_tz))
        values['date_of_request'] = values["date_of_request"].strftime('%Y-%m-%d')
        values['appointment_date'] = values["appointment_date"].strftime('%Y-%m-%d')
        return super(OnlineRequests, self).create(values)

    def write(self, values):
        if values.get('company_id'):
            company_event_tz = self.env['res.company'].search([('id', '=', values['company_id'])]).timezone
        else:
            company_event_tz = self.env['res.company'].search([('id', '=', self.company_id.id)]).timezone

        if not values.get('time_of_request'):
            values['time_of_request'] = self.time_of_request
        if not values.get('date_of_request'):
            values['date_of_request'] = self.date_of_request
        else:
            values['date_of_request'] = datetime.strptime(values['date_of_request'], '%Y-%m-%d').date()
        if not values.get('appointment_time'):
            values['appointment_time'] = self.appointment_time
        if not values.get('appointment_date'):
            values['appointment_date'] = self.appointment_date
        else:
            values['appointment_date'] = datetime.strptime(values['appointment_date'], '%Y-%m-%d').date()

        if values.get('time_of_request') and values.get('date_of_request'):
            open_datetime = datetime.strptime(values['time_of_request'], '%I:%M %p')
            values['datetime_of_request'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime, _date=values['date_of_request'], _tz_name=company_event_tz))
        if values.get('appointment_time') and values.get('appointment_date'):
            close_datetime = datetime.strptime(values['appointment_time'], '%I:%M %p')
            values['appointment_datetime'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime, _date=values['appointment_date'], _tz_name=company_event_tz))

        values['date_of_request'] = values["date_of_request"].strftime('%Y-%m-%d')
        values['appointment_date'] = values["appointment_date"].strftime('%Y-%m-%d')
        return super(OnlineRequests, self).write(values)

    @api.onchange('type')
    def _change_state(self):
        if self.type == 'New Appointment Request':
            self.state = "new"
        elif self.type == 'Appointment Reschedule Request':
            self.state = "reschedule"
        else:
            self.state = "cancel"

    def new_schedule(self):
        appointment = self.env['calendar.event'].create({
            # 'appointment_date': self.appointment_date,
            # 'appointment_time': self.appointment_time,
            'start': self.appointment_datetime,
            'stop': self.appointment_datetime + relativedelta(minutes=self.service_id.service_id.duration),
            'local_start_datetime': self.appointment_date.strftime('%m/%d/%Y ') + self.appointment_time,
            'start_datetime': self.appointment_datetime,
            'stop_datetime': self.appointment_datetime + relativedelta(minutes=self.service_id.service_id.duration),
            'appointment_type': self.appointment_type,
            'employee_id': self.appointment_doctor.provider_id.id,
            'service_type': self.service_id.service_id.id,
            'preferred_location_id': self.company_id.id,
            'patient_id': self.patient_name.id,
            'duration': (divmod(float(self.service_id.service_id.duration), 60))[1] / 60
        })
        if appointment.id:
            self.state = 'scheduled'

    def delete_schedule(self):
        self.state = 'deleted'

    def remove_schedule(self):
        self.state = 'new'
        self.active = False

    def contact_patient(self):
        self.ensure_one()
        form =self.env.ref('patient_engagement.contact_patient_wizard_view', False)
        return {
            'name': _('Contact Patient'),
            'type': 'ir.actions.act_window',
            'res_model': 'contact.patient.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': [(form and form.id)],
            'views': [(form and form.id, 'form')],
            'context': {
                    'default_patient_id': self.patient_name.id,
                    'default_patient_mobile': self.patient_mobile,
                    }
            }
