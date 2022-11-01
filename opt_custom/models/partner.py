# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError, Warning
from datetime import date, datetime
import dateutil.rrule as rrule
import re
from dateutil.relativedelta import relativedelta
from email.policy import default
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lab = fields.Boolean(string="Is Lab")

    @api.depends('first_name', 'middle_name', 'last_name', 'street')
    def _display_partner_name(self):
        for rec in self:
            name_list = []
            if rec.first_name:
                name_list.append(rec.first_name or '')
            if rec.middle_name:
                name_list.append(rec.middle_name or '')
            if rec.last_name:
                name_list.append(rec.last_name or '')
            name = ' '.join(name_list)
            rec.update({'name': name})

    annual_recall_kanban = fields.Char(compute="compute_annual_recall_kanban")

    def compute_annual_recall_kanban(self):
        for data in self:
            count = 0
            data.annual_recall_kanban = "Recall Date: N/A"
            for records in data.recall_type_ids:
                # if records.name.name == "Annual Exam":
                count += 1
                if count == 1:
                    data.annual_recall_kanban = ""
                data.annual_recall_kanban += (
                                                 records.name.name if records.name.name else 'N/A') + " " + records.next_recall_date.strftime(
                    '%m/%d/%Y') + "<br/>"

    formatted_phone = fields.Char(compute='_formatted_phone_number', store=True)

    @api.depends('phone')
    def _formatted_phone_number(self):
        for data in self:
            if data.phone:
                data.formatted_phone = "+" + str(data.country_id.phone_code) + data.phone.replace('-', '').replace(' ',
                                                                                                                   '').replace(
                    '(', '').replace(')', '').replace('+', '')

    # balance = fields.Monetary(string="Balance", compute="_balance")
    name = fields.Char(string="Name", required=False, readonly=False,
                       compute="_display_partner_name", store=True, copy=False)
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")
    nick_name = fields.Char(string="Nickname")
    title = fields.Selection([('mr', 'Mr'), ('mrs', 'Mrs'), ('ms', 'Ms'), ('miss', 'Miss'), ('mx', 'Mx')],
                             string="Title")
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Char(compute="_get_age", string="Age")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),
                               ('unspecified', 'Unspecified')], string="Gender")
    gender_identification = fields.Selection(
        [('identifies_as_male', 'Identifies as Male'), ('identifies_as_female', 'Identifies as Female'),
         ('ftm_transgender_male', 'Female-to-Male (FTM)/Transgender Male'),
         ('mtf_transgender_female', 'Male-to-Female (MTF)/Transgender Female'),
         ('identifies_conforming_gender', 'Identifies as non-conforming gender'),
         ('additional_gender_category_other,', 'Additional gender category or other,'),
         ('choose_not_disclose', 'Choose not to disclose')
         ], string="Gender Identification")
    suffix = fields.Selection([('jr', 'Jr'), ('sr', 'Sr'), ('i', 'I'), ('ii', 'II'),
                               ('iii', 'III'), ('iv', 'IV'), ('v', 'V'), ('vi', 'VI'),
                               ('esq', 'Esq'), ('cpa', 'CPA'),
                               ('dc', 'DC'), ('dds', 'DDS'),
                               ('vm', 'VM')], string="Suffix")
    ssn = fields.Char(string="SSN")
    other = fields.Char(string="Other")
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'),
                                       ('Divorced', 'Divorced'), ('widowed', 'Widowed')], string="Marital Status")
    communication_preferences = fields.Selection([('email', 'Email'), ('phone', 'Phone'), ('cell', 'Cell'), ],
                                                 string="Preferred Contact Method")
    preferred_language = fields.Selection(
        [('declined_to_Specify', 'Declined to Specify'), ('unspecified', 'Unspecified'),
         ('english', 'English'), ('spanish', 'Spanish'), ('french', 'French'),
         ('german', 'German')], string="Preferred Language")
    relationship_to_patient = fields.Selection(
        [('father', 'Father'), ('mother', 'Mother'), ('son', 'Son'), ('daughter', 'Daughter'), ('husband', 'Husband'),
         ('wife', 'Wife'),
         ('partner', 'Partner'), ('parent', 'Parent'), ('sibling', 'Sibling'), ('other', 'Other')],
        string="Relationship to Patient")
    hipaa_sign = fields.Boolean(string="Signature on file")
    date = fields.Date(string="Date")
    provide = fields.Many2one('hr.employee', string='Preferred Provider')
    partner_id = fields.Many2one('res.partner', string='Responsible Party')

    # preferred_location = fields.Many2one('res.company', string='Location', default=lambda self: self.env.user.company_id)
    company_id = fields.Many2one('res.company', index=True, string='Location',
                                 default=lambda self: self.env.user.company_id)

    deceased = fields.Boolean(string="Deceased")
    patient = fields.Boolean(string="Patient")
    country_id = fields.Many2one('res.country', string="Country")
    document_ids = fields.One2many('multi.images', 'partner_id', string="Attachment")
    notes_ids = fields.One2many('spec.notes', 'partner_id', string="Notes")
    recall_type_ids = fields.One2many('spec.recall.type.line', 'partner_id', string="Recall Type")
    next_recall = fields.Date(string="Next Recall")
    family_ids = fields.Many2many('res.partner', 'res_partner_rel', 'partner_id', 'res_id', string='Family')
    family_partner_id = fields.Many2one('res.partner', string='Responsible Party')
    update_label_address = fields.Boolean(string="Update Label Address")
    update_label_cell = fields.Boolean(string="Update Label cell")
    update_label_other = fields.Boolean(string="Update Label other")
    disabled_email = fields.Boolean(string="Disabled email")
    contact_lens_ids = fields.One2many('spec.contact.lenses', 'partner_id', string="Rx")
    occupation = fields.Char(string="Occupation")
    ethnicity = fields.Selection([('declined_to_Specify', 'Declined to Specify'),
                                  ('american_indian_Alaska_native', 'American Indian or Alaska Native'),
                                  ('asian', 'Asian'), ('black_or_african_american', 'Black or African American'),
                                  ('native _pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
                                  ('white', 'White')], string="Ethnicity")
    race = fields.Selection([('declined', 'Declined'), ('american_indian', 'American Indian'), ('asian', 'Asian'),
                             ('native _pacific_islander', 'Native Hawaiian or Other Pacific Islander'),
                             ('black_or_african_american', 'Black or African American'),
                             ('white', 'White'), ('other', 'Other')], string="Race")
    referred_by_id = fields.Many2one('spec.referred.by', string="Referred By")
    emergency_name = fields.Char(string="Emergency Name")
    emergency_phone = fields.Char(string="Emergency Phone")
    select_all = fields.Boolean(string='Select all')
    communication_ids = fields.One2many('spec.communication.table', 'partner_id', string="Communication Method")
    assign_as_emergency_contact = fields.Boolean(string='Assign As Emergency Contact')
    assign_as_responsible_party = fields.Boolean(string='Assign As Responsible Party')
    family_street = fields.Char(string="Street")
    family_street2 = fields.Char(string="Street2")
    family_city = fields.Char(string="City")
    family_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    family_zip = fields.Char(string="ZIP")
    family_country_id = fields.Many2one('res.country', string="Country")
    account_balance = fields.Char(string="Account Balance")
    last_exam = fields.Char(string="Last Exam", compute="_onchange_last_exam")
    same_as_patient = fields.Boolean(string="Same as Patient")
    actual_patien_id = fields.Many2one('res.partner', 'Actual Patient')
    doctor_type = fields.Selection([('doctor', 'Provider'),
                                    ('out_doctor', 'Out Side Provider')], string="Provider Type")
    npi = fields.Char(string="NPI")
    bill_acct_number = fields.Char('Bill Account Number')
    ship_acct_number = fields.Char('Ship Account Number')

    # @api.onchange('deceased')
    # def disable_active(self):
    #     if self.deceased:
    #         self.active = False
    #     else:
    #         self.active = True

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if not res.disabled_email:
            if not self.env.context.get(MODULE_UNINSTALL_FLAG, False):
                user_vals = {'name': vals.get('name', '')}
                vals = {
                    'company_id': self.env.company.id,
                    'name': res.name_get()[0][1] if res.name_get() and len(res.name_get()) > 0 else res.name,
                    'login': res.name_get()[0][1] if res.name_get() and len(res.name_get()) > 0 else res.name,
                    'email': res.email,
                    'partner_id': res.id,
                    'patient': True,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
                }
                users = self.env['res.users'].sudo().create(vals)
                # new_user = user_obj.new(user_vals)
                # user_vals.update(new_user.with_context(is_user=True).default_get(new_user._fields))
                # user_obj.create(user_vals)
                portal_user_group = self.env.ref('base.group_portal')
                if self.env.context.get('is_import'):
                    user_vals.update({'doctor_type': 'out_doctor'})
        return res

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if self._context.get('from_edit_claim') and self._context.get('active_id'):
            claim_rec = self.env['claim.manager'].browse(self._context.get('active_id'))
            claim_rec._onchange_lang_localization()

        if not self.env.context.get(MODULE_UNINSTALL_FLAG, False):
            pass
            # user_flag = False
            # seq_obj = self.env['ir.sequence']
            # login_user = ''
            # if vals.get('email') and len(vals.get('email')) == 0:
            #     seq_no = seq_obj.next_by_code('patient.profile.login') or 'New'
            #     login_user = seq_no
            #     user_flag = True
            # elif vals.get('email'):
            #     login_user = vals.get('email', '')
            #     user_flag = True
            #
            # if user_flag:
            #     user_obj = self.env['res.users']
            #     user = user_obj.search([('partner_id', '=', self.id)], limit=1)
            #     if user:
            #         portal_user_group = self.env.ref('base.group_portal')
            #         user_vals = ({
            #                       'name': self.name,
            #                       'login':login_user,
            #                       'groups_id': [(4, portal_user_group.id)],
            #                       })
            #         user.write(user_vals)
            #     else:
            #         user_vals = {'name': self.name}
            #         new_user = user_obj.new(user_vals)
            #         user_vals.update(new_user.default_get(new_user._fields))
            #         portal_user_group = self.env.ref('base.group_portal')
            #         user_vals.update({
            #                           'login':login_user,
            #                           'groups_id': [(4, portal_user_group.id)],
            #                           'partner_id':self.id
            #                           })
            #         user_obj.create(user_vals)
        return res

    def action_send_mail_user(self):
        self.ensure_one()
        if not self.email:
            return {
                'name': _('Add Email'),
                'view_mode': 'form',
                'res_model': 'update.email.patient.profile',
                'view_id': self.env.ref('opt_custom.update_email_patient_profile_form').id,
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
        else:
            user = self.env['res.users'].search([('partner_id', '=', self.id)], limit=1)
            user.action_reset_password()

    @api.onchange('is_company')
    def _onchange_is_company(self):
        if self.patient and self.is_company:
            self.company_type = 'person'

    @api.onchange('last_exam')
    def _onchange_last_exam(self):
        for res in self:
            calendar_event_id = self.env['calendar.event'].with_context(virtual_id=False).search([('patient_id', '=', res.id),
                                                                   ('appointment_status', '=', 'none')],
                                                                  limit=1, order="start_datetime desc")
            if not calendar_event_id.id:
                res.last_exam = "-"
            elif calendar_event_id.local_start_datetime:
                res.last_exam = calendar_event_id.local_start_datetime
            else:
                res.last_exam = calendar_event_id.start_datetime

    # @api.onchange('account_balance')
    # def _onchange_account_balance(self):
    #     for res in self:
    #         if res.patient_balance:
    #             res.account_balance = "$ " + "{:.2f}".format(res.patient_balance)

    @api.onchange('hipaa_sign')
    def _onchange_hipaa_sign(self):
        if self.hipaa_sign:
            self.date = fields.Date.today()
        else:
            self.date = False

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone and self.phone.isdigit():
            if len(self.phone) >= 10:
                self.phone = '({}) {}-{}'.format(self.phone[:3], self.phone[3:6], self.phone[6:])

    @api.onchange('emergency_phone')
    def _onchange_emergency_phone(self):
        if self.emergency_phone and self.emergency_phone.isdigit():
            if len(self.emergency_phone) >= 10:
                self.emergency_phone = '({}) {}-{}'.format(self.emergency_phone[:3], self.emergency_phone[3:6],
                                                           self.emergency_phone[6:])

    @api.onchange('other')
    def _onchange_other(self):
        if self.other and self.other.isdigit():
            if len(self.other) >= 10:
                self.other = '({}) {}-{}'.format(self.other[:3], self.other[3:6], self.other[6:])

    @api.onchange('street', 'street2', 'city', 'state_id', 'zip', 'country_id')
    def _onchange_street(self):
        if self.family_ids.ids:
            for family_ids in self.family_ids.ids:
                family_id = self.env['res.partner'].browse(family_ids)
                family_id.street = self.street or ''
                family_id.street2 = self.street2 or ''
                family_id.city = self.city or ''
                family_id.state_id = self.state_id or ''
                family_id.zip = self.zip or ''
                family_id.country_id = self.country_id or ''

    @api.onchange('disabled_email')
    def _onchange_disabled_email(self):
        if self.disabled_email:
            self.email = False

    @api.onchange('select_all')
    def _onchange_select_all(self):
        for communication_id in self.communication_ids:
            if self.select_all:
                communication_id.text = True
                communication_id.cell = True
                communication_id.email = True
                communication_id.mail = True
                communication_id.opt_out = False
            else:
                communication_id.text = False
                communication_id.cell = False
                communication_id.email = False
                communication_id.mail = False

    @api.model
    def default_get(self, fields):
        defaults = super(ResPartner, self).default_get(fields)
        if not self._context.get('is_user'):
            country_id = self.env.ref('base.us')
            defaults['country_id'] = country_id.id
            defaults['select_all'] = True
            communication_list = ['Appointment', 'Recall', 'Order Pick-up', 'General']
            dic_list = []
            for communication in communication_list:
                dic_list.append((0, 0, {'communication': communication}))
            defaults['communication_ids'] = dic_list
        return defaults

    @api.depends('date_of_birth', )
    def _get_age(self):
        """Age Method"""
        for record in self:
            record.age = '0 y 0 m'
            if record.date_of_birth:
                age = relativedelta(date.today(), datetime.strptime(
                    str(record.date_of_birth), "%Y-%m-%d").date())
                record.age = str(age.years) + ' y ' + \
                             str(age.months) + ' m'

    @api.constrains('email')
    def check_email(self):
        for rec in self:
            if rec.email:
                match = re.match(
                    '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', rec.email)
                if not match:
                    raise ValidationError('Please Enter Valid Email')

    @api.constrains('ssn')
    def check_last_char(self):
        total_size = 0
        if self.ssn:
            total_size = len(self.ssn)
            if total_size == 9:
                self.ssn = '{}-{}-{}'.format(self.ssn[:3],
                                             self.ssn[3:5], self.ssn[5:])
            ssn = str(self.ssn).split('-')
            for total_char in ssn:
                total_size = len(total_char)
            if total_size != 4 and total_size != 9:
                raise ValidationError(
                    _("Please update SSN field to either 4 or 9 digits"))

    @api.onchange('same_as_patient')
    def _onchange_same_as_patient(self):
        if self._context.get('default_actual_patient_id'):
            if not self.actual_patien_id:
                self.actual_patien_id = self._context.get('default_actual_patient_id')
        if self.same_as_patient:
            if not self.actual_patien_id:
                raise exceptions.Warning("You need to save record to use this option.")
            self.family_street = self.actual_patien_id.street
            self.family_street2 = self.actual_patien_id.street2
            self.family_city = self.actual_patien_id.city
            self.family_state_id = self.actual_patien_id.state_id
            self.family_zip = self.actual_patien_id.zip
            self.family_country_id = self.actual_patien_id.country_id
        else:
            self.family_street = False
            self.family_street2 = False
            self.family_city = False
            self.family_state_id = False
            self.family_zip = False
            self.family_country_id = False

    @api.onchange('family_ids')
    def _onchange_family_ids(self):
        if self.family_ids.ids:
            if not self.ids:
                raise exceptions.Warning("You need to save the patient to add family members.")
            for family_ids in self.family_ids.ids:
                family_id = self.env['res.partner'].browse(family_ids)
                if family_id.assign_as_emergency_contact:
                    self.emergency_name = family_id.name
                    self.emergency_phone = family_id.phone
                if family_id.assign_as_responsible_party:
                    self.partner_id = family_id
                self.delete_family_ids_relation()
                family_id = self.env['res.partner'].browse(family_ids)
                family_id.family_ids = [(4, self.ids[0])]
        else:
            self.delete_family_ids_relation()

    def delete_family_ids_relation(self):
        if len(self.ids) > 0:
            family_ids = self.env['res.partner'].search([]).filtered(lambda x: self.ids[0] in x.family_ids.ids)
            for family_id in family_ids:
                family_id.family_ids = [(3, self.ids[0])]

    @api.constrains('communication_preferences', 'email')
    def check_communication_preferences_email(self):
        for rec in self:
            if rec.communication_preferences == 'email':
                if not rec.email or rec.disabled_email:
                    raise ValidationError(
                        _("Please add a valid email or select another contact method"))

    @api.constrains('communication_preferences', 'cell')
    def check_communication_preferences_cell(self):
        for rec in self:
            if rec.communication_preferences == 'cell':
                if not rec.phone:
                    raise ValidationError(
                        _("Please add a valid cell number or select another contact method"))

    @api.constrains('communication_preferences', 'other')
    def check_communication_preferences_other(self):
        for rec in self:
            if rec.communication_preferences == 'phone':
                if not rec.other:
                    raise ValidationError(
                        _("Please add a valid phone number or select another contact method"))

    @api.onchange('insurance_authorizations_ids')
    def _onchange_insurance_authorizations_ids(self):
        for rec in self.insurance_authorizations_ids:
            if rec and rec.authorizations_type == 'authorization' and rec.vision_medical == 'vision':
                if not rec.exam and not rec.farme and not rec.lenses and not rec.contact_lens:
                    return {'warning': {'title': _("User Alert!"),
                                        'message': _(
                                            "In Authorization please select one of the (Exam, Frame, Lenses, Contact Lenses).")}}

    def appointments_list_view(self):
        self.ensure_one()
        _list = self.env.ref('opt_appointment.calendar_event_from_patient_form', False)
        return {
            'name': _('Appointments'),
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_type': 'list',
            'view_mode': 'list',
            'target': 'current',
            'view_id': [(_list and _list.id)],
            'views': [(_list and _list.id, 'list')],
            'domain': [('patient_id', '=', self.id), ('appointment_type', '=', 'appointment')],
        }


class ReferredBy(models.Model):
    _name = "spec.referred.by"
    _description = 'Referred by'

    name = fields.Char(string='Referred By')


class CommunicationTable(models.Model):
    _name = "spec.communication.table"
    _description = 'Communication Table'

    text = fields.Boolean(string='Text')
    cell = fields.Boolean(string='Cell')
    email = fields.Boolean(string='Email')
    mail = fields.Boolean(string='Mail')
    opt_out = fields.Boolean(string='Opt-out')
    communication = fields.Char(string='Communication')
    partner_id = fields.Many2one('res.partner', string="Partner")

    # @api.onchange('text', 'cell', 'email', 'mail', 'opt_out')
    # def onchange_opt_out(self):
    #     if self.opt_out:
    #         self.text = False
    #         self.cell = False
    #         self.email = False
    #         self.mail = False


class ActivitiesList(models.Model):
    _name = 'spec.activities.list'
    _description = 'Activities list'
    name = fields.Char(string="Activities")


class CommunicationMethods(models.Model):
    _name = 'spec.communication.method'
    _description = 'Communication Method'

    name = fields.Char(string='Communication Method')
    text = fields.Boolean(string="Text")


class Document(models.Model):
    _name = 'spec.documents'
    _description = 'Documents'
    name = fields.Char(string="Name")
    document_type = fields.Selection(
        [('cms_1500', 'CMS-1500 Form'), ('credit_card_authorization', 'Credit Card Authorization'),
         ("driver_license", "Driver's License"), ('hipaa_npp', 'HIPAA NPP'), (
             'id_card', 'ID Card'), ('insurance_card', 'Insurance Card'),
         ('insurance_card_secondary', 'Insurance Card - Secondary'),
         ('insurance_card_tertiary', 'Insurance Card - Tertiary'), ('pcp_consent_form', 'PCP Release Consent Form'),
         ('patient_photo', 'Patient Photo'), ('payment', 'Payment'), ('registration_form', 'Registration Form'),
         ('registration_packet', 'Registration Packet'), ('release_of_information', 'Release of Information'),
         ('reminder_call_release', 'Reminder Call Release'), ('service_agreement', 'Service Agreement'),
         ('cataract_referral_letter', 'Cataract Referral Letter'), ('contact_lens_agreement', 'Contact Lens Agreement'),
         ('diabetic_letter', 'Diabetic Letter'), ('insurance_uthorization', 'Insurance Authorization'),
         ('invoice', 'Invoice'), ('medical_history', 'Medical History'), ('other', 'Other'),
         ('office_policies', 'Office Policies'), ('outside_rx', 'Outside Rx'), ('pcp_letter', 'PCP Letter'),
         ('previous_exams', 'Previous Exams'), ('referral', 'Referral'), ('ssn_card', 'SSN Card')], string="Type")
    comments = fields.Text(string="Notes")
    upload_file = fields.Binary(string="Attachments")
    upload_file_file_name = fields.Char(string='File Name')
    date = fields.Date(string="Date", default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.constrains('upload_file')
    def check_upload_file(self):
        """Check Upload File"""
        for record in self:
            if record.upload_file_file_name:
                file_name = record.upload_file_file_name.split('.')
                if file_name[-1].lower() not in ['png', 'jpg', 'jpeg', 'gif', 'tif', 'pdf']:
                    raise ValidationError(
                        "You can upload only PDF, PNG, JPG, GIF or TIF Documnet file!")


class MultiImages(models.Model):
    _inherit = "multi.images"

    partner_id = fields.Many2one('res.partner', string="Partner")
    document_type = fields.Selection(
        [('cms_1500', 'CMS-1500 Form'), ('credit_card_authorization', 'Credit Card Authorization'),
         ("driver_license", "Driver's License"), ('hipaa_npp', 'HIPAA NPP'),
         ('id_card', 'ID Card'), ('insurance_card', 'Insurance Card'),
         ('insurance_card_secondary', 'Insurance Card - Secondary'),
         ('insurance_card_tertiary', 'Insurance Card - Tertiary'),
         ('pcp_consent_form', 'PCP Release Consent Form'),
         ('patient_photo', 'Patient Photo'),
         ('payment', 'Payment'), ('registration_form', 'Registration Form'),
         ('registration_packet', 'Registration Packet'),
         ('release_of_information', 'Release of Information'),
         ('reminder_call_release', 'Reminder Call Release'),
         ('service_agreement', 'Service Agreement'),
         ('cataract_referral_letter', 'Cataract Referral Letter'),
         ('contact_lens_agreement', 'Contact Lens Agreement'),
         ('diabetic_letter', 'Diabetic Letter'),
         ('insurance_uthorization', 'Insurance Authorization'),
         ('invoice', 'Invoice'), ('medical_history', 'Medical History'),
         ('other', 'Other'), ('office_policies', 'Office Policies'),
         ('outside_rx', 'Outside Rx'), ('pcp_letter', 'PCP Letter'),
         ('previous_exams', 'Previous Exams'),
         ('referral', 'Referral'), ('ssn_card', 'SSN Card')], string="Type")
    upload_file_file_name = fields.Char(string='File Name')
    date = fields.Date(string="Date", default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment', required=True, help='Add Attachment.')
    attachment_preview = fields.Char('Attachment Preview')

    @api.constrains('image')
    def check_upload_file(self):
        """Check Upload File"""
        for record in self:
            if record.upload_file_file_name:
                file_name = record.upload_file_file_name.split('.')
                if file_name[-1].lower() not in ['png', 'jpg', 'jpeg', 'gif', 'tif', 'pdf']:
                    raise ValidationError(
                        "You can upload only PDF, PNG, JPG, GIF or TIF Documnet file!")


class Notes(models.Model):
    _name = 'spec.notes'
    _description = 'Notes'
    name = fields.Text(string="Notes")
    notes_type = fields.Char(string="Type", default="Profile")
    urgent = fields.Boolean(string="Urgent")
    follow_up = fields.Boolean(string="Follow Up")
    partner_id = fields.Many2one('res.partner', string="Partner")
    date = fields.Date(string="Date", default=fields.Date.today())
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)


#            for insurance_id in self.partner_id.insurance_ids:
#                if insurance_id.insurance_type == 'vision' and insurance_id.activation_date \
#                    and any(terminate_date_rec.termination_date > self.activation_date for terminate_date_rec in terminate_dates_recs):
#                    if insurance_id.priority == 'primary':
#                        primary.append(insurance_id.priority)
#                    if insurance_id.priority == 'secondary':
#                        secondary.append(insurance_id.priority)
#                    if insurance_id.priority == 'tertiary':
#                        tertiary.append(insurance_id.priority)
#                if len(primary) > 1:
#                    self.priority = False
#                    return {'warning': {'title': _("User Alert!"),
#                                        'message': _("A primary insurance is already specified. Please update selection.")}}
#                if len(secondary) > 1:
#                    self.priority = False
#                    return {'warning': {'title': _("User Alert!"),
#                                        'message': _("A secondary insurance is already specified. Please update selection.")}}
#                if len(tertiary) > 1:
#                    self.priority = False
#                    return {'warning': {'title': _("User Alert!"),
#                                        'message': _("A tertiary insurance is already specified. Please update selection.")}}
#                if insurance_id.insurance_type == 'medical' and insurance_id.activation_date\
#                    and any(terminate_date_rec.termination_date > self.activation_date for terminate_date_rec in terminate_dates_recs):
#                    if insurance_id.priority == 'primary':
#                        medical_primary.append(insurance_id.priority)
#                    if insurance_id.priority == 'secondary':
#                        medical_secondary.append(insurance_id.priority)
#                    if insurance_id.priority == 'tertiary':
#                        medical_tertiary.append(insurance_id.priority)
#                if len(medical_primary) > 1:
#                    self.priority = False
#                    return {'warning': {'title': _("User Alert!"),
#                                        'message': _("A primary insurance is already specified. Please update selection.")}}
#                if len(medical_secondary) > 1:
#                    self.priority = False
#                    return {'warning': {'title': _("User Alert!"),
#                                        'message': _("A secondary insurance is already specified. Please update selection.")}}
#                if len(medical_tertiary) > 1:
#                    self.priority = False
#                    return {'warning': {'title': _("User Alert!"),
#                                        'message': _("A tertiary insurance is already specified. Please update selection.")}}


class RecallType(models.Model):
    _name = 'spec.recall.type'
    _description = 'Recall Type'

    name = fields.Char(string="Recall Type")
    months = fields.Integer(string="Months to Recall")
    # recall_schedule_ids = fields.One2many(
    #     'spec.recall.schedule', 'recall_type_id', string="Recall Schedule")


class RecallTypeLine(models.Model):
    _name = 'spec.recall.type.line'
    _description = 'Recall Type Line'

    name = fields.Many2one('spec.recall.type', string="Recall Type")
    months = fields.Integer(related="name.months", string="Months to Recall")
    next_recall_date = fields.Date(string="Date")
    partner_id = fields.Many2one('res.partner', string="Partner")

    # patient_id = fields.Many2one('res.partner', string="Partner")

    @api.onchange('name', 'months')
    def _onchange_name(self):
        if self.name:
            self.months = self.name.months
            # if self.name.name == 'Annual Exam':
            self.next_recall_date = fields.Date.today() + relativedelta(months=self.months)


class RecallSchedule(models.Model):
    _name = 'spec.recall.schedule'
    _description = 'Recall Schedule'

    number = fields.Integer(string="Number of Periods")
    period = fields.Selection(
        [('day', 'Day'), ('week', 'Week'), ('month', 'Month'), ], string="Period")
    when = fields.Selection(
        [('before', 'Before'), ('after', 'After')], default='before', string="When")
    recall_type_id_2 = fields.Many2one(
        'spec.recall.type', string="Recall Type")
    recall_type_id = fields.Many2one('spec.recall.type', string="Recall Type")
    partner_id = fields.Many2one('res.partner', string="Partner")


class RxUsage(models.Model):
    _name = 'spec.rx.usage'
    _description = 'Rx Usage'

    name = fields.Char(string="Rx Usage")


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
