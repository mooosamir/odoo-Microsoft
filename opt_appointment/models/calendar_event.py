# -*- coding: utf-8 -*-

import pytz
from typing import re
from dateutil import tz
from datetime import datetime, date, timedelta
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from ...opt_custom import models as timestamp_UTC


class Meeting(models.Model):
    _inherit = 'calendar.event'
    _description = "Appointment"
    # _rec_name = 'new_rec_name'
    _order = 'start_datetime DESC'

    def _compute_local_start_datetime(self):
        for res in self:
            res.compute_local_start_datetime = res.local_start_datetime
            # if res.recurrency and res.rrule:
            #     res.compute_local_start_datetime = str(res.start_datetime)[5:7] + "/" + str(res.start_datetime)[8:10] + res.local_start_datetime[5:]
            #     if len(res.get_recurrent_ids([])) > 0:
            #         for calendar in self.browse(res.get_recurrent_ids([])):
            #             compute_local_start_datetime = str(calendar.start_datetime)[5:7] + "/" + str(calendar.start_datetime)[8:10] + res.local_start_datetime[5:]
            #             self.env.cache.set(calendar, self._fields['local_start_datetime'],
            #                                compute_local_start_datetime)
            #             calendar.local_start_datetime = compute_local_start_datetime
                        # self.env.cache.set(calendar, self._fields['compute_local_start_datetime'],
                        #                    compute_local_start_datetime)

    @api.depends('patient_id')
    def _compute_appintment_name(self):
        for rec in self:
            if rec.patient_id:
                rec.update({'name': rec.patient_id.display_name})

    def _compute_new_rec_name(self):
        for rec in self:
            rec.new_rec_name = "NAME:" + rec.name + " DateTime:" + str(rec.start_datetime) + " STATUS: " + rec.appointment_status
    # @api.depends('start', 'stop')
    # def _compute_appointment_duration(self):
    #     """ Get the duration value between the 2 given dates. """
    #     duration = 00
    #     for rec in self:
    #         if rec.start and rec.stop:
    #             diff = fields.Datetime.from_string(rec.stop) - fields.Datetime.from_string(rec.start)
    #             if diff:
    #                 duration = float(diff.days) * 24 + (float(diff.seconds) / 60)
    #         rec.update({'appointment_duration':int(duration)})

    # new_rec_name = fields.Char(compute="_compute_new_rec_name")
    company_event_tz = fields.Selection('_event_tz_get', string='Timezone', default=lambda self: self.env.user.company_id.timezone)
    local_start_datetime = fields.Char(string='Local Datetime', required=False, copy=False)
    compute_local_start_datetime = fields.Char(compute='_compute_local_start_datetime')

    @api.onchange('local_start_datetime')
    def local_time(self):
        if self.local_start_datetime:
            if self.start and self.stop:
                duration = fields.Datetime.from_string(self.stop) - fields.Datetime.from_string(self.start)
            self.start = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, datetime.strptime(
                self.local_start_datetime,  timestamp_UTC.datetime.TimeConversation.user_datetime_format(self)), _tz_name=self.company_event_tz, _same= True)
            if duration:
                self.stop = self.start + duration

    name = fields.Char(compute="_compute_appintment_name", string='Meeting Subject', required=False, store=True)
    patient_id = fields.Many2one('res.partner', string="Patient")
    service_type = fields.Many2one('product.template',
                                   domain="[('categ_id.name','=','Services'), ('appointment_checkbox', '=', True)]",
                                   string="Service")
    insurance_id = fields.Many2one('spec.insurance', string="Insurance")
    phone = fields.Char(related='patient_id.phone', string="Phone")
    age = fields.Char(related='patient_id.age', string="Age")
    user_id = fields.Many2one('res.users', string='Resource', default=lambda self: self.env.user, readonly="False")
    pre_appointment = fields.Boolean(string="Pre-Appointment")
    appointment_date = fields.Date(string="Appointment Date")
    appointment_time = fields.Float(string="Appointment Time")
    confirmation_status = fields.Selection(
        [('none', 'Booked'), ('left_message', 'Left Message'), ('not_available', 'Not Available'),
         ('confirmed', 'Confirmed')], default='none', string="Confirmation Status")
    appointment_status = fields.Selection(
        [('none', 'Scheduled'), ('no_show', 'No Show'), ('checked_in', 'Checked In'), ('checked_out', 'Checked Out'),
         ('walk_in', 'Walk In'), ('rescheduled', 'Rescheduled'), ('cancel', 'Cancelled')], default='none',
        string="Appointment Status")
    notes = fields.Text(string="Notes")
    employee_id = fields.Many2one('hr.employee', string="Provider", required='1')
    telehealth = fields.Boolean(string="Telehealth")
    # appointment_duration = fields.Integer(compute="_compute_appointment_duration", string='Duration')
    # appointment_duration = fields.Integer(string='Duration', default=15)
    color = fields.Char(string="Color")
    appointment_type = fields.Selection([('appointment', 'Appointment')], string="Type", default='appointment')

    cancellations_count = fields.Integer(default=0, compute='_appointment_status_counts')
    no_shows_count = fields.Integer(default=0, compute='_appointment_status_counts')
    reschedule_count = fields.Integer(default=0, compute='_appointment_status_counts')

    preferred_location_id = fields.Many2one('res.company', "Location", default=lambda self: self.env.company)

    @api.constrains('patient_id', 'start_datetime', 'employee_id')
    def _check_appointment_clash(self):
        if not self._context.get('detaching'):
            for rec in self:
                self._cr.execute("""SELECT
                                        id
                                    FROM
                                        calendar_event
                                    WHERE
                                        active = True AND
                                        id != %d AND
                                        employee_id = %d AND
                                        patient_id = %d AND
                                        appointment_status != 'rescheduled' AND
                                        (start_datetime, stop_datetime) OVERLAPS ('%s', '%s')
                                    LIMIT 1 """ % (rec.id, rec.employee_id.id, rec.patient_id.id,
                                                   rec.start_datetime,
                                                   rec.stop_datetime))
                if self._cr.fetchone():
                    raise ValidationError(
                        _("Another appointment is already scheduled, would you still like to create an appointment?"))

    @api.onchange('patient_id')
    def _onchange_patient(self):
        self.partner_ids = False
        if self.patient_id:
            self.update({'partner_ids': [(6, 0, [self.patient_id.id])]})

    @api.onchange('patient_id')
    def _appointment_status_counts(self):
        for data in self:
            data.cancellations_count = data.search_count([('patient_id', '=', data.patient_id.id), ('appointment_status', '=', 'cancel')])
            data.no_shows_count = data.search_count([('patient_id', '=', data.patient_id.id), ('appointment_status', '=', 'no_show')])
            data.reschedule_count = data.search_count([('patient_id', '=', data.patient_id.id), ('appointment_status', '=', 'rescheduled')])

    def write(self, vals):
        res = super(Meeting, self).write(vals)
        for rec in self:
            if rec._context.get('default_appointment_type') == 'appointment' and \
                    rec._context.get('create') == False and \
                    vals.get('start_datetime'):
                rec.appointment_status = 'rescheduled'
                if vals.get('notes'):
                    rec.notes = 'Rescheduled Due To:' + ' ' + str(vals.get('notes'))
        return res

    @api.model
    def create(self, vals):
        res = super(Meeting, self).create(vals)
        get_recurrent_ids = [x for x in self.browse(res.get_recurrent_ids([]))
                             if x.start_datetime != str(res.start_datetime) and x.id != res.id]
        if len(get_recurrent_ids) > 0:
            for calendar in get_recurrent_ids:
                meeting = calendar.detach_recurring_event()
                meeting.local_start_datetime = str(meeting.start_datetime)[5:7] + "/" + \
                                               str(meeting.start_datetime)[8:10] + \
                                               res.local_start_datetime[5:]
                # self.env.cache.set(calendar, self._fields['local_start_datetime'],
                #                    compute_local_start_datetime)
            res.recurrency = 0
        return res

    @api.onchange('service_type')
    def _onchange_service_type(self):
        if self.service_type:
            self.duration = (divmod(float(self.service_type.duration), 60))[1]/60

    def get_appointment_booking_datas(self, employee_id, status, company_id, date_domain, day_single):
        # get resource Doctor
        resources = []
        more_resources = []
        events = []
        js_events = []
        js_events_extended = []
        monday_working_hours = []
        tuesday_working_hours = []
        wednesday_working_hours = []
        thursday_working_hours = []
        friday_working_hours = []
        saturday_working_hours = []
        sunday_working_hours = []

        datetime_check = datetime.strptime(str(date_domain[1][2]), DEFAULT_SERVER_DATETIME_FORMAT)

        # Timezone correction
        if str(datetime_check + relativedelta(days=1))[8:10] != date_domain[0][2][8:10]:
            # date_domain[0][2] = date_domain[0][2][:11] + "00:00:00"
            if datetime.strptime(date_domain[1][2], '%Y-%m-%d %H:%M:%S').weekday() == 6:
                date_domain[1][2] = str(datetime.strptime(date_domain[1][2], '%Y-%m-%d %H:%M:%S') - relativedelta(days=1))
            elif datetime.strptime(date_domain[1][2], '%Y-%m-%d %H:%M:%S').weekday() == 4:
                date_domain[1][2] = str(datetime.strptime(date_domain[1][2], '%Y-%m-%d %H:%M:%S') + relativedelta(days=1))
            datetime_check = datetime.strptime(str(date_domain[1][2]), DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            if datetime.strptime(date_domain[0][2], '%Y-%m-%d %H:%M:%S').weekday() == day_single:
                date_domain[0][2] = str(datetime.strptime(date_domain[0][2], '%Y-%m-%d %H:%M:%S') - relativedelta(days=1))
                date_domain[1][2] = str(datetime.strptime(date_domain[1][2], '%Y-%m-%d %H:%M:%S') - relativedelta(days=1))
                datetime_check = datetime.strptime(str(date_domain[1][2]), DEFAULT_SERVER_DATETIME_FORMAT)

        # appointment_duration_ids = self.env['appointments.open.close'].search([])
        appointment_duration_ids = self.env['appointments.hours'].search([('company_id', '=', self.env.user.company_id.id)]).appointments_close_open_ids
        appointments_hours_id = self.env['appointments.hours'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)

        if date_domain[0][0] == 'start':
            date_domain[0][0] = 'opening_time'
        if date_domain[1][0] == 'stop':
            date_domain[1][0] = 'closing_time'
        date_domain.append(('is_original', '=', False))
        date_domain.append(('company_id', '=', self.env.user.company_id.id))

        # appointments_holidays_id = self.env['appointments.hours'].search([('company_id', '=', self.env.company.id)]).appointments_holidays_ids
        appointments_holidays_id = self.env['appointments.holidays'].search(date_domain)

        # domain = [('doctor', '=', True), ('appointment', '=', True)]
        domain = [('appointment', '=', True)]
        if employee_id:
            domain.append(('id', 'in', employee_id))
        # if company_id:
        #     domain.append(('user_id.company_id', 'in', company_id))
        doctors = self.env['hr.employee'].search(domain)
        companies = self.env['res.company'].search([])

        for duration in appointment_duration_ids:
            day = ''
            jsday = ''
            if duration.day_select == 'mo':
                day = 'Monday'
                jsday = 'Mon'
            elif duration.day_select == 'tu':
                day = 'Tuesday'
                jsday = 'Tue'
            elif duration.day_select == 'we':
                day = 'Wednesday'
                jsday = 'Wed'
            elif duration.day_select == 'th':
                day = 'Thursday'
                jsday = 'Thu'
            elif duration.day_select == 'fr':
                day = 'Friday'
                jsday = 'Fri'
            elif duration.day_select == 'sa':
                day = 'Saturday'
                jsday = 'Sat'
            elif duration.day_select == 'su':
                day = 'Sunday'
                jsday = 'Sun'
            # ============================
            # Showing in company timezone
            # ============================
            events.append({
                'start': '00:00:00',
                'end': duration.opening_time and (
                    fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz), datetime.strptime(str(duration.opening_time),
                                                                              DEFAULT_SERVER_DATETIME_FORMAT))).time() or '12:00:00',
                'rendering': 'background',
                'resourceIds': doctors.ids,
                # 'title': 'closed',
                'backgroundColor': duration.appointments_hours_id.closed_color or 'black',
                'day': day
            })
            js_events.append({
                'day': jsday,
                'start': '00:00:00',
                'end': duration.opening_time and (
                    fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz), datetime.strptime(str(duration.opening_time),
                                                                              DEFAULT_SERVER_DATETIME_FORMAT))).time() or '12:00:00',
                'resourceIds': doctors.ids,
            })
            events.append({
                'start': duration.closing_time and (
                    fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz), datetime.strptime(str(duration.closing_time),
                                                                              DEFAULT_SERVER_DATETIME_FORMAT))).time() or '12:00:01',
                'end': '23:59:59',
                'rendering': 'background',
                'resourceIds': doctors.ids,
                # 'title': 'closed',
                'backgroundColor': duration.appointments_hours_id.closed_color or 'black',
                'day': day
            })
            js_events.append({
                'day': jsday,
                'start': duration.closing_time and (
                    fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz), datetime.strptime(str(duration.closing_time),
                                                                              DEFAULT_SERVER_DATETIME_FORMAT))).time() or '12:00:01',
                'end': '23:59:59',
                'resourceIds': doctors.ids,
            })

        if str(datetime_check + relativedelta(days=1))[8:10] != date_domain[0][2][8:10]:
            for duration in appointments_holidays_id:
                day = ''
                jsday = ''
                if str(duration.date)[8:] == str(datetime_check + relativedelta(days=2))[8:10]:
                    day = 'Monday'
                    jsday = 'Mon'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=3))[8:10]:
                    day = 'Tuesday'
                    jsday = 'Tue'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=4))[8:10]:
                    day = 'Wednesday'
                    jsday = 'Wed'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=5))[8:10]:
                    day = 'Thursday'
                    jsday = 'Thu'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=6))[8:10]:
                    day = 'Friday'
                    jsday = 'Fri'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=7))[8:10]:
                    day = 'Saturday'
                    jsday = 'Sat'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=1))[8:10]:
                    day = 'Sunday'
                    jsday = 'Sun'

                if duration.holiday_closed:
                    events.append({
                        'start': '00:00:00',
                        'end': '23:59:59',
                        'rendering': 'background',
                        'resourceIds': doctors.ids,
                        'title': duration.name,
                        'backgroundColor': appointments_hours_id.holiday_color or 'black',
                        'day': day,
                        'editable': False,
                    })
                    js_events.append({
                        'day': jsday,
                        'start': '00:00:00',
                        'end': '23:59:59',
                        'resourceIds': doctors.ids,
                    })
                elif not duration.holiday_closed:
                    events.append({
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'rendering': 'background',
                        'resourceIds': doctors.ids,
                        'title': duration.name,
                        'backgroundColor': appointments_hours_id.closed_color or 'black',
                        'day': day,
                        'editable': False,
                    })
                    js_events.append({
                        'day': jsday,
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'resourceIds': doctors.ids,
                    })

        if str(datetime_check + relativedelta(days=1))[8:10] == date_domain[0][2][8:10]:
            for duration in appointments_holidays_id:
                day = ''
                jsday = ''
                if day_single == 1:
                    day = 'Monday'
                    jsday = 'Mon'
                elif day_single == 2:
                    day = 'Tuesday'
                    jsday = 'Tue'
                elif day_single == 3:
                    day = 'Wednesday'
                    jsday = 'Wed'
                elif day_single == 4:
                    day = 'Thursday'
                    jsday = 'Thu'
                elif day_single == 5:
                    day = 'Friday'
                    jsday = 'Fri'
                elif day_single == 6:
                    day = 'Saturday'
                    jsday = 'Sat'
                elif day_single == 0:
                    day = 'Sunday'
                    jsday = 'Sun'

                if str(duration.date)[8:] == date_domain[0][2][8:10]:
                    if duration.holiday_closed:
                        events.append({
                            'start': '00:00:00',
                            'end': '23:59:59',
                            'rendering': 'background',
                            'resourceIds': doctors.ids,
                            'title': duration.name,
                            'backgroundColor': appointments_hours_id.holiday_color or 'black',
                            'day': day,
                            'editable': False,
                        })
                        js_events.append({
                            'day': jsday[0:3],
                            'start': '00:00:00',
                            'end': '23:59:59',
                            'resourceIds': doctors.ids,
                        })
                    else:
                        events.append({
                            'start': duration.opening_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(duration.opening_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                            'end': duration.closing_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(duration.closing_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                            'rendering': 'background',
                            'resourceIds': doctors.ids,
                            'title': duration.name,
                            'backgroundColor': appointments_hours_id.closed_color or 'black',
                            'day': day,
                            'editable': False,
                        })
                        js_events.append({
                            'day': jsday,
                            'start': duration.opening_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(duration.opening_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                            'end': duration.closing_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(duration.closing_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                            'resourceIds': doctors.ids,
                        })

        new_date_domain = date_domain
        if new_date_domain[0][0] == 'opening_time':
            new_date_domain[0][0] = 'date'
            if str(datetime_check + relativedelta(days=1))[8:10] == date_domain[0][2][8:10]:
                new_date_domain[0][1] = '='
            new_date_domain[0][2] = new_date_domain[0][2][:10]
        close_time = 0
        if str(datetime_check + relativedelta(days=1))[8:10] == date_domain[0][2][8:10]:
            close_time = new_date_domain[1]
            new_date_domain.remove(close_time)
        else:
            if new_date_domain[1][0] == 'opening_time':
                new_date_domain[1][0] = 'date'
                new_date_domain[1][2] = new_date_domain[1][2][:10]

        appointments_off_ids = self.env['schedule.appointment'].search(new_date_domain)
        if close_time:
            a = new_date_domain[1]
            b = new_date_domain[2]
            new_date_domain.remove(a)
            new_date_domain.remove(b)
            new_date_domain.append(close_time)
            new_date_domain.append(a)
            new_date_domain.append(b)

        if str(datetime_check + relativedelta(days=1))[8:10] != date_domain[0][2][8:10]:
            for duration in appointments_off_ids:
                day = ''
                jsday = ''
                if str(duration.date)[8:] == str(datetime_check + relativedelta(days=2))[8:10]:
                    day = 'Monday'
                    jsday = 'Mon'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=3))[8:10]:
                    day = 'Tuesday'
                    jsday = 'Tue'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=4))[8:10]:
                    day = 'Wednesday'
                    jsday = 'Wed'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=5))[8:10]:
                    day = 'Thursday'
                    jsday = 'Thu'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=6))[8:10]:
                    day = 'Friday'
                    jsday = 'Fri'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=7))[8:10]:
                    day = 'Saturday'
                    jsday = 'Sat'
                elif str(duration.date)[8:] == str(datetime_check + relativedelta(days=1))[8:10]:
                    day = 'Sunday'
                    jsday = 'Sun'

                if duration.is_available:
                    js_events_extended.append({
                        'day': jsday,
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                        'resourceIds': duration.employee_id.ids,
                    })
                    opening_time = duration.opening_time
                    closing_time = duration.opening_time + relativedelta(minutes=int(appointments_hours_id.duration_block))
                    minutes = int(((duration.closing_time - opening_time).total_seconds() / 60.0) / int(appointments_hours_id.duration_block))
                    for data in range(minutes):
                        events.append({
                            'start': opening_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(opening_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                            'end': closing_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(closing_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                            'rendering': 'background',
                            'resourceIds': duration.employee_id.ids,
                            'title': "allow",
                            'backgroundColor': 'white',
                            'day': day,
                            'id': str(duration.reason) + day
                        })
                        opening_time = opening_time + relativedelta(minutes=int(appointments_hours_id.duration_block))
                        closing_time = closing_time + relativedelta(minutes=int(appointments_hours_id.duration_block))

                else:
                    # ============================
                    # Showing in branch timezone
                    # ============================
                    events.append({
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                        'rendering': 'background',
                        'resourceIds': duration.employee_id.ids,
                        'title': duration.reason,
                        'backgroundColor': duration.color or 'black',
                        'day': day,
                        'editable': False,
                        'id': str(duration.reason) + day
                    })
                    js_events.append({
                        'day': jsday,
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                        'resourceIds': duration.employee_id.ids,
                    })

        if str(datetime_check + relativedelta(days=1))[8:10] == date_domain[0][2][8:10]:
            for duration in appointments_off_ids:
                day = ''
                jsday = ''
                if day_single == 1:
                    day = 'Monday'
                    jsday = 'Mon'
                elif day_single == 2:
                    day = 'Tuesday'
                    jsday = 'Tue'
                elif day_single == 3:
                    day = 'Wednesday'
                    jsday = 'Wed'
                elif day_single == 4:
                    day = 'Thursday'
                    jsday = 'Thu'
                elif day_single == 5:
                    day = 'Friday'
                    jsday = 'Fri'
                elif day_single == 6:
                    day = 'Saturday'
                    jsday = 'Sat'
                elif day_single == 0:
                    day = 'Sunday'
                    jsday = 'Sun'

                if duration.is_available:
                    js_events_extended.append({
                        'day': jsday,
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                        'resourceIds': duration.employee_id.ids,
                    })
                    opening_time = duration.opening_time
                    closing_time = duration.opening_time + relativedelta(minutes=int(appointments_hours_id.duration_block))
                    minutes = int(((duration.closing_time - opening_time).total_seconds() / 60.0) / int(appointments_hours_id.duration_block))
                    for data in range(minutes):
                        events.append({
                            'start': opening_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(opening_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                            'end': closing_time and (
                                fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                                  datetime.strptime(str(closing_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                            'rendering': 'background',
                            'resourceIds': duration.employee_id.ids,
                            'title': "allow",
                            'backgroundColor': 'white',
                            'day': day,
                            'id': str(duration.reason) + day
                        })
                        opening_time = opening_time + relativedelta(minutes=int(appointments_hours_id.duration_block))
                        closing_time = closing_time + relativedelta(minutes=int(appointments_hours_id.duration_block))
                else:
                    # ============================
                    # Showing in branch timezone
                    # ============================

                    events.append({
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                        'rendering': 'background',
                        'resourceIds': duration.employee_id.ids,
                        'title': duration.reason,
                        'backgroundColor': duration.color or 'black',
                        'day': day,
                        'editable': False,
                        'id': str(duration.reason) + day
                    })
                    js_events.append({
                        'day': jsday,
                        'start': duration.opening_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.opening_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                        'end': duration.closing_time and (
                            fields.Datetime.context_timestamp(duration.with_context(tz=duration.company_event_tz),
                                                              datetime.strptime(str(duration.closing_time),
                                                                                DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                        'resourceIds': duration.employee_id.ids,
                    })

        for doctor in doctors:
            # hour_from = hour_to = ''
            for duration in doctor.resource_calendar_id.attendance_ids:
                day = ''
                if duration.dayofweek == '0':
                    monday_working_hours.append(duration)
                    day = 'Monday'
                elif duration.dayofweek == '1':
                    tuesday_working_hours.append(duration)
                    day = 'Tuesday'
                elif duration.dayofweek == '2':
                    wednesday_working_hours.append(duration)
                    day = 'Wednesday'
                elif duration.dayofweek == '3':
                    thursday_working_hours.append(duration)
                    day = 'Thursday'
                elif duration.dayofweek == '4':
                    friday_working_hours.append(duration)
                    day = 'Friday'
                elif duration.dayofweek == '5':
                    saturday_working_hours.append(duration)
                    day = 'Saturday'
                elif duration.dayofweek == '6':
                    sunday_working_hours.append(duration)
                    day = 'Sunday'
                # start = '00:00:00'
                # end = '23:59:59'
                # ============================
                # Showing in branch timezone
                # ============================

                if duration.day_period == 'morning':
                    hour_from = fields.Datetime.to_string(
                        timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(
                            self, datetime.strptime(str(timedelta(hours=duration.hour_from)), '%H:%M:%S'),
                            _tz_name=doctor.resource_calendar_id.tz))

                if duration.day_period == 'afternoon':
                    hour_to = fields.Datetime.to_string(
                        timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(
                            self, datetime.strptime(str(timedelta(hours=duration.hour_to)), '%H:%M:%S'),
                            _tz_name=doctor.resource_calendar_id.tz))

                    events.append({
                                    'resourceId': doctor.id,
                                    # 'title':doctor.display_name,
                                    'backgroundColor': appointments_hours_id.closed_color,
                                    'start': '00:00:00',
                                    # 'end': datetime.utcfromtimestamp(duration.hour_from * 3600).strftime('%H:%M:%S'),
                                    'end': hour_from and (fields.Datetime.context_timestamp(duration.with_context(tz=doctor.resource_calendar_id.tz), datetime.strptime(
                                str(hour_from), DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                                    'day': day,
                                    'rendering': 'background',
                                    'editable': False,
                                    })

                    events.append({
                                    'resourceId': doctor.id,
                                    # 'title':doctor.display_name,
                                    'backgroundColor': appointments_hours_id.closed_color,
                                    # 'start': datetime.utcfromtimestamp(duration.hour_to * 3600).strftime('%H:%M:%S'),
                                    'start': hour_to and (fields.Datetime.context_timestamp(duration.with_context(tz=doctor.resource_calendar_id.tz),
                                                                                   datetime.strptime(
                                                                                       str(hour_to),
                                                                                       DEFAULT_SERVER_DATETIME_FORMAT))).time()
                                                        or '00:00:00',
                                    'end': '23:59:59',
                                    'day': day,
                                    'rendering': 'background',
                                    'editable': False,
                                    })
            # For break Time
            all_day_working_hours = []
            all_day_working_hours.append(monday_working_hours)
            all_day_working_hours.append(tuesday_working_hours)
            all_day_working_hours.append(wednesday_working_hours)
            all_day_working_hours.append(thursday_working_hours)
            all_day_working_hours.append(friday_working_hours)
            all_day_working_hours.append(saturday_working_hours)
            all_day_working_hours.append(sunday_working_hours)

            for records in all_day_working_hours:
                start_time = ''
                stop_time = ''
                day_break_time = ''
                # start = '00:00:00'
                # end = '23:59:59'
                for rec in records:
                    if rec.dayofweek == '0':
                        day_break_time = 'Monday'
                    elif rec.dayofweek == '1':
                        day_break_time = 'Tuesday'
                    elif rec.dayofweek == '2':
                        day_break_time = 'Wednesday'
                    elif rec.dayofweek == '3':
                        day_break_time = 'Thursday'
                    elif rec.dayofweek == '4':
                        day_break_time = 'Friday'
                    elif rec.dayofweek == '5':
                        day_break_time = 'Saturday'
                    elif rec.dayofweek == '6':
                        day_break_time = 'Sunday'
                    if rec.day_period == 'morning':
                        start_time = fields.Datetime.to_string(
                            timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(
                                self, datetime.strptime(str(timedelta(hours=rec.hour_to)), '%H:%M:%S'),
                                _tz_name=doctor.resource_calendar_id.tz))
                        # start_time = datetime.utcfromtimestamp(rec.hour_to * 3600).strftime('%H:%M:%S')
                    elif rec.day_period == 'afternoon':
                        stop_time = fields.Datetime.to_string(
                            timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(
                                self, datetime.strptime(str(timedelta(hours=rec.hour_from)), '%H:%M:%S'),
                                _tz_name=doctor.resource_calendar_id.tz))
                        # stop_time = datetime.utcfromtimestamp(rec.hour_from * 3600).strftime('%H:%M:%S')

                    if start_time and stop_time:
                        events.append({
                                        'resourceId': doctor.id,
                                        # 'title':doctor.display_name,
                                        'backgroundColor': doctor.color or 'lightgreen',
                                        'start' : start_time,
                                        'end' : stop_time,
                                        'day' : day_break_time,
                                        'rendering': 'background',
                                        })

        for doctor in doctors:
            resources.append({
                'id': doctor.id,
                'title': doctor.display_name,
                'eventColor': doctor.color or 'white',
                'company': companies,
            })
        for company in companies:
            more_resources.append({
                'id': company.id,
                'name': company.name,
            })

        return resources, events, more_resources, self.env.company.id, js_events, js_events_extended, pytz.timezone(self.env.user.company_id.timezone).localize(fields.datetime.now()).strftime('%Y-%m-%d %H:%M:%S %Z%z')[-5:]

    def return_values(self, domain, date_domain, employee_id, day):
        # if self.env['appointments.hours'].get_appointment_hours_details(day)[0]['default_view'] == 'week':
        domain[0][2] = str(datetime.strptime(domain[0][2], "%Y-%m-%d %H:%M:%S") + relativedelta(days=1))
        current_events = self.env['calendar.event'].with_context(virtual_id=False).search(domain)
        resources = []

        for data in current_events:
            resources.append({
                'age': data.age,
                'company_event_tz': data.company_event_tz,
                'allday': data.allday,
                'display_name': data.display_name,
                'start_datetime': data.start_datetime and (fields.Datetime.context_timestamp(data.with_context(tz=data.company_event_tz),
                                                                datetime.strptime(str(data.start_datetime),
                                                                        DEFAULT_SERVER_DATETIME_FORMAT))),
                'duration': data.duration,
                'id': data.id,
                'employee_id': [data.employee_id.id, data.employee_id.name],
                'start': data.start and (fields.Datetime.context_timestamp(data.with_context(tz=data.company_event_tz),
                                                                datetime.strptime(str(data.start),
                                                                        DEFAULT_SERVER_DATETIME_FORMAT))),
                'attendee_status': data.attendee_status,
                'stop': data.stop and (fields.Datetime.context_timestamp(data.with_context(tz=data.company_event_tz),
                                                                datetime.strptime(str(data.stop),
                                                                        DEFAULT_SERVER_DATETIME_FORMAT))),
                # 'stop': data.start + relativedelta(minutes=data.appointment_duration),
                'service_type': [data.service_type.id, data.service_type.name],
                'partner_id': [data.partner_id.id, data.partner_id.name],
                'description': data.description,
                'is_highlighted': data.is_highlighted,
                'insurance_id': [data.insurance_id.id, data.insurance_id.name if data.insurance_id.name else 'No Insurance'],
                'patient_id': [data.patient_id.id, data.patient_id.name],
                'confirmation_status': data.confirmation_status,
                'appointment_status': data.appointment_status,
                'backgroundColor': data.service_type.color if data.service_type.color else 'white',
            })
        return resources

    def appointment_rescheduled(self, id, data):
        duration = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, datetime.strptime(
            data['stop'], '%Y-%m-%d %H:%M:%S'), _tz_name=self.company_event_tz, _same=True) -\
                   timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(
                       self, datetime.strptime(data['start'], '%Y-%m-%d %H:%M:%S'),
                        _tz_name=self.company_event_tz, _same=True)

        data['start'] = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, datetime.strptime(
            data["local_start_datetime"], timestamp_UTC.datetime.TimeConversation.user_datetime_format(self)),
                                                                                      _tz_name=self.company_event_tz,
                                                                                      _same=True)
        if duration:
            data['stop'] = data['start'] + duration

        current_record = self.search([('id', '=', id)])
        current_record.update({'appointment_status': 'rescheduled'})
        self.create({
            'name': current_record["name"],
            'local_start_datetime': data["local_start_datetime"],
            'allday': data['allday'],
            'state': current_record.state,
            'active': current_record.active,
            'start': data['start'],
            'stop': data['stop'],
            'duration': data['duration'],
            'appointment_type': current_record.appointment_type,
            'patient_id': current_record.patient_id.id,
            'age': current_record.age,
            'service_type': current_record.service_type.id,
            'insurance_id': current_record.insurance_id.id,
            'phone': current_record.phone,
            'employee_id': current_record.employee_id.id,
            'preferred_location_id': current_record.preferred_location_id.id,
            'telehealth': current_record.telehealth,
            'pre_appointment': current_record.pre_appointment,
            'confirmation_status': current_record.confirmation_status,
            'appointment_status': 'none',
            'duration': current_record.duration,
            'recurrency': current_record.recurrency,
            'notes': current_record.notes,
            'interval': current_record.interval,
            'rrule_type': current_record.rrule_type,
            'end_type': current_record.end_type,
            'count': current_record.count,
            'final_date': current_record.final_date,
            'mo': current_record.mo,
            'tu': current_record.tu,
            'we': current_record.we,
            'th': current_record.th,
            'fr': current_record.fr,
            'sa': current_record.sa,
            'su': current_record.su,
            'month_by': current_record.month_by,
            'day': current_record.day,
            'byday': current_record.byday,
            'week_list': current_record.week_list,
        })

    @api.model
    def fields_view_get(self, view_id=None, view_type='search', toolbar=False, submenu=False):
        res = super(Meeting, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'search':
            doctors = self.env['hr.employee'].search([('appointment', '=', True)])
            company_id = self.env['res.company'].search([])

            string = ""
            if res['name'] == "appointment.schedule.search" or res['name'] == "opt_appointment.calendar.event.search":
                for data in doctors:
                    string += '<filter name="' + str(data.name) + '" string="' + str(data.name) + '" domain="[(\'employee_id\',\'=\',' + str(data.id) + ')]"/>\n'
            if res['name'] == "appointment.schedule.search":
                string += "<separator/>\n"
                for data in company_id:
                    string += '<filter name="' + str(data.name) + '" string="' + str(data.name) + '" domain="[(\'preferred_location_id\',\'=\',' + str(data.id) + ')]"/>\n'
            string += '<group'
            res['arch'] = res['arch'].replace('<group', string)
        return res
