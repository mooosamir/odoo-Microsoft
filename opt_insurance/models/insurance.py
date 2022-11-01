# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


reason_list1 = [('accept_assignment', 'Accept Assignment'),
                ('adjustment', 'Adjustment'),
                ('CO_237', 'CO-237:Legislated/regulatory penalty'),
                ('CO_253', 'CO-253:Sequestration-reduction in federal payment'),
                ('lab', 'Lab Provided Materials'),
                ('patiendt_payment', 'Patient Payment'),
                ('receivable_adjustment', 'Receivable Adjustment'),
                ('se', 'SE-Patient not eligible'),
                ('timely_filling', 'Timely Filling')]

reason_list2 = [('contract', 'Contract'), ('charity', 'Charity')]


class Insurance(models.Model):
    _name = 'spec.insurance'
    _description = 'Insurance'
    _rec_name = 'carrier_id'
    _order = "terminated"

    def _compute_name_with_termination_date(self):
        for rec in self:
            rec.name_with_termination_date = rec.carrier_id.name
            rec.terminated = False
            if rec.termination_date:
                if fields.datetime.now().date() >= rec.termination_date:
                    rec.name_with_termination_date += " (Termed " + str(rec.termination_date) + " )"
                    rec.terminated = True

    def _compute_name(self):
        for res in self:
            res.name = (res.first_name + ' ' if res.first_name else '') + (res.middle_name + ' ' if res.middle_name else '') +\
                       (res.last_name + ' ' if res.last_name else '')

    name_with_termination_date = fields.Char(string='Insurance', compute="_compute_name_with_termination_date")
    terminated = fields.Boolean(string="Terminated", default=True)

    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Char(string='Insurance ID')
    policy_group = fields.Char(string='Policy Group')
    name = fields.Char(string="Subscriber Name", compute='_compute_name')
    first_name = fields.Char(string="First Name")
    middle_name = fields.Char(string="Middle Name")
    last_name = fields.Char(string="Last Name")

    use_patient_ssn = fields.Boolean(string="Use Patient SSN")
    relationship = fields.Selection([('child_depende', 'Child'), ('other', 'Other'),
                                     ('self', 'Self'), ('spouse', 'Spouse')], default="self", string="Relationship")
    address_same_patient = fields.Boolean(string='Address Same as Patient')
    address_line_1 = fields.Char(string='Address Line 1 (7)')
    address_line_2 = fields.Char(string='Address Line 2 (7)')
    city = fields.Char(string='City (7)')
    zip = fields.Char(change_default=True, string="ZIP (7)")
    country_id = fields.Many2one('res.country', string="Country", default=lambda self: self.env.user.company_id.country_id)
    state_id = fields.Many2one("res.country.state", string='State (7)', ondelete='restrict', help='The name of the state.', domain="[('country_id', '=',  country_id)]")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('unspecified', 'Unspecified')], default="male", string="Gender")
    phone = fields.Char(string="Phone")
    date = fields.Date(string="Date of Birth")
    employer = fields.Char(string="Employer")
    carrier_id = fields.Many2one('res.partner', string="Insurance", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    plan_id = fields.Many2one('spec.insurance.plan', string="Plan")
    priority = fields.Selection([('primary', 'Primary'), ('secondary', 'Secondary'), ('tertiary', 'Tertiary')], string="Priority")
    insurance_type = fields.Selection([('medical', 'Medical'), ('vision', 'Vision')], string="Insurance Type")
    address = fields.Char(string="Address")
    activation_date = fields.Date(string="Active", default=fields.Date.today())
    termination_date = fields.Date(string="Termination")
    image_front = fields.Binary(string="Add image front")
    image_back = fields.Binary(string="Add image back")
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.model
    def default_get(self, default_fields):
        res = super(Insurance, self).default_get(default_fields)
        partner_id = self._context.get("partner_id")
        if partner_id:
            res.update({'partner_id': partner_id})
        return res

    @api.model
    def create(self, vals):
        if vals and not vals.get('sequence', False):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('spec.insurance.id')
        return super(Insurance, self).create(vals)

    def write(self, vals):
        res = super(Insurance, self).write(vals)
        if self._context.get('from_edit_claim') and self._context.get('active_id'):
            claim_rec = self.env['claim.manager'].browse(self._context.get('active_id'))
            claim_rec._onchange_lang_localization()
        return res

    def dummy_btn(self):
        # ================================================================
        # Please do not change this code this method is call from JS
        # ================================================================
        return True

    @api.onchange('use_patient_ssn')
    def _onchange_name(self):
        if self.use_patient_ssn:
            self.sequence = self.partner_id.ssn or ''
        else:
            self.sequence = ''

    @api.onchange('address_same_patient')
    def _onchange_address_same_patient(self):
        if self.address_same_patient:
            self.address_line_1 = self.partner_id.street
            self.address_line_2 = self.partner_id.street2
            self.city = self.partner_id.city
            self.zip = self.partner_id.zip
            self.state_id = self.partner_id.state_id
        else:
            self.address_line_1 = False
            self.address_line_2 = False
            self.city = False
            self.zip = False
            self.state_id = False

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        if self.carrier_id:
            self.address = self.carrier_id.street

    @api.onchange('relationship')
    def _onchange_relationship(self):
        if self.relationship == 'self':
            self.name = self.partner_id.name
            self.address_line_1 = self.partner_id.street
            self.address_line_2 = self.partner_id.street2
            self.city = self.partner_id.city
            self.state_id = self.partner_id.state_id
            self.zip = self.partner_id.zip
            self.gender = self.partner_id.gender
            self.phone = self.partner_id.phone
            self.date = self.partner_id.date_of_birth
        else:
            self.name = False
            self.address_line_1 = False
            self.address_line_2 = False
            self.city = False
            self.state_id = False
            self.zip = False
            self.gender = False
            self.phone = False
            self.date = False

    @api.onchange('phone')
    def _onchange_phone(self):
        if self.phone and self.phone.isdigit():
            if len(self.phone) >= 10:
                self.phone = '({}) {}-{}'.format(self.phone[:3], self.phone[3:6], self.phone[6:])

    @api.onchange('priority', 'insurance_type', 'activation_date', 'termination_date')
    def _onchange_priority(self):
        primary = []
        secondary = []
        tertiary = []
        medical_primary = []
        medical_secondary = []
        medical_tertiary = []
        if self.priority and self.insurance_type:
            warning_flag = False
            insurance_lines = self.partner_id.insurance_ids.filtered(lambda l: l.priority == self.priority and l.insurance_type == self.insurance_type and l != self)
            if insurance_lines and self.termination_date:
                terminate_dates_recs = insurance_lines.filtered(lambda l: l.termination_date)
                warning_flag = any(terminate_date_rec.termination_date > self.activation_date for terminate_date_rec in terminate_dates_recs)
            elif insurance_lines and not self.termination_date:
                warning_flag = True
            if warning_flag:
                if self.priority == 'primary':
                    self.priority = False
                    return {'warning': {'title': _("User Alert!"),
                                        'message': _("A primary insurance is already specified. Please update selection.")}}
                elif self.priority == 'secondary':
                    self.priority = False
                    return {'warning': {'title': _("User Alert!"),
                                        'message': _("A secondary insurance is already specified. Please update selection.")}}

                elif self.priority == 'tertiary':
                    self.priority = False
                    return {'warning': {'title': _("User Alert!"),
                                        'message': _("A tertiary insurance is already specified. Please update selection.")}}


class InsuranceCompanyListing(models.Model):
    _name = 'spec.insurance.company.listing'
    _description = 'Insurance Company Listing'

    # name = fields.Char(string='Insurance')
    # phone = fields.Char(string='Phone')
    # fax = fields.Char(string='Fax')
    # submit_to = fields.Char(string='Submit To')
    # address_line_1 = fields.Char(string='Address Line 1')
    # address_line_2 = fields.Char(string='Address Line 2')
    # city = fields.Char(string='City')
    # zip = fields.Char(change_default=True, string="ZIP")
    # state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', help='The name of the state.')
    # payer_id = fields.Char(string='Payer ID')
    # insurance_type_id = fields.Selection([('medicare', 'Medicare'), ('medicaid', 'Medicaid'), ('tricare', 'Tricare'), ('champva', 'Champva'),
    #                                       ('group_health_plan', 'Group Health Plan'), ('feca_blklung', 'FECA Black Lung'), ('other', 'Other')], string="Insurance Type")
    # insured_first_name = fields.Boolean(string='Insured First Name')
    # insured_last_name = fields.Boolean(string='Insured Last Name')
    # insured_birth_date = fields.Boolean(string='Insured Birth Date')
    # insured_ssn_sin = fields.Boolean(string='Insured SSN/SIN')
    # relation_to_insrured = fields.Boolean(string='Relation to insrured')
    # patient_first_name = fields.Boolean(string='Patient First Name')
    # patient_last_name = fields.Boolean(string='Patient Last Name')
    # patient_birth_date = fields.Boolean(string='Patient Birth Date')
    # Insurance_id = fields.Boolean(string='Insurance ID')
    # plan_name = fields.Boolean(string='Plan Name')
    # policy_group = fields.Boolean(string='Policy Group')
    # authorization = fields.Boolean(string='Authorization')
    # activation_date = fields.Date(string="Activation Date", default=fields.Date.today())
    # termination_date = fields.Date(string="Termination Date")
    # active = fields.Boolean(compute="_compute_active", string="Active", store=True)
    # insurance_plan_ids = fields.One2many('spec.insurance.plan', 'insurance_company_id', readonly=True, string="Plan")
    # generate_claims = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Generate Claims", default='yes')
    # claim_output = fields.Selection([('electronic', 'Electronic'), ('print', 'Print')], string="Claim Output")
    # pop_sec_ins_cms = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 9d - Populate Secondary Insurance on CMS", default='yes')
    # pop_ref_ord_phy = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 17 - Auto Populate Referring/Ordering Provider", default='yes')
    # place_of_service = fields.Selection([('telehealth', '02-Telehealth'), ('school', '03-School'), ('india_fee_standin', '05-Indian Health Service Free-standin Facility'),
    #                                      ('india_provide_based', '06-Indian Health Service Provider-based Facility'), ('tribal_fee_standin', '07-Tribal 638 Free-standing Facility'),
    #                                      ('tribal_provide_based', '08-Tribal 638 Provider-based Facility'), ('prison_correctional_facility', '09-Prison/Correctional Facility'),('office', '11-Office'),
    #                                      ('home', '12-Home'), ('assisted_living_facility','13-Assisted Living Facility'), ('group_home', '14-Group Home'), ('mobile_unite','15-Mobile Unit'),
    #                                      ('temporary_lodging', '16-Temporary Lodging'), ('health_clinick', '17-Walk-in Retail Health Clinic'), ('place_employment_works','18-Place of Employment Worksite'),
    #                                      ('outpaatient_hospital', '19-Off Campus-Outpatient Hospital'), ('skilled_nursing_facility', '31-Skilled Nursing Facility'), ('nursing_facility', '32-Nursing Facility'),
    #                                      ('hospice', '34-Hospice'), ('comprehensive_inpatient_rehabilitation', '61-Comprehensive Inpatient Rehabilitation Facility'),
    #                                      ('comprehensive_outpatient_rehabilitation', '62-Comprehensive Outpatient Rehabilitation Facility'), ('other_place_service', '99-Other Place of Service')],
    #                                      string="Box 24b - Place of Service ", default='office')
    # contract_lens_unites = fields.Selection([('boxes', 'Boxes'), ('units', 'Units')], string="Box 24 g - Contact Lens Units", default='boxes')
    # rendering_provider_qualifier = fields.Selection([('state_license_number', '0B - State License Number'),('provider_upin_number', '1G-Provider UPIN Number'),
    #                                                 ('provider_commercial_number', 'G2-Provider Commercial Number'),('location_number', 'LU-Location Number,'),
    #                                                 ('provider', 'ZZ-Provider'), ('taxonomy', 'Taxonomy')], string="Box 24 i-Rendering Provider Qualifier",
    #                                                 help="Rendering Provider Qualifier")
    # rendering_provider_qualifier_char = fields.Char(string="Box 24 i - Rendering Provider Qualifier")
    # accept_assignment = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 27 - Accept Assignment", default='yes')
    # amount_paid = fields.Selection([('none', 'None'), ('patient_payment', 'Patient Payment')], string="Box 29 - Amount Paid", default='patient_payment')
    # federal_tax_id = fields.Selection([('company_tax_id', 'Company Tax ID'), ('physicians_ssn', 'Physician’s SSN'), ('physicians_tax_id', 'Physician’s Tax ID')], string="Box 25 - Federal Tax ID", default='company_tax_id')
    # signature_physician_supplier = fields.Selection([('physician', 'Physician'), ('supplier', 'Supplier')], string="Box 31 - Signature of Provider or Supplier", default='physician')
    # service_facility_other_id = fields.Selection([('state_license_number', '0B - State License Number'), ('provider_commercial_number', 'G2-Provider Commercial Number'),
    #                                               ('location_number', 'LU-Location Number')], string="Box 32 b-Service Facility Other ID", help="Service Facility Other ID")
    # service_facility_other_id_char = fields.Char(string="Box 32 b-Service Facility Other ID")
    # billing_provider = fields.Selection([('location', 'Location'), ('company', 'Company'), ('physician', 'Physician')],  string="Box 33 Billing Provider", default='company')
    # billing_provider_npi = fields.Selection([('location', 'Location'), ('company', 'Company'), ('physician', 'Physician')], string="Box 33 a - Billing Provider NPI", default='company')
    # billing_provider_other_id = fields.Selection([('location', 'Location'), ('company', 'Company'), ('physician', 'Physician')], string="Box 33 b - Billing Provider Other ID", default='company')
    # country_id = fields.Many2one(string="Country", comodel_name='res.country', required=True, default=lambda x: x.env.company.country_id.id, help="Country for which this line is available.")
    # notes = fields.Text(string="Notes")
    # company_id = fields.Many2one('res.company', string="Company")
    #
    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     args = args or []
    #     primary_insurance = []
    #     secondary_insurance = []
    #     context = self._context or {}
    #     if context.get('search_patient_insurance') and context.get('patient_id'):
    #         patient_rec = self.env['res.partner'].browse(context.get('patient_id'))
    #         for primary in patient_rec.insurance_ids:
    #             if primary.carrier_id.id not in primary_insurance:
    #                 if primary.priority == 'primary':
    #                     primary_insurance.append(primary.carrier_id.id)
    #         args.append(('id', 'in', tuple(primary_insurance)))
    #     if context.get('search_patient_secondary_insurance') and context.get('patient_id'):
    #         secondary_patient_rec = self.env['res.partner'].browse(context.get('patient_id'))
    #         for secondary in secondary_patient_rec.insurance_ids:
    #             if secondary.carrier_id.id not in secondary_insurance:
    #                 secondary_insurance.append(secondary.carrier_id.id)
    #         args.append(('id', 'in', tuple(secondary_insurance)))
    #     return super(InsuranceCompanyListing, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
    #
    # @api.model
    # def default_get(self, fields):
    #     result = super(InsuranceCompanyListing, self).default_get(fields)
    #     company_id = self.env['res.company'].search([('main', '=', True)])
    #     result['company_id'] = company_id.id
    #     return result
    #
    # @api.depends('termination_date')
    # def _compute_active(self):
    #     plan_obj = self.env['spec.insurance.plan']
    #     for record in self:
    #         if record.termination_date and record.termination_date <= fields.Date.today():
    #             record.active = False
    #         else:
    #             record.active = True
    #         for plan_id in record.insurance_plan_ids:
    #             plan_id.active = record.active
    #             plan_id.termination_date = False
    #             if not plan_id.termination_date:
    #                 plan_id.termination_date = record.termination_date
    #         else:
    #             plan_ids = plan_obj.search([('active', '=', False), ('insurance_company_id', '=', record._origin.id)])
    #             if plan_ids:
    #                 for plan_id in plan_ids:
    #                     plan_id.active = record.active
    #                     plan_id.termination_date = False
    #                     if not plan_id.termination_date:
    #                         plan_id.termination_date = record.termination_date
    #
    # @api.onchange('payer_id')
    # def _onchange_payer_id(self):
    #     if self.payer_id:
    #         self.claim_output = 'electronic'
    #     else:
    #         self.claim_output = 'print'
    #
    # @api.onchange('phone', 'fax')
    # def _onchange_phone(self):
    #     if self.phone and self.phone.isdigit():
    #         self.phone = '({}) {}-{}'.format(self.phone[:3], self.phone[3:6], self.phone[6:])
    #
    # @api.onchange('fax')
    # def _onchange_fax(self):
    #     if self.fax and self.fax.isdigit():
    #         self.fax = '({}) {}-{}'.format(self.fax[:3], self.fax[3:6], self.fax[6:])
    #
    # @api.constrains('zip')
    # def check_zip(self):
    #     for rec in self:
    #         total_size = 0
    #         total = 0
    #         if rec.zip:
    #             total_size = len(rec.zip)
    #             if total_size == 9:
    #                 rec.zip = '{}-{}'.format(self.zip[:5], self.zip[5:])
    #             zip_len = str(rec.zip).split('-')
    #             for total_char in zip_len:
    #                 total_size = len(total_char)
    #                 total += total_size
    #             if total != 9:
    #                 raise ValidationError(_("Please enter a 9 digit zip code"))
    #
    # def active_insurance(self):
    #     for insurance_id in self.search([('termination_date', '<=', fields.Date.today())]):
    #         insurance_id.active = False
    #         for plan_id in insurance_id.insurance_plan_ids:
    #             plan_id.active = insurance_id.active
    #             plan_id.termination_date = False
    #             if not plan_id.termination_date:
    #                 plan_id.termination_date = insurance_id.termination_date
    #
    # @api.constrains('claim_output')
    # def check_claim_output(self):
    #     if self.claim_output == 'electronic' and not self.payer_id:
    #         raise ValidationError('Please add a valid Payer ID')


class InsuranceNetwork(models.Model):
    _name = 'spec.insurance.network'
    _description = 'Insurance Network'

    name = fields.Char(string='Network Name')
    insurance_company_id = fields.Many2one(
        'res.partner', string="Insurance Company", domain="[('is_company','=',1), ('is_insurance','=',1)]")


class InsurancePlan(models.Model):
    _name = 'spec.insurance.plan'
    _description = 'Insurance Plan'

    name = fields.Char(string='Plan Name')
    insurance_company_id = fields.Many2one('res.partner', string="Insurance Company", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    classification = fields.Selection([('vision', 'Vision'), ('medical', 'Medical'), ('both', 'Both')], string="Classification")
    activation_date = fields.Date(string="Activation Date", default=fields.Date.today())
    termination_date = fields.Date(string="Termination Date")
    pcp_referral_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="PCP Referral Required")
    prior_authorization_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 23 - Prior authorization Required")
    region_ids = fields.Many2many('spec.region', 'plan_region_rel', 'plan_id', 'region_id', string="Region")
    notes = fields.Text(string="Notes")
    active = fields.Boolean(string="Active", default=True)

    @api.constrains('termination_date')
    def check_termination_date(self):
        if self.termination_date:
            if self.insurance_company_id.termination_date != self.termination_date:
                raise ValidationError('Insurance plan termination date cannot be different from insurance company termination date')


class InsuranceChargeBack(models.Model):
    _name = 'spec.insurance.chargeback'
    _description = 'Insurance ChargeBack'

    name = fields.Char(string='Charge Back Schedule')
    insurance_company_id = fields.Many2one('res.partner', string="Insurance Company", domain="[('is_company','=',1), ('is_insurance','=',1)]")


class InsuranceGroupCoPay(models.Model):
    _name = 'spec.insurance.group.co.pay'
    _description = 'Insurance Group Co-Pay'

    name = fields.Char(string='Group Co-Pay Name')
    pro_code_ids = fields.Many2many('spec.procedure.code', 'insurance_procedure_rel', 'insurance_id', 'procedure_id', string='Applied to Procedure')


class InsuranceGroupAllowance(models.Model):
    _name = 'spec.insurance.group.allowance'
    _description = 'Insurance Allowance'

    name = fields.Char(string='Group Allowance Name')
    pro_code_ids = fields.Many2many('spec.procedure.code', 'insurances_procedure_rel', 'insurance_id', 'procedure_id', string='Applied to Procedure')


class InsuranceDispensingFees(models.Model):
    _name = 'spec.insurance.dispensing.fee'
    _description = 'Insurance Dispensing Fees'

    name = fields.Char(string='Dispensing Fee Name')
    pro_code_ids = fields.Many2many('spec.procedure.code', 'insurances_procedures_rel', 'insurance_id', 'procedure_id', string='Applied to Procedure')


class InsuranceFittingFees(models.Model):
    _name = 'spec.insurance.fitting.fee'
    _description = 'Insurance Fitting Fees'

    name = fields.Char(string='Fitting Fee Name')
    pro_code_ids = fields.Many2many('spec.procedure.code', 'ins_proc_rel', 'insurance_id', 'procedure_id', string='Applied to Procedure')


class InsuranceNetworkGroups(models.Model):
    _name = 'spec.insurance.network.groups'
    _description = 'Insurance Network Groups'

    name = fields.Char(string='Group Name')
    network_id = fields.Many2one('spec.insurance.network', string="Network")
    primary_bill_code = fields.Many2one(
        'spec.procedure.code', string='Primary Bill Code')
    secondary_bill_code = fields.Many2one(
        'spec.procedure.code', string='Secondary Bill Code')


class ERAAutoAdjustmentRules(models.Model):
    _name = "spec.era.auto.adjustment"
    _description = 'ERA Auto-Adjustment Rules'
    _rec_name = 'insurance_id'

    insurance_id = fields.Many2one('res.partner', string="Insurance", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    amount_min = fields.Float(string="Amount Min")
    amount_max = fields.Float(string="Amount Max")
    level = fields.Selection([('claim', 'Claim'), ('line', 'Line')], string="Level")
    action = fields.Selection([('write_off', 'Write-Off'), ('adjustment', 'Adjustment')], default='write_off', string="Action")
    era_active = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Active", default='yes')
    date = fields.Date(tring="Date", default=fields.Datetime.now, readonly=True)
    user = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, readonly=True)
    reasons = fields.Selection(reason_list1, string="Reason")
    reasons_write = fields.Selection(reason_list2, string="Reason")
    reason_char = fields.Selection(selection=lambda self: self.get_reason_list(), string='Reason')

    def get_reason_list(self):
        combine_lst = reason_list1 + reason_list2
        return combine_lst

    @api.onchange('action', 'reasons_write', 'reasons')
    def set_values(self):
        if self.action == 'write_off':
            self.reasons = ''
        if self.action == 'adjustment':
            self.reasons_write = ''

        if self.reasons:
            self.reason_char = self.reasons

        if self.reasons_write:
            self.reason_char = self.reasons_write


class FormularyProcedureCodeGrouping(models.Model):
    _name = 'spec.formulary.procedure.grouping'
    _description = 'Formulary Procedure Code Grouping'

    name = fields.Char(string="Group Name")
    bill_code_id = fields.Many2one('spec.procedure.code', string='Bill Code')
    procedure_ids = fields.One2many('spec.procedure.code.line', 'formulary_id', string="Procedure")

    @api.model
    def default_get(self, fields):
        sequence_id = self.env['ir.sequence'].search(
            [('code', '=', 'spec.grouping.item')], limit=1)
        sequence_id.number_next_actual = 1
        return super(FormularyProcedureCodeGrouping, self).default_get(fields)


class ProcedureCodeLine(models.Model):
    _name = 'spec.procedure.code.line'
    _description = 'Procedure Code Line'

    sequence = fields.Char(string='Item', readonly=1)
    lens_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Lens')]", string="Lens Name")
    lens_procedure = fields.Char(string="Procedure")
    lens_type_id = fields.Many2one('spec.lens.type', string="Lens Type")
    lens_brand_id = fields.Many2one('spec.lens.brand', string="Lens Brand")
    lens_style_id = fields.Many2one('spec.lens.style', string="Lens Style")
    material_id = fields.Many2one('spec.lens.material', string="Material")
    filter_id = fields.Many2one('spec.lens.filter', string="Filter")
    lens_color_id = fields.Many2one('spec.lens.colors', string="Filter/Lens Color")
    formulary_id = fields.Many2one('spec.formulary.procedure.grouping', string="Formulary")

    @api.onchange('lens_id')
    def _onchange_lens_name_id(self):
        if self.lens_id:
            self.lens_type_id = self.lens_id.lens_type_id.id
            self.lens_brand_id = self.lens_id.brand_id.id
            self.lens_style_id = self.lens_id.style_id.id
            self.material_id = self.lens_id.material_id.id
            self.filter_id = self.lens_id.filter_id.id
            self.lens_color_id = self.lens_id.color_id.id
        result = []
        for rec in self.lens_id.lens_param_ids.procedure_code_id:
            if rec.name:
                result.append(rec.name)
        self.lens_procedure = ",".join(
            [str(procedure) for procedure in result])

    @api.model
    def create(self, vals):
        if vals and not vals.get('sequence', False):
            vals['sequence'] = self.env[
                'ir.sequence'].next_by_code('spec.grouping.item')
        return super(ProcedureCodeLine, self).create(vals)
