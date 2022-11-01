# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class ReportAppointment(models.AbstractModel):
    _name = 'report.opt_reports.appointment_services_count'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['appointment.report.wizard'].browse(docids)
        group_by_physician = {}
        if docs.group_by_physician:
            employee_ids = docs.calender_event.mapped('employee_id')
            service_types = docs.calender_event.mapped('service_type')
            for employee_id in employee_ids:
                employee_name = employee_id.name_get()[0][1] if len(employee_id.name_get()[0]) else ''
                group_by_physician[employee_name] = {}
                for service_type in service_types:
                    service_type_name = service_type.name_get()[0][1] if len(service_type.name_get()[0]) else ''
                    group_by_physician[employee_name][service_type_name] = len(docs.calender_event.filtered(lambda x: x.employee_id == employee_id and x.service_type == service_type).ids)
            # docs.calender_event.filtered(lambda x: x.)

        group_by_service = {}
        if docs.group_by_service:
            employee_ids = docs.calender_event.mapped('employee_id')
            service_types = docs.calender_event.mapped('service_type')
            for service_type in service_types:
                service_type_name = service_type.name_get()[0][1] if len(service_type.name_get()[0]) else ''
                group_by_service[service_type_name] = {}
                for employee_id in employee_ids:
                    employee_name = employee_id.name_get()[0][1] if len(employee_id.name_get()[0]) else ''
                    group_by_service[service_type_name][employee_name] = len(docs.calender_event.filtered(lambda x: x.employee_id == employee_id and x.service_type == service_type).ids)
            # docs.calender_event.filtered(lambda x: x.)

        return {
            'doc_ids': docids,
            'docs': docs,
            'o': docs[0] if len(docs) > 1 else docs,
            'doc_model': 'appointment.report.wizard',
            'report_type': data.get('report_type') if data else '',
            'currency_id': self.env['res.users'].browse(self._uid).company_id.currency_id,
            'datetime': datetime,
            'fields': fields,
            'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,
            'group_by_physician': group_by_physician,
            'group_by_service': group_by_service,
            'json':json,
        }
