# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class AppintmentReport(models.TransientModel):
    _name = "appointment.report"
    _description = "Appointment Report"

    employee_id = fields.Many2one('hr.employee', string="Provider",
                                  domain="[('appointment','=',True)]")
    date_from = fields.Date(string="From", default=fields.Date.today())
    date_to = fields.Date(string="To", default=fields.Date.today())
    docs = fields.Many2many('calendar.event')
    date_list = []

    def action_print_appointment(self):
        ctx = self._context
        data = {
            'ids': self.ids,
            'model': 'calendar.event',
            'form': self.read(['employee_id' , 'date_from', 'date_to'])[0]
        }
        if data['form'].get('date_to') < data['form'].get('date_from'):
             raise ValidationError('Please Select Valid Date')
        return self.env.ref('opt_appointment.action_report_appointment').report_action([], data=data)
