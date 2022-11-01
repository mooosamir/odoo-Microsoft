# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from imp import reload
from odoo import tools
import logging
import sys

try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning(
        "The num2words python library is not installed, l10n_mx_edi features won't be fully available.")
    num2words = None


class AppointmentStatusWizard(models.TransientModel):
    _name = 'appointment.status.wizard'
    _description = 'appointment.status.wizard'

    name = fields.Char()
    code = fields.Char()


class AppointmentReportWizard(models.TransientModel):
    _name = 'appointment.report.wizard'
    _description = 'appointment.report.wizard'

    calender_event = fields.Many2many('calendar.event')

    partner_id = fields.Many2one('res.partner', default=lambda self:self.env.user.partner_id)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company.id)
    from_date = fields.Date(string='Date From', required=True)
    to_date = fields.Date(string='Date To')
    hr_employee_id = fields.Many2many('hr.employee',string='Providers')
    is_schedule_report = fields.Boolean()

    group_by_service = fields.Boolean(string="Group By Service")
    group_by_physician = fields.Boolean(string="Group By Provider")
    is_services_count = fields.Boolean()

    appointment_status = fields.Many2many('appointment.status.wizard', string="Appointment Status")
    service_type = fields.Many2many('product.template',
                                   domain="[('categ_id.name','=','Services'), ('appointment_checkbox', '=', True)]",
                                   string="Service")
    is_details_reports = fields.Boolean()

    def print_report(self):
        domain = []
        if self.is_schedule_report:
            domain = [('start_datetime', '<=', self.to_date), ('start_datetime', '>=', self.from_date),
                      ('preferred_location_id', '=', self.company_id.id)]
            if len(self.hr_employee_id.ids) > 0:
                domain.append(('employee_id', 'in', self.hr_employee_id.ids))
            self.calender_event = self.env['calendar.event'].with_context(virtual_id=False).search(domain)
            action = self.env.ref('opt_reports.report_action_appointment_schedule_report').report_action(self)
        elif self.is_services_count:
            if not self.group_by_service and not self.group_by_physician:
                self.group_by_service = True
            domain = [('start_datetime', '<=', self.to_date), ('start_datetime', '>=', self.from_date),
                      ('preferred_location_id', '=', self.company_id.id), ('appointment_status', 'not in', ['rescheduled', 'cancel'])]
            self.calender_event = self.env['calendar.event'].with_context(virtual_id=False).search(domain)
            action = self.env.ref('opt_reports.report_action_appointment_services_count').report_action(self)
        elif self.is_details_reports:
            domain = [('start_datetime', '<=', self.to_date), ('start_datetime', '>=', self.from_date),
                      ('preferred_location_id', '=', self.company_id.id)]
            if len(self.hr_employee_id.ids) > 0:
                domain.append(('employee_id', 'in', self.hr_employee_id.ids))
            if len(self.service_type.ids) > 0:
                domain.append(('service_type', 'in', self.service_type.ids))
            if len(self.appointment_status.ids) > 0:
                domain.append(('appointment_status', 'in', self.appointment_status.mapped('code')))
            self.calender_event = self.env['calendar.event'].with_context(virtual_id=False).search(domain)
            action = self.env.ref('opt_reports.report_action_appointment_details_report').report_action(self)

        action.update({'close_on_report_download': True})
        return action

    def _get_street(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.street:
            address = "%s" % (partner.street)
        if partner.street2:
            address += ", %s" % (partner.street2)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False

    def _get_address_details(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.city:
            address = "%s" % (partner.city)
        if partner.state_id.name:
            address += ", %s" % (partner.state_id.name)
        if partner.zip:
            address += ", %s" % (partner.zip)
        # if partner.country_id.name:
        #     address += ", %s" % (partner.country_id.name)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False
