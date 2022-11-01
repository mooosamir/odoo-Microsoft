# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from math import ceil


class ReportAppointment(models.AbstractModel):
    _name = 'report.opt_appointment.report_appointment_template'

    @api.model
    def _get_report_values(self, docids, data=None):

        active_model = self.env.context.get('active_model')
        if data.get('form', False):
            employee_id = data.get('form').get('employee_id')[0]

            dt = relativedelta(hour=23, minute=59, second=59)

            date_from = fields.Datetime.to_datetime(data.get('form').get('date_from'))
            date_to = fields.Datetime.to_datetime(data.get('form').get('date_to')) + dt

            docs = self.env['calendar.event'].with_context(virtual_id=False).search([('employee_id', '=', employee_id),
                                                                                     (
                                                                                         'start_datetime', '>=',
                                                                                         date_from),
                                                                                     ('start_datetime', '<=', date_to)],
                                                                                    order="start_datetime")
            if docs:
                date_list = sorted(list({doc.start_datetime.date() for doc in docs}))
            if not docs:
                raise ValidationError(_('''No data to print!\n'''
                                        '''Please change date range (or) physician.'''))
            return {
                'doc_ids': docids,
                'docs': docs,
                'doc_model': active_model,
                'date_list': date_list,
                'list_view': False,
            }
        else:
            docs = self.env['calendar.event'].with_context(virtual_id=False).browse(docids)
            return {
                'doc_ids': docids,
                'docs': docs,
                'doc_model': 'calendar.event',
                'report_type': data.get('report_type') if data else '',
                'list_view': True
            }
