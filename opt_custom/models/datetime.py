# -*- coding: utf-8 -*-

from datetime import datetime, date
from odoo import api, fields, models, _


class TimeConversation(models.Model):
    _name = 'time.conversation'
    _description = 'time.conversation'

    def convert_timestamp_UTC(record, timestamp, _date=False):
        assert isinstance(timestamp, datetime), 'Datetime instance expected'
        tz_name = record._context.get('tz') or record.env.user.tz
        self_tz = record.with_context(tz=tz_name)

        # tmp_date = datetime.strptime('2020-01-10', '%Y-%m-%d')
        if _date:
            tmp_date = datetime.strptime(date.strftime('%Y-%m-%d'), '%Y-%m-%d')
        else:
            tmp_date = fields.datetime.now().date()

        tmp_time = fields.Datetime.from_string(timestamp).time()
        timestamp = datetime.combine(tmp_date, tmp_time)

        timezone_diff = fields.Datetime.to_datetime(
            fields.Datetime.to_string(fields.Datetime.context_timestamp(self_tz, timestamp))) - timestamp

        return timestamp - timezone_diff

    def convert_timestamp_UTC(record, timestamp, _date=False, _tz_name=False, _same=False):
        assert isinstance(timestamp, datetime), 'Datetime instance expected'
        if not _tz_name:
            _tz_name = record._context.get('tz') or record.env.user.tz
        self_tz = record.with_context(tz=_tz_name)

        # tmp_date = datetime.strptime('2020-01-10', '%Y-%m-%d')
        if not _same:
            if _date:
                tmp_date = datetime.strptime(_date.strftime('%Y-%m-%d'), '%Y-%m-%d')
            else:
                tmp_date = fields.datetime.now().date()

            tmp_time = fields.Datetime.from_string(timestamp).time()
            timestamp = datetime.combine(tmp_date, tmp_time)

        timezone_diff = fields.Datetime.to_datetime(
            fields.Datetime.to_string(fields.Datetime.context_timestamp(self_tz, timestamp))) - timestamp

        return timestamp - timezone_diff

    def user_datetime_format(self):
        return self.env['res.lang']._lang_get(self.env.user.lang).date_format + " " + self.env['res.lang']._lang_get(self.env.user.lang).time_format