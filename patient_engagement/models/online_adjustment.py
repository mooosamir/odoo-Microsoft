# -*- coding: utf-8 -*-

from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from ...opt_custom import models as timestamp_UTC
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from datetime import datetime, date
from dateutil import tz
from typing import re
import pytz


class OnlineAdjustmentt(models.Model):
    _name = 'online.adjustment'
    _description = "Online Adjustment"
    _order = "create_date DESC"

    company_event_tz = fields.Selection('_event_tz_get', string='Timezone', related='company_id.timezone')

    employee_id = fields.Many2one('hr.employee', string="Provider", required='1', domain=[('appointment', '=', True)])
    company_id = fields.Many2one('res.company', "Location", related='setting_id.company_id')

    date = fields.Date(string="Date")
    holiday_open = fields.Char(string='Start Time')
    holiday_close = fields.Char(string='End Time')
    opening_time = fields.Datetime('Modified Opening Time')
    closing_time = fields.Datetime('Modified Closing Time')

    is_original = fields.Boolean('Original')

    setting_id = fields.Many2one('pe.setting', ondelete="cascade")

    @api.model
    def _event_tz_get(self):
        return _tz_get(self)

    @api.constrains('holiday_open', 'holiday_close')
    def _check_open_close_time(self):
        for rec in self:
            open_time = "00:00"
            close_time = "24:00"
            if rec.holiday_open:
                open_time = datetime.strptime(rec.holiday_open, '%I:%M %p').strftime('%H:%M')
            if rec.holiday_close:
                close_time = datetime.strptime(rec.holiday_close, '%I:%M %p').strftime('%H:%M')
            if open_time > close_time:
                raise UserError(_('Closing time should be bigger than opening time!'))

    # RECURRENCE FIELD
    recurrency = fields.Boolean('Recurrent', help="Recurrent action")
    interval = fields.Integer(string='Repeat Every', default=1, help="Repeat every (Days/Week/Month/Year)")
    rrule_type = fields.Selection([
        ('daily', 'Days'),
        ('weekly', 'Weeks'),
        ('monthly', 'Months'),
        ('yearly', 'Years')
    ], string='Recurrence', help="Let the event automatically repeat at that interval")

    rrule = fields.Char('Recurrent Rule', store=True)
    recurrent_id = fields.Integer('Recurrent ID')
    recurrent_id_date = fields.Datetime('Recurrent ID date')
    end_type = fields.Selection([
        ('count', 'Number of repetitions'),
        ('end_date', 'End date')
    ], string='Recurrence Termination', default='count')
    count = fields.Integer(string='Repeat', help="Repeat x times", default=1)
    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    month_by = fields.Selection([
        ('date', 'Date of month'),
        ('day', 'Day of month')
    ], string='Option', default='date')
    day = fields.Integer('Date of month', default=1)
    week_list = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday')
    byday = fields.Selection([
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Fourth'),
        ('5', 'Fifth'),
        ('-1', 'Last')
    ], string='By day')
    final_date = fields.Date('Repeat Until')

    def write(self, values):
        if values.get('date'):
            values['holiday_open'] = self.holiday_open
            values['holiday_close'] = self.holiday_close
            values['date'] = datetime.strptime(values['date'], '%Y-%m-%d').date()
        else:
            values['date'] = self.date

        if values.get('company_id'):
            company_event_tz = self.env['res.company'].search([('id', '=', values['company_id'])]).timezone
            if not values.get('holiday_open'):
                values['holiday_open'] = self.holiday_open
            if not values.get('holiday_close'):
                values['holiday_close'] = self.holiday_close
        else:
            company_event_tz = self.company_event_tz

        if values.get('holiday_open'):
            open_datetime = datetime.strptime(values['holiday_open'], '%I:%M %p')
            values['opening_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime, _date=values['date'], _tz_name=company_event_tz))
        if values.get('holiday_close'):
            close_datetime = datetime.strptime(values['holiday_close'], '%I:%M %p')
            values['closing_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime, _date=values['date'], _tz_name=company_event_tz))

        values['date'] = values["date"].strftime('%Y-%m-%d')
        return super(OnlineAdjustmentt, self).write(values)

    # copy Not required, as the create function is running.

    @api.model
    def create(self, values):
        if values.get('date'):
            values['date'] = datetime.strptime(values['date'], '%Y-%m-%d').date()
        if values.get('company_id'):
            company_event_tz = self.env['res.company'].search([('id', '=', values['company_id'])]).timezone
        else:
            company_event_tz = self.company_event_tz

        if values.get('holiday_open'):
            open_datetime = datetime.strptime(values['holiday_open'], '%I:%M %p')
            values['opening_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime, _date=values['date'], _tz_name=company_event_tz))
        if values.get('holiday_close'):
            close_datetime = datetime.strptime(values['holiday_close'], '%I:%M %p')
            values['closing_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime, _date=values['date'], _tz_name=company_event_tz))
        values['date'] = values["date"].strftime('%Y-%m-%d')

        if values['recurrency']:
            original_date = values['date']
            new_values = {
                'date': values['date'],
                'employee_id': values['employee_id'],
                'holiday_open': values['holiday_open'],
                'holiday_close': values['holiday_close'],
                'setting_id': values['setting_id'],
                'recurrency': False
            }

            if values['rrule_type'] == 'daily':
                if values['end_type'] == 'count':
                    for i in range(0, values['count'], values['interval']):
                        new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(days=i)
                        super(OnlineAdjustmentt, self).create(new_values)
                else:
                    date_diff = date(int(values['final_date'][0:4]), int(values['final_date'][5:7]),
                                     int(values['final_date'][8:10])) - \
                                date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10]))
                    for i in range(0, date_diff.days, values['interval']):
                        new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(days=i)
                        super(OnlineAdjustmentt, self).create(new_values)

            elif values['rrule_type'] == 'weekly':
                if values['end_type'] == 'count':
                    Final_Date = date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10]))
                    values['date'] = str(
                        date(int(values['date'][0:4]), int(values['date'][5:7]),
                             int(values['date'][8:10])) - relativedelta(
                            days=(Final_Date.weekday())))
                    repetition_check = 0
                    for i in range(0, values['count']):
                        if values['mo'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 0)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10]))
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['tu'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 1)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=1)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['we'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 2)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=2)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['th'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 3)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=3)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['fr'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 4)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=4)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['sa'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 5)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=5)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['su'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 6)):
                            if repetition_check >= values['count']:
                                break
                            repetition_check = repetition_check + 1
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=6)
                            super(OnlineAdjustmentt, self).create(new_values)
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(
                            days=(7 * values['interval'])))
                        Final_Date = Final_Date + relativedelta(days=7 - Final_Date.weekday())
                else:
                    date_diff = date(int(values['final_date'][0:4]), int(values['final_date'][5:7]),
                                     int(values['final_date'][8:10])) - \
                                date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10]))
                    Final_Date = date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10]))
                    values['date'] = str(
                        date(int(values['date'][0:4]), int(values['date'][5:7]),
                             int(values['date'][8:10])) - relativedelta(
                            days=(Final_Date.weekday())))
                    End_Date = date(int(values['final_date'][0:4]), int(values['final_date'][5:7]),
                                    int(values['final_date'][8:10]))
                    for i in range(0, date_diff.days):
                        if values['mo'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 0)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10]))
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['tu'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 1)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])) + relativedelta(days=1):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=1)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['we'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 2)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])) + relativedelta(days=2):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=2)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['th'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 3)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])) + relativedelta(days=3):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=3)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['fr'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 4)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])) + relativedelta(days=4):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=4)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['sa'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 5)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])) + relativedelta(days=5):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=5)
                            super(OnlineAdjustmentt, self).create(new_values)
                        if values['su'] and (i != 0 or (i == 0 and Final_Date.weekday() <= 6)):
                            if End_Date < date(int(values['date'][0:4]), int(values['date'][5:7]),
                                               int(values['date'][8:10])) + relativedelta(days=6):
                                break
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(days=6)
                            super(OnlineAdjustmentt, self).create(new_values)
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(
                            days=(7 * values['interval'])))
                        Final_Date = Final_Date + relativedelta(days=7 - Final_Date.weekday())

            elif values['rrule_type'] == 'monthly':
                if values['end_type'] == 'count':
                    if values['month_by'] == 'date':
                        Final_Date = str(
                            date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10])))
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) - relativedelta(
                            days=(int(values['date'][8:10]))))
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(days=values['day']))

                        for i in range(0, values['count']):
                            if i != 0 or (i == 0 and int(Final_Date[8:10]) < int(values['date'][8:10])):
                                new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) + relativedelta(
                                    months=i * values['interval'])
                                super(OnlineAdjustmentt, self).create(new_values)
                        if int(Final_Date[8:10]) > int(values['date'][8:10]):
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(
                                months=values['count'] * values['interval'])
                            super(OnlineAdjustmentt, self).create(new_values)
                    else:
                        Final_Date = str(
                            date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10])))
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) - relativedelta(
                            days=(int(values['date'][8:10])) - 1))

                        if int(Final_Date[8:10]) > int(values['date'][8:10]):
                            values['count'] = values['count'] + 1

                        for i in range(0, values['count']):
                            if i == 0 and int(Final_Date[8:10]) > int(values['date'][8:10]):
                                continue
                            if i != 0 and int(values['date'][8:10]) > 24:
                                values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) + relativedelta(
                                    months=1) + relativedelta(day=1))
                            if i != 0:
                                values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) + relativedelta(
                                    months=values['interval']))
                                values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) - relativedelta(
                                    days=(int(values['date'][8:10])) - 1))
                                if date(int(values['date'][0:4]), int(values['date'][5:7]),
                                        int(values['date'][8:10])).weekday() != 6:
                                    values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) -
                                                         relativedelta(days=(
                                                             date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                                  int(values['date'][8:10]))).weekday()))
                                else:
                                    values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1))
                            if values['byday'] == '1':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '2':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '3':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '4':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '5' or values['byday'] == '-1':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)

                else:
                    if values['month_by'] == 'date':
                        date_diff = date(int(values['final_date'][0:4]), int(values['final_date'][5:7]),
                                         int(values['final_date'][8:10])) - \
                                    date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10]))
                        Final_Date = str(
                            date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10])))
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) - relativedelta(
                            days=(int(values['date'][8:10]))))
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(days=values['day']))

                        i = 0
                        for i in range(0, int(date_diff.days / 30), values['interval']):
                            if i != 0 or (i == 0 and int(Final_Date[8:10]) < int(values['date'][8:10])):
                                new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) + relativedelta(months=i)
                                super(OnlineAdjustmentt, self).create(new_values)
                        if int(Final_Date[8:10]) > int(values['date'][8:10]):
                            new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                      int(values['date'][8:10])) + relativedelta(
                                months=i + values['interval'])
                            super(OnlineAdjustmentt, self).create(new_values)
                    else:
                        date_diff = date(int(values['final_date'][0:4]), int(values['final_date'][5:7]),
                                         int(values['final_date'][8:10])) - \
                                    date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10]))
                        Final_Date = str(
                            date(int(values['date'][0:4]), int(values['date'][5:7]), int(values['date'][8:10])))
                        values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) - relativedelta(
                            days=(int(values['date'][8:10])) - 1))

                        counter = 0
                        if int(Final_Date[8:10]) > int(values['date'][8:10]):
                            counter = 1

                        for i in range(0, int(int(date_diff.days / 30) / values['interval']) + counter):
                            if i == 0 and int(Final_Date[8:10]) > int(values['date'][8:10]):
                                continue
                            if i != 0 and int(values['date'][8:10]) > 24:
                                values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) + relativedelta(
                                    months=1) + relativedelta(day=1))
                            if i != 0:
                                values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) + relativedelta(
                                    months=values['interval']))
                                values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                          int(values['date'][8:10])) - relativedelta(
                                    days=(int(values['date'][8:10])) - 1))
                                if date(int(values['date'][0:4]), int(values['date'][5:7]),
                                        int(values['date'][8:10])).weekday() != 6:
                                    values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) -
                                                         relativedelta(days=(
                                                             date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                                  int(values['date'][8:10]))).weekday()))
                                else:
                                    values['date'] = str(date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1))
                            if values['byday'] == '1':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '2':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 7)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '3':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 14)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '4':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 21)
                                    super(OnlineAdjustmentt, self).create(new_values)
                            if values['byday'] == '5' or values['byday'] == '-1':
                                if values['week_list'] == 'MO':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=0 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=1 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'WE':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=2 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'TH':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=3 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'FR':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=4 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SA':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=5 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)
                                if values['week_list'] == 'SU':
                                    new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                              int(values['date'][8:10])) + relativedelta(days=6 + 28)
                                    super(OnlineAdjustmentt, self).create(new_values)

            elif values['rrule_type'] == 'yearly':
                if values['end_type'] == 'count':
                    for i in range(0, values['count'], values['interval']):
                        new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(months=(12 * i))
                        super(OnlineAdjustmentt, self).create(new_values)
                else:
                    date_diff = relativedelta(date(int(values['final_date'][0:4]), int(values['final_date'][5:7]),
                                                   int(values['final_date'][8:10])),
                                              date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                   int(values['date'][8:10])))
                    for i in range(0, date_diff.years, values['interval']):
                        new_values['date'] = date(int(values['date'][0:4]), int(values['date'][5:7]),
                                                  int(values['date'][8:10])) + relativedelta(months=(12 * i))
                        super(OnlineAdjustmentt, self).create(new_values)

            values['date'] = original_date
            values['is_original'] = True
            return super(OnlineAdjustmentt, self).create(values)
        else:
            return super(OnlineAdjustmentt, self).create(values)

