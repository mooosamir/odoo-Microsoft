# -*- coding: utf-8 -*-

import pytz
from typing import re
from dateutil import tz
from datetime import datetime, date
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from ...opt_custom import models as timestamp_UTC
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.res_partner import _tz_get


class AppointmentsHours(models.Model):
    _name = 'appointments.hours'
    _description = "Appointment Hours"
    _rec_name = 'default_view'

    company_event_tz = fields.Selection('_event_tz_get', string='Timezone', related='company_id.timezone')

    appointments_close_open_ids = fields.One2many('appointments.open.close',
                                                  'appointments_hours_id',
                                                  string="Appointment Close/Open")
    default_view = fields.Selection([('week', 'Weekly'),
                                     ('day', 'Daily')], string="Default View")
    duration_block = fields.Selection([('10', '10'),
                                       ('15', '15'),
                                       ('20', '20'),
                                       ('25', '25'),
                                       ('30', '30')], string="Duration Block")
    closed_color = fields.Char(string="Closed")
    available_color = fields.Char(string="Available")
    holiday_color = fields.Char(string="Holiday")
    hide_saturday = fields.Boolean(string="Hide Saturday")
    hide_sunday = fields.Boolean(string="Hide Sunday")
    appointments_holidays_ids = fields.One2many('appointments.holidays', 'appointments_hours_id',
                                                string="Appointment Holidays")
    company_id = fields.Many2one('res.company',
                                 string='Company',
                                 default=lambda self: self.env.company.id,
                                 required=True)

    def get_appointment_hours_details(self, day):
        if day == 1:
            day = 'mo'
        elif day == 2:
            day = 'tu'
        elif day == 3:
            day = 'we'
        elif day == 4:
            day = 'th'
        elif day == 5:
            day = 'fr'
        elif day == 6:
            day = 'sa'
        elif day == 7:
            day = 'su'

        resources = []
        today = self.search([('company_id', '=', self.env.company.id), ('appointments_close_open_ids.day_select', '=', day)], limit = 1)
        if today.default_view == 'week':
            opening_time = min(today.appointments_close_open_ids.filtered(lambda x: x.permanent_closed != 1).mapped('opening_time'))
            closing_time = max(today.appointments_close_open_ids.filtered(lambda x: x.permanent_closed != 1).mapped('closing_time'))
            permanent_closed = 0 if len(today.appointments_close_open_ids.filtered(lambda x: x.permanent_closed != 1)) > 0 else 1
        else:
            opening_time = today.appointments_close_open_ids.filtered(lambda x: x.day_select == day).opening_time
            closing_time = today.appointments_close_open_ids.filtered(lambda x: x.day_select == day).closing_time
            permanent_closed = today.appointments_close_open_ids.filtered(lambda x: x.day_select == day).permanent_closed

        for data in today:
            resources.append({
                'opening_time': opening_time and (
                                fields.Datetime.context_timestamp(data.with_context(tz=data.company_event_tz),
                                                                  datetime.strptime(str(opening_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '00:00:00',
                'closing_time': closing_time and (
                                fields.Datetime.context_timestamp(data.with_context(tz=data.company_event_tz),
                                                                  datetime.strptime(str(closing_time),
                                                                                    DEFAULT_SERVER_DATETIME_FORMAT))).time() or '23:59:59',
                'permanent_closed': permanent_closed,
                'duration_block': data.duration_block,
                'default_view': data.default_view,
                'hide_saturday': data.hide_saturday,
                'hide_sunday': data.hide_sunday
            })
        return resources

    @api.constrains('company_id')
    def _check_company_configration(self):
        duplicate_rec = self.search([('company_id', '=', self.company_id.id),
                                     ('id', '!=', self.id)])
        if duplicate_rec:
            raise ValidationError(_("Duplicate record found! \n"
                                    "This branch appointment configuration is already available!"))
