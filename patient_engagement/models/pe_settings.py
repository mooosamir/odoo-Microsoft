# -*- coding: utf-8 -*-

import os
import time
import pytz
from typing import re
from dateutil import tz
from twilio.rest import Client
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from twilio.base.exceptions import TwilioRestException
from ...opt_custom import models as timestamp_UTC


class Setting(models.Model):
    _name = 'pe.setting'
    _description = 'pe.setting'
    _order = "create_date DESC"
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company, copy=False)
    # Booking URL
    booking_page_link = fields.Char(string='Booking page link')
    external_booking_page_link = fields.Char(string='External booking page link')
    online_schedule = fields.Boolean(string='Auto Add Appointments from Online Scheduling', default=True)
    # Provider
    provider_id = fields.One2many('pe.setting.provider', 'setting_id', ondelete="cascade")
    # Services
    services_id = fields.One2many('pe.setting.services', 'setting_id', ondelete="cascade")
    # Calender
    # calender_id = fields.One2many('pe.setting.calender', 'setting_id', ondelete="cascade")
    calender_id = fields.One2many('online.adjustment', 'setting_id', ondelete="cascade")
    # Chat
    is_chat = fields.Boolean(string="Enable Chat")
    is_respond = fields.Boolean(string="Auto Respond")
    auto_respond_message = fields.Char(string="Auto Respond Message")
    quick_response = fields.One2many('pe.setting.chat.quick.response', 'setting_id')
    auto_response = fields.One2many('pe.setting.chat.schedule', 'setting_id')
    form_id = fields.One2many('pe.setting.form', 'setting_id')
    # Delivery Restrictions
    company_event_tz = fields.Selection('_event_tz_get', string='Timezone', related='company_id.timezone')
    is_saturday = fields.Boolean(string="Do not send messages on Saturday")
    is_sunday = fields.Boolean(string="Do not send messages on Sunday")
    from_ = fields.Char(string='From')
    from_time = fields.Datetime('From Time')
    to = fields.Char(string='to')
    to_time = fields.Datetime('TO Time')

    @api.model
    def create(self, values):
        if values.get('company_id'):
            company_event_tz = self.env['res.company'].search([('id', '=', values['company_id'])]).timezone

        if values.get('from_'):
            open_datetime = datetime.strptime(values['from_'], '%I:%M %p')
            values['from_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime,
                                                                              _tz_name=company_event_tz))
        if values.get('to'):
            close_datetime = datetime.strptime(values['to'], '%I:%M %p')
            values['to_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime,
                                                                              _tz_name=company_event_tz))

        return super(Setting, self).create(values)

    def write(self, values):
        if values.get('company_id'):
            company_event_tz = self.env['res.company'].search([('id', '=', values['company_id'])]).timezone
            if not values.get('from_'):
                values['from_'] = self.from_
            if not values.get('to'):
                values['to'] = self.to
        else:
            company_event_tz = self.company_event_tz

        if values.get('from_'):
            open_datetime = datetime.strptime(values['from_'], '%I:%M %p')
            values['from_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime,
                                                                              _tz_name=company_event_tz))
        if values.get('to'):
            close_datetime = datetime.strptime(values['to'], '%I:%M %p')
            values['to_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime,
                                                                              _tz_name=company_event_tz))

        return super(Setting, self).write(values)

    @api.constrains('open', 'close')
    def _check_open_close_time(self):
        for rec in self:
            open_time = "00:00"
            close_time = "24:00"
            if rec.from_:
                open_time = datetime.strptime(rec.from_, '%I:%M %p').strftime('%H:%M')
            if rec.to:
                close_time = datetime.strptime(rec.to, '%I:%M %p').strftime('%H:%M')
            if open_time > close_time:
                raise UserError(_('Closing time should be bigger than opening time!'))

    @api.model
    def default_get(self, fields_list):
        res = super(Setting, self).default_get(fields_list)
        provider_id = [(5, 0, 0)]
        services_id = [(5, 0, 0)]
        providers = self.env['hr.employee'].search([('appointment', '=', True), ('company_id', '=', self.env.user.company_id.id)])
        for provider in providers:
            line = (0, 0, {
                'provider_id': provider.id,
                'online_description': provider.name,
            })
            provider_id.append(line)
        services = self.env['product.template'].search([('categ_id.name','=','Services'), ('appointment_checkbox', '=', True)])
        for service in services:
            line = (0, 0, {
                'service_id': service.id,
                'online_description': service.name,
            })
            services_id.append(line)
        res.update({
            'services_id': services_id,
            'provider_id': provider_id,
        })
        return res

    @api.constrains('company_id')
    def _check_company_configration(self):
        duplicate_rec = self.search([('company_id', '=', self.company_id.id),
                                     ('id', '!=', self.id)])
        if duplicate_rec:
            raise ValidationError(_("Duplicate record found! \n"
                                    "This branch settings is already available!"))

    _sql_constraints = [(
        'pe_setting_company_unique',
        'unique(company_id)',
        'This Company already exists!'
        )]


class SettingProvider(models.Model):
    _name = 'pe.setting.provider'
    _description = 'pe.setting.provider'
    _rec_name = 'online_description'

    # is_active = fields.Boolean(string="isActive")
    sequence = fields.Integer()
    provider_id = fields.Many2one('hr.employee', string="Provider",
                                  domain="[('appointment', '=', True), ('company_id', '=', company_id)]")
    online_description = fields.Char(string="Online Description")
    show_online = fields.Boolean(string="Show Online", default=False)

    setting_id = fields.Many2one('pe.setting', ondelete="cascade")
    company_id = fields.Many2one('res.company', related="setting_id.company_id")
    # schedule_id = fields.One2many('pe.setting.provider.schedule', 'provider_id', ondelete="cascade")

    @api.onchange('service_id')
    def _onchange_provider_id(self):
        for data in self:
            data.online_description = data.provider_id.name

    def action_schedule_form_view(self):
        form = self.env.ref('patient_engagement.pe_setting_provider_for_schedule_form')
        return {
            'name': _('Schedule'),
            'res_model': 'pe.setting.provider',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': [(form and form.id)],
            'views': [(form and form.id, 'form')],
            # 'view_ids': form_view_id,
            'target': 'new',
        }


class SettingServices(models.Model):
    _name = 'pe.setting.services'
    _description = 'pe.setting.services'
    _rec_name = 'online_description'

    # is_active = fields.Boolean(string="isActive")
    service_id = fields.Many2one('product.template', string="Service",
                                 domain="[('categ_id.name','=','Services'), ('appointment_checkbox', '=', True)]")
    online_description = fields.Char(string="Online Description")
    show_online = fields.Boolean(string="Show Online", default=False)
    # duration = fields.Char(string="Duration", readonly="1", compute="_onchange_service_type")
    setting_id = fields.Many2one('pe.setting', ondelete="cascade")

    @api.onchange('service_id')
    def _onchange_service_id(self):
        for data in self:
            data.online_description = data.service_id.name

    # @api.onchange('service_id')
    # def _onchange_service_type(self):
    #     for data in self:
    #         if data.service_id:
    #             data.duration = data.service_id.duration
    #         # self.duration = (divmod(float(self.service_id.duration), 60))[1]/60


class SettingChatAutoResponseSchedule(models.Model):
    _name = 'pe.setting.chat.schedule'
    _description = 'pe.setting.chat.schedule'
    _rec_name = 'day_select'

    company_event_tz = fields.Selection('_event_tz_get', string='Timezone', related='setting_id.company_id.timezone')

    day_select = fields.Selection([('mo', 'Monday'),
                                   ('tu', 'Tuesday'),
                                   ('we', 'Wednesday'),
                                   ('th', 'Thursday'),
                                   ('fr', 'Friday'),
                                   ('sa', 'Saturday'),
                                   ('su', 'Sunday')], string="Day")
    open = fields.Char(string='Start')
    opening_time = fields.Datetime('Opening Time', compute="company_local_time")
    close = fields.Char(string='End')
    closing_time = fields.Datetime('Closing Time', compute="company_local_time")
    setting_id = fields.Many2one('pe.setting', ondelete="cascade")

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


class SettingChatQuickResponse(models.Model):
    _name = 'pe.setting.chat.quick.response'
    _description = 'pe.setting.chat.quick.response'
    # _rec_name = 'day_select'

    name = fields.Char(string="Name")
    message = fields.Char(string="Message")
    setting_id = fields.Many2one('pe.setting', ondelete="cascade")


class SettingForm(models.Model):
    _name = 'pe.setting.form'
    _description = 'pe.setting.form'

    name = fields.Char(string="Intake Form Name")
    welcome_message = fields.Text(string="Welcome Message")
    completed_message = fields.Text(string="Completed Message")
    setting_id = fields.Many2one('pe.setting', ondelete="cascade")
    appointment_selection_id = fields.Many2one('product.template', string="Appointment Selection",
                                 domain="[('categ_id.name','=','Services'), ('appointment_checkbox', '=', True)]")
    form_selection_ids = fields.One2many('pe.setting.form.selection', 'form_id')
    company_id = fields.Many2one('res.company', related="setting_id.company_id")

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(SettingForm, self).default_get(fields_list)
    #     model = []
    #     model_ids = self.env['ir.model'].search([('model', 'in', ['res.partner','spec.insurance'])])
    #     pe_setting_form_selection_id = self.env['pe.setting.form.selection']
    #     pe_setting_form_selection_fields_id = self.env['pe.setting.form.selection.fields']
    #     for data in model_ids:
    #         if data.id == model_ids[0].id:
    #             model_fields_id = self.env['ir.model.fields'].search([('model_id', '=', data.id),
    #                                                                   ('name', 'in',
    #                                                                    ['first_name', 'middle_name', 'last_name',
    #                                                                     'date_of_birth',
    #                                                                     'ssn', 'street', 'street2', 'city', 'state_id',
    #                                                                     'zip', 'phone', 'email',
    #                                                                     'email', 'marital_status', 'occupation',
    #                                                                     'emergency_name', 'emergency_phone'])])
    #
    #             form_selection_id = pe_setting_form_selection_id.create({'ir_model_id': data.id, 'model_name': data.name})
    #             for datas in model_fields_id:
    #                 pe_setting_form_selection_fields_id.create(
    #                     {'model_fields_id': datas.id, 'form_selection_id': form_selection_id.id})
    #             model.append(form_selection_id.id)
    #
    #         elif data.id == model_ids[1].id:
    #             model_fields_id = self.env['ir.model.fields'].search([('model_id', '=', data.id),
    #                                                                   ('name', 'in', ['carrier_id', 'sequence', 'name',
    #                                                                     'date', 'image_front', 'image_back'])])
    #             form_selection_id = pe_setting_form_selection_id.create({'ir_model_id': data.id,'model_name':data.name + " (Vision)"})
    #             for datas in model_fields_id:
    #                 pe_setting_form_selection_fields_id.create(
    #                     {'model_fields_id': datas.id, 'form_selection_id': form_selection_id.id})
    #             model.append(form_selection_id.id)
    #
    #             form_selection_id = pe_setting_form_selection_id.create({'ir_model_id': data.id, 'model_name': data.name + " (Medical)"})
    #             for datas in model_fields_id:
    #                 pe_setting_form_selection_fields_id.create(
    #                     {'model_fields_id': datas.id, 'form_selection_id': form_selection_id.id})
    #             model.append(form_selection_id.id)
    #
    #     res.update({
    #         'form_selection_ids': model,
    #     })
    #     return res

    _sql_constraints = [(
        'pe_setting_form_appointment_selection_id_unique',
        'unique(company_id,appointment_selection_id)',
        'This Appointment Selection already exists for this company!'
        )]


class SettingFormSelection(models.Model):
    _name = 'pe.setting.form.selection'
    _description = 'pe.setting.form.selection'
    _order = "sequence"

    model_name = fields.Char(string="Name")
    ir_model_id = fields.Many2one('ir.model', string="Form Model")
    ir_model_model = fields.Char(related="ir_model_id.model")

    sequence = fields.Integer()
    form_id = fields.Many2one('pe.setting.form', ondelete="cascade")
    model_fields_ids = fields.One2many('pe.setting.form.selection.fields', 'form_selection_id', ondelete="cascade")
    acs_consent_form_template_ids = fields.Many2many('acs.consent.form.template')
    company_id = fields.Many2one('res.company', related="form_id.setting_id.company_id")

    # acs.consent.form.template
    # def open_model_fields_id(self):
    #     return {
    #         'res_model': 'pe.setting.form.selection',
    #         'type': 'ir.actions.act_window',
    #         'views': [(self.env.ref("patient_engagement.pe_setting_form_selection_fields_form_02").id, 'form')],
    #         'target': 'new',
    #         'res_id': self.id,
    #     }

    _sql_constraints = [(
        'pe_setting_form_selection_model_id_unique',
        'unique(form_id,ir_model_id)',
        'This Model already defined for this form.'
        )]


class SettingFormSelectionFields(models.Model):
    _name = 'pe.setting.form.selection.fields'
    _description = 'pe.setting.form.selection.fields'
    _order = "sequence"

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    form_selection_id = fields.Many2one('pe.setting.form.selection')
    form_selection_name = fields.Many2one('ir.model', string="Form Model", related="form_selection_id.ir_model_id")
    model_fields_id = fields.Many2one('ir.model.fields', string='Field', ondelete="cascade")
    sequence = fields.Integer()
    name = fields.Char()
