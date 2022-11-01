# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    is_intake_submitted = fields.Boolean(default=False)
