# -*- coding: utf-8 -*-

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError
from odoo.addons.base.models.res_partner import _tz_get
from ...opt_custom import models as timestamp_UTC


class CompanyOpenClose(models.Model):
    _name = 'company.open.close'
    _description = "company Open Close"
    _rec_name = 'day_select'

    day_select = fields.Selection([('mo', 'Monday'),
                                   ('tu', 'Tuesday'),
                                   ('we', 'Wednesday'),
                                   ('th', 'Thursday'),
                                   ('fr', 'Friday'),
                                   ('sa', 'Saturday'),
                                   ('su', 'Sunday')], string="Day")
    open = fields.Char(string='Open')
    opening_time = fields.Datetime('Opening Time')
    close = fields.Char(string='Close')
    closing_time = fields.Datetime('Closing Time')
    permanent_closed = fields.Boolean('Closed')
    company_id = fields.Many2one('res.company',
                                string="Company Hour",
                                ondelete="cascade", default=lambda self: self.env.company_id)

    @api.model
    def create(self, values):
        if values.get('open'):
            open_datetime = datetime.strptime(values['open'], '%I:%M %p')
            values['opening_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime))
        if values.get('close'):
            close_datetime = datetime.strptime(values['close'], '%I:%M %p')
            values['closing_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime))
        return super(CompanyOpenClose, self).create(values)

    def write(self, values):
        if values.get('open'):
            open_datetime = datetime.strptime(values['open'], '%I:%M %p')
            values['opening_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime))
        if values.get('close'):
            close_datetime = datetime.strptime(values['close'], '%I:%M %p')
            values['closing_time'] = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime))
        return super(CompanyOpenClose, self).write(values)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        new_opening_time = new_closing_time = ''

        if self.open:
            open_datetime = datetime.strptime(self.open, '%I:%M %p')
            new_opening_time = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, open_datetime))
        if self.close:
            close_datetime = datetime.strptime(self.close, '%I:%M %p')
            new_closing_time = fields.Datetime.to_string(
                timestamp_UTC.datetime.TimeConversation.convert_timestamp_UTC(self, close_datetime))

        self.ensure_one()
        default = dict(default or {},
                       opening_time=new_opening_time,
                       closing_time=new_closing_time)
        res = super(CompanyOpenClose, self).copy(default=default)
        return res

    @api.onchange('permanent_closed')
    def _onchange_permanent_closed(self):
        self.open = self.close = ""


class ResCompnay(models.Model):
    _inherit = "res.company"

    npi = fields.Char(string="NPI")
    contact_person = fields.Char(string="Contact Person")
    provide = fields.Many2one('hr.employee', string='Provider')
    timezone = fields.Selection(_tz_get, string='Timezone')
    dst_observed = fields.Boolean(string="DST Observed")
    main = fields.Boolean(string="Main")
    region_ids = fields.Many2many('spec.region', 'company_region_rel', 'company_id', 'region_id', string="Region")
    hours = fields.Many2one(
        'resource.calendar', string="Hours")
    active = fields.Boolean(string="Active", default=True)
    fax = fields.Char(string="Fax")
    tax_ids = fields.One2many('account.tax', 'company_id', string='Taxes')
    clia = fields.Char(string="CLIA")
    location_code = fields.Char(string="Location Code")
    hl7_code = fields.Char(string="HL7 Code")
    google_maps = fields.Char(string="Google Maps")
    rx_expiration_lens = fields.Selection([('1', '1 Year'),
                                           ('2', '2 Year'),
                                           ('3', '3 Year')], string='Rx Expiration Lens')
    rx_expiration_contacts = fields.Selection([('1', '1 Year'),
                                           ('2', '2 Year'),
                                           ('3', '3 Year')], string='Rx Expiration Contacts')
    print_doctor_recommendation = fields.Boolean(string="Print Provider Recommendation", default = True)
    notes = fields.Text('Default Terms and Conditions')
    default_lab = fields.Many2one('res.partner', string='Default Lab', domain="[('is_lab', '=', True)]")

    def update_company(self, company_id):
        self.env.user.update({
            'company_id': int(company_id)
        })

    @api.constrains('main')
    def check_main(self):
        if self.main:
            company_id = self.env['res.company'].search([('id', '!=', self._origin.id), ('main', '=', True)])
            if company_id:
                    raise Warning(_('%s company is allready main.' % (company_id.name)))

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone and self.phone.isdigit():
            if len(self.phone) >= 10:
                self.phone = '({}) {}-{}'.format(self.phone[:3], self.phone[3:6], self.phone[6:])

    @api.onchange('fax')
    def _onchange_fax(self):
        if self.fax and self.fax.isdigit():
            if len(self.fax) >= 10:
                self.fax = '({}) {}-{}'.format(self.fax[:3], self.fax[3:6], self.fax[6:])


class AccountTax(models.Model):
    _inherit = "account.tax"

    is_sale = fields.Boolean(string="Sale")
    is_purchase = fields.Boolean(string="Purchase")


