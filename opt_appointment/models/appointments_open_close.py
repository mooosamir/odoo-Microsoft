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


class AppointmentsOpenClose(models.Model):
    _name = 'appointments.open.close'
    _description = "Appointment Open Close"
    _rec_name = 'day_select'

    #            rec._get_open_close_slots()

    company_event_tz = fields.Selection('_event_tz_get', string='Timezone', related='appointments_hours_id.company_event_tz')

    day_select = fields.Selection([('mo', 'Monday'),
                                   ('tu', 'Tuesday'),
                                   ('we', 'Wednesday'),
                                   ('th', 'Thursday'),
                                   ('fr', 'Friday'),
                                   ('sa', 'Saturday'),
                                   ('su', 'Sunday')], string="Day")
    open = fields.Char(string='Open')
    opening_time = fields.Datetime('Opening Time', compute="company_local_time")
    close = fields.Char(string='Close')
    closing_time = fields.Datetime('Closing Time', compute="company_local_time")
    permanent_closed = fields.Boolean('Closed')
    appointments_hours_id = fields.Many2one('appointments.hours',
                                            string="Appointment Hour",
                                            ondelete="cascade")

    @api.depends('open', 'close')
    def company_local_time(self):
        for data in self:
            if data.open:
                open_datetime = datetime.strptime(data.open, '%I:%M %p')
                data.opening_time = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(data, open_datetime, _tz_name=data.company_event_tz)
            else:
                data.opening_time = False
            if data.close:
                close_datetime = datetime.strptime(data.close, '%I:%M %p')
                data.closing_time = timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(data, close_datetime, _tz_name=data.company_event_tz)
            else:
                data.closing_time = False

    @api.onchange('permanent_closed')
    def _onchange_permanent_closed(self):
        self.open = self.close = ""

    @api.constrains('open', 'close')
    def _check_open_close_time(self):
        for rec in self:
            open_time = "00:00"
            close_time = "24:00"
            if rec.open:
                open_time = datetime.strptime(rec.open, '%I:%M %p').strftime('%H:%M')
            if rec.close:
                close_time = datetime.strptime(rec.close, '%I:%M %p').strftime('%H:%M')
            if open_time > close_time:
                raise UserError(_('Closing time should be bigger than opening time!'))
