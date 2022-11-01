# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _rec_name = 'first_name'

    is_insurance = fields.Boolean(string='is_insurance')
    fax = fields.Char(string='Fax')
    submit_to = fields.Char(string='Submit To')
    payer_id = fields.Char(string='Payer ID')
    insurance_type_id = fields.Selection([('medicare', 'Medicare'), ('medicaid', 'Medicaid'), ('tricare', 'Tricare'), ('champva', 'Champva'),
                                          ('group_health_plan', 'Group Health Plan'), ('feca_blklung', 'FECA Black Lung'), ('other', 'Other')], string="Insurance Type")
    insured_first_name = fields.Boolean(string='Insured First Name')
    insured_last_name = fields.Boolean(string='Insured Last Name')
    insured_birth_date = fields.Boolean(string='Insured Birth Date')
    insured_ssn_sin = fields.Boolean(string='Insured SSN/SIN')
    relation_to_insrured = fields.Boolean(string='Relation to insrured')
    patient_first_name = fields.Boolean(string='Patient First Name')
    patient_last_name = fields.Boolean(string='Patient Last Name')
    patient_birth_date = fields.Boolean(string='Patient Birth Date')
    Insurance_id = fields.Boolean(string='Insurance ID')
    plan_name = fields.Boolean(string='Plan Name')
    policy_group = fields.Boolean(string='Policy Group')
    authorization = fields.Boolean(string='Authorization')
    activation_date = fields.Date(string="Activation Date", default=fields.Date.today())
    termination_date = fields.Date(string="Termination Date")
    active = fields.Boolean(compute="_compute_active", string="Active", store=True)
    insurance_plan_ids = fields.One2many('spec.insurance.plan', 'insurance_company_id', readonly=True, string="Plan")

    generate_claims = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Generate Claims", default='yes')
    claim_output = fields.Selection([('electronic', 'Electronic'), ('print', 'Print')], string="Claim Output")
    pop_sec_ins_cms = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 9d - Populate Secondary Insurance on CMS", default='yes')
    pop_ref_ord_phy = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 17 - Auto Populate Referring/Ordering Provider", default='yes')
    place_of_service = fields.Selection([('telehealth', '02-Telehealth'), ('school', '03-School'), ('india_fee_standin', '05-Indian Health Service Free-standin Facility'),
                                         ('india_provide_based', '06-Indian Health Service Provider-based Facility'), ('tribal_fee_standin', '07-Tribal 638 Free-standing Facility'),
                                         ('tribal_provide_based', '08-Tribal 638 Provider-based Facility'), ('prison_correctional_facility', '09-Prison/Correctional Facility'),('office', '11-Office'),
                                         ('home', '12-Home'), ('assisted_living_facility','13-Assisted Living Facility'), ('group_home', '14-Group Home'), ('mobile_unite','15-Mobile Unit'),
                                         ('temporary_lodging', '16-Temporary Lodging'), ('health_clinick', '17-Walk-in Retail Health Clinic'), ('place_employment_works','18-Place of Employment Worksite'),
                                         ('outpaatient_hospital', '19-Off Campus-Outpatient Hospital'), ('skilled_nursing_facility', '31-Skilled Nursing Facility'), ('nursing_facility', '32-Nursing Facility'),
                                         ('hospice', '34-Hospice'), ('comprehensive_inpatient_rehabilitation', '61-Comprehensive Inpatient Rehabilitation Facility'),
                                         ('comprehensive_outpatient_rehabilitation', '62-Comprehensive Outpatient Rehabilitation Facility'), ('other_place_service', '99-Other Place of Service')],
                                         string="Box 24b - Place of Service ", default='office')
    contract_lens_unites = fields.Selection([('boxes', 'Boxes'), ('units', 'Units')], string="Box 24 g - Contact Lens Units", default='boxes')
    rendering_provider_qualifier = fields.Selection([('state_license_number', '0B - State License Number'),('provider_upin_number', '1G-Provider UPIN Number'),
                                                    ('provider_commercial_number', 'G2-Provider Commercial Number'),('location_number', 'LU-Location Number,'),
                                                    ('provider', 'ZZ-Provider'), ('taxonomy', 'Taxonomy')], string="Box 24 i-Rendering Provider Qualifier",
                                                    help="Rendering Provider Qualifier")
    rendering_provider_qualifier_char = fields.Char(string="Box 24 i - Rendering Provider Qualifier")
    accept_assignment = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Box 27 - Accept Assignment", default='yes')
    amount_paid = fields.Selection([('none', 'None'), ('patient_payment', 'Patient Payment')], string="Box 29 - Amount Paid", default='patient_payment')
    federal_tax_id = fields.Selection([('company_tax_id', 'Company Tax ID'), ('physicians_ssn', 'Provider’s SSN'), ('physicians_tax_id', 'Provider’s Tax ID')], string="Box 25 - Federal Tax ID", default='company_tax_id')
    signature_physician_supplier = fields.Selection([('physician', 'Provider'), ('supplier', 'Supplier')], string="Box 31 - Signature of Provider or Supplier", default='physician')
    service_facility_other_id = fields.Selection([('state_license_number', '0B - State License Number'), ('provider_commercial_number', 'G2-Provider Commercial Number'),
                                                  ('location_number', 'LU-Location Number')], string="Box 32 b-Service Facility Other ID", help="Service Facility Other ID")
    service_facility_other_id_char = fields.Char(string="Box 32 b-Service Facility Other ID")
    billing_provider = fields.Selection([('location', 'Location'), ('company', 'Company'), ('physician', 'Provider')],  string="Box 33 Billing Provider", default='company')
    billing_provider_npi = fields.Selection([('location', 'Location'), ('company', 'Company'), ('physician', 'Provider')], string="Box 33 a - Billing Provider NPI", default='company')
    billing_provider_other_id = fields.Selection([('location', 'Location'), ('company', 'Company'), ('physician', 'Provider')], string="Box 33 b - Billing Provider Other ID", default='company')
    notes = fields.Text(string="Notes")
    apply_tax = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Apply Tax", default='yes', help="If you want to apply tax on this Insurance select YES, or else NO.")
    add_tax_to_cms = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Add Tax to CMS", default='yes', help="Do you want the tax to be applied on CMS?")
    patient_tax_responsibility = fields.Selection([('pt_total', 'PT Total'), ('copay', 'Copay'),('retail', 'Retail')], string="Patient Tax Responsibility", help="on which field do you want the tax to be applied")

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        args = args or []
        primary_insurance = []
        secondary_insurance = []
        context = self._context or {}
        if context.get('search_patient_insurance') and context.get('patient_id'):
            patient_rec = self.env['res.partner'].browse(context.get('patient_id'))
            for primary in patient_rec.insurance_ids:
                if primary.carrier_id.id not in primary_insurance:
                    if primary.priority == 'primary':
                        primary_insurance.append(primary.carrier_id.id)
            args.append(('id', 'in', tuple(primary_insurance)))
        if context.get('search_patient_secondary_insurance') and context.get('patient_id'):
            secondary_patient_rec = self.env['res.partner'].browse(context.get('patient_id'))
            for secondary in secondary_patient_rec.insurance_ids:
                if secondary.carrier_id.id not in secondary_insurance:
                    secondary_insurance.append(secondary.carrier_id.id)
            args.append(('id', 'in', tuple(secondary_insurance)))
        return super(ResPartner, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.depends('termination_date')
    def _compute_active(self):
        plan_obj = self.env['spec.insurance.plan']
        for record in self:
            if record.termination_date and record.termination_date <= fields.Date.today():
                record.active = False
            else:
                record.active = True
            for plan_id in record.insurance_plan_ids:
                plan_id.active = record.active
                plan_id.termination_date = False
                if not plan_id.termination_date:
                    plan_id.termination_date = record.termination_date
            else:
                plan_ids = plan_obj.search([('active', '=', False), ('insurance_company_id', '=', record._origin.id)])
                if plan_ids:
                    for plan_id in plan_ids:
                        plan_id.active = record.active
                        plan_id.termination_date = False
                        if not plan_id.termination_date:
                            plan_id.termination_date = record.termination_date

    @api.onchange('payer_id')
    def _onchange_payer_id(self):
        if self.payer_id:
            self.claim_output = 'electronic'
        else:
            self.claim_output = 'print'

    @api.onchange('fax')
    def _onchange_fax(self):
        if self.fax and self.fax.isdigit():
            self.fax = '({}) {}-{}'.format(self.fax[:3], self.fax[3:6], self.fax[6:])

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

    def active_insurance(self):
        for insurance_id in self.search([('termination_date', '<=', fields.Date.today())]):
            insurance_id.active = False
            for plan_id in insurance_id.insurance_plan_ids:
                plan_id.active = insurance_id.active
                plan_id.termination_date = False
                if not plan_id.termination_date:
                    plan_id.termination_date = insurance_id.termination_date

    @api.constrains('claim_output')
    def check_claim_output(self):
        if self.claim_output == 'electronic' and not self.payer_id:
            raise ValidationError('Please add a valid Payer ID')

    @api.onchange('first_name')
    def _onchange_first_name(self):
        if self.env.context.get('copy_to_name', False):
            self.name = self.first_name

    # @api.model
    # def write(self, vals):
    #     if self.env.context.get('res_partner_search_mode', False) == 'supplier' and  self.env.context.get('default_is_company', False) and self.env.context.get('default_supplier_rank', False):
    #         self.name = self.first_name
    #     return super(ResPartner, self).write(vals)

    # @api.model
    # def create(self, vals_list):
    #     if self.env.context.get('res_partner_search_mode', False) == 'supplier' and \
    #             self.env.context.get('default_is_company', False) and self.env.context.get('default_supplier_rank', False):
    #         if 'first_name' in vals_list:
    #             vals_list['name'] = vals_list['first_name']
    #     return super(ResPartner, self).create(vals_list)
