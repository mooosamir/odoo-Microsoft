# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from datetime import date, datetime
import dateutil.rrule as rrule
import re
from dateutil.relativedelta import relativedelta
from email.policy import default
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class ContactLens(models.Model):
    _inherit = 'spec.contact.lenses'

    outside_provider = fields.Many2one('hr.employee', string="Outside Provider", domain=[('is_outside_doctor', '=', True)])

    def import_doctor(self):
        res =  {
            'type': 'ir.actions.client',
            'name':'Import Outside Provider',
            'tag':'outside_doctor',
            'context': {'no_user_create': 1}
        }
        return res
