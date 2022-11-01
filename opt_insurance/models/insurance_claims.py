from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _, exceptions
import datetime

class ClaimManager(models.Model):
    _name = "claim.manager"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Claim Manager"
    _rec_name = "sequence"
    _order = "service_date"

    @api.depends('claim_line_ids.payments', 'claim_line_ids.retail')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for claims in self:
            amount_paid = total_charge = 0.0
            for line in claims.claim_line_ids:
                amount_paid += line.payments
                total_charge += line.retail
            claims.update({
                'amount_paid': amount_paid,
                'total_charge': total_charge,
            })

    @api.depends('claim_line_ids')
    def _compute_insuranc_receivable(self):
        for rec in self:
            rec.insurance_ar = sum(rec.claim_line_ids.mapped('ins_receivable'))

    @api.depends('submission_date')
    def _compute_claim_age(self):
        for rec in self:
            if rec.submission_date:
                fmt = '%Y-%m-%d'
                current_date = datetime.datetime.today()
                submission_date= datetime.datetime.strptime(str(rec.submission_date), fmt)
                relative_delta = relativedelta(current_date, submission_date)

                days = str(relative_delta.days)
                months = str(relative_delta.months)
                years =  str(relative_delta.years)

                if days == False or days == None:
                    days = 0
                if months == False or months == None:
                    months = 0
                if years == False or years == None:
                    years = 0
                rec.claim_age = str(years) + " Years " + str(months) + " Months " + str(days) + " Days"
            else:
                rec.claim_age = ''


    sequence = fields.Char(string='Claim #')
    service_date = fields.Date(string='Service Date')
    submission_date = fields.Date(string='Submission Date')
    claim_age = fields.Char(compute='_compute_claim_age')
    company_id = fields.Many2one('res.company', string="Location")
    insurance_claim = fields.Float('Claim #')
    primary_insurance_company_id = fields.Many2one('res.partner', string="Primary Insurance", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    secondary_insurance_company_id = fields.Many2one('res.partner', string="Secondary Insurance", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    insurance_fees = fields.Float('Fees')
    insurance_ar = fields.Float('Insurance Receivable', compute='_compute_insuranc_receivable')
    state = fields.Selection([('ready_to_bill', 'Ready To Bill'),
                                            ('on_hold', 'On Hold'),
                                            ('submitted_to_payer', 'Submitted to Payer'),
                                            ('rejected', 'Rejected'),
                                            ('paid', 'Paid'),
                                            ('cancelled', 'Cancelled')],
                                            string="Claim Status", default='ready_to_bill', tracking=True)
    sale_order_id = fields.Many2one('sale.order', string="Order Number")
    account_move_id = fields.Many2one('account.move', string="Invoice Number")
    authorization_id = fields.Many2one('spec.insurance.authorizations')
    employee_provider_id = fields.Many2one('hr.employee', string="Provider")
    partner_doctors_id = fields.Many2one('res.partner', string="Doctors", domain=[('doctor_type', 'in', ('doctor', 'out_doctor'))])
    patient_id = fields.Many2one('res.partner', string="Patient", domain=[('patient', '=', True)])
    insured_id = fields.Many2one('spec.insurance', string='Primary Insured')
    insured_sequence = fields.Char(string='Insured ID', related="insured_id.sequence")
    insured = fields.Char('Insured')
    qualifier = fields.Selection([('dk', 'DK'), ('dn', 'DN'), ('dq', 'DQ')], 'Qualifier')
    additional_information = fields.Text('Additional Information (19)')
    prior_auth = fields.Char('Prior Auth')
    clia = fields.Char('CLIA')
    resubmission_qualifier = fields.Selection([('1_original', '1-Original'),
                                                ('7_replacement', '7-Replacement'),
                                                ('8_void', '8-Void')], 'Resubmission Qualifier')
    resubmission_text = fields.Char('Resubmission Text')
    claim_line_ids = fields.One2many('claim.line', 'claim_manager_id', string="Insurance Claim line")
    error = fields.Text('Error')
    claim_supplemental_information_ids = fields.One2many('claim.supplemental.information', 'claim_manager_id', string="Claim Supplemental Information")
    total_charge = fields.Float("Total Charge", compute="_amount_all")
    amount_paid = fields.Float("Amount Paid", compute="_amount_all")
    currency_id = fields.Many2one('res.currency', string='Currency',
                         default=lambda self: self.env.company.currency_id)

    # EDIT CLAIM VIEWS FOR CLAIM PROCESS
    # section 1
    insurance_company_id = fields.Many2one(related="primary_insurance_company_id", comodel='res.partner',
                                                    string="Insurance", readonly=False, domain="[('is_company','=',1), ('is_insurance','=',1)]")
    plan_id = fields.Many2one('spec.insurance.plan', string="Plan")
    secondary_plan_id = fields.Many2one('spec.insurance.plan', string="Secondary Plan", readonly=False)
    address_line_1 = fields.Char(related="insurance_company_id.street", string='Address Line 1', readonly=False)
    address_line_2 = fields.Char(related="insurance_company_id.street2", string='Address Line 2', readonly=False)
    city = fields.Char(related="insurance_company_id.city", string='City', readonly=False)
    zip = fields.Char(related="insurance_company_id.zip", change_default=True, string="ZIP", readonly=False)
    state_id = fields.Many2one(related="insurance_company_id.state_id", comodel="res.country.state", string='State', ondelete='restrict', help='The name of the state.', readonly=False)
    insurance_type_id = fields.Selection(related="insurance_company_id.insurance_type_id", selection=[('medicare', 'Medicare'),
                                                    ('medicaid', 'Medicaid'),
                                                    ('tricare', 'Tricare'),
                                                    ('champva', 'Champva'),
                                                    ('group_health_plan', 'Group Health Plan'),
                                                    ('feca_blklung', 'FECA Black Lung'),
                                                    ('other', 'Other')], string="Insurance Type", readonly=False)
    # section 2
    edit_insured_sequence = fields.Char(related='insured_sequence', string='Insured’s ID', readonly=False)
    policy_group = fields.Char(string='Policy Group', related='insured_id.policy_group')
    hipaa_sign = fields.Boolean(related='patient_id.hipaa_sign' , string="HIPAA Signature on file", readonly=False)
    hipaa_date = fields.Date(related='patient_id.date', string="Date", readonly=False)
    relationship = fields.Selection([('child_depende', 'Child/Depende'),
                                     ('domestic', 'Domestic'),
                                     ('partner', 'Partner'),
                                     ('other', 'Other'),
                                     ('self', 'Self'),
                                     ('spouse', 'Spouse'),
                                     ('student', 'Student')], string="Pt Relationship", related='insured_id.relationship')
    insured_auth = fields.Boolean(string="Insured Auth")
    insured_date = fields.Date(string="Date")
    insured_sequence_other = fields.Char(string='Insured’s ID')
    relationship_other = fields.Selection([('child_depende', 'Child/Depende'),
                                     ('domestic', 'Domestic'),
                                     ('partner', 'Partner'),
                                     ('other', 'Other'),
                                     ('self', 'Self'),
                                     ('spouse', 'Spouse'),
                                     ('student', 'Student')], string="Pt Relationship")
            # Patient address fields
    patient_name = fields.Char(related='patient_id.name', string="Name", readonly=False)
    patient_address_line_1 = fields.Char(related="patient_id.street", string='Address Line 1', readonly=False)
    patient_address_line_2 = fields.Char(related="patient_id.street2", string='Address Line 2', readonly=False)
    patient_city = fields.Char(related="patient_id.city", string='City', readonly=False)
    patient_zip = fields.Char(related="patient_id.zip", change_default=True, string="ZIP", readonly=False)
    country_id = fields.Many2one(related="patient_id.country_id", comodel='res.country', string="Country")
    patient_state_id = fields.Many2one(related="patient_id.state_id", comodel="res.country.state", string='State', ondelete='restrict', help='The name of the state.', readonly=False)
    patient_date_of_birth = fields.Date(related="patient_id.date_of_birth", string='Date of Birth', readonly=False)
    patient_gender = fields.Selection(related="patient_id.gender", selection=[('male', 'Male'), ('female', 'Female'),
                                                ('unspecified', 'Unspecified')], string="Gender", readonly=False)
    patient_phone = fields.Char(related="patient_id.phone", string="Phone", readonly=False)

    # Subscriber address fields
    def get_subscriber_name(self):
        for res in self:
            res.subscriber_name = str(res.insured_id.first_name) + ' ' + str(res.insured_id.middle_name) + ' ' + str(res.insured_id.last_name)

    subscriber_name = fields.Char(string="Name", readonly=False, compute='get_subscriber_name')
    subscriber_address_line_1 = fields.Char(string='Address Line 1', readonly=False, related='insured_id.address_line_1')
    subscriber_address_line_2 = fields.Char(string='Address Line 2', readonly=False, related='insured_id.address_line_2')
    subscriber_city = fields.Char(string='City', readonly=False, related='insured_id.city')
    subscriber_zip = fields.Char(change_default=True, string="ZIP", readonly=False, related='insured_id.zip')
    subscriber_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', help='The name of the state.', related='insured_id.state_id')
    subscriber_date_of_birth = fields.Date(string='Date of Birth', readonly=False, related='insured_id.date')
    subscriber_gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'),
                                                ('unspecified', 'Unspecified')], string="Gender", readonly=False, related='insured_id.gender')
    subscriber_phone = fields.Char(string="Phone", readonly=False, related='insured_id.phone')

            # Secondary insurance fields
    secondary_patient_name = fields.Char(string="Name", readonly=False)
    secondary_patient_address_line_1 = fields.Char(string='Address Line 1', readonly=False)
    secondary_patient_address_line_2 = fields.Char(string='Address Line 2', readonly=False)
    secondary_patient_city = fields.Char(string='City', readonly=False)
    secondary_patient_zip = fields.Char(change_default=True, string="ZIP", readonly=False)
    secondary_patient_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', help='The name of the state.', readonly=False)
    secondary_patient_date_of_birth = fields.Date(string='Date of Birth', readonly=False)
    secondary_patient_gender = fields.Selection(selection=[('male', 'Male'), ('female', 'Female'),
                                                ('unspecified', 'Unspecified')], string="Gender", readonly=False)
    secondary_patient_phone = fields.Char(string="Phone", readonly=False)

    # section 3
    condition_related = fields.Selection([('employment', 'Employment'),
                                     ('auto_accident', 'Auto Accident'),
                                     ('other_accident', 'Other Accident')],
                                     string="Patient’s Condition Related to ")
    condition_related_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', help='The name of the state.', domain="[('country_id', '=', 233)]")
    other_claim_1 = fields.Char(string='Other Claim ID ')
    other_claim_2 = fields.Char(string='Other Claim ID')
    date_of_current_illness = fields.Date(string="Date of Current Illness ")
    qualif = fields.Char(string='Qualif')
    other_date = fields.Date(string="Other Date ")
    other_selection = fields.Selection([('1', '454 Initial Treatment'),
                                          ('2', '304 Latest Visit or Consultation'),
                                          ('3', '453 Acute Manifestation of a Chronic Condition'),
                                          ('4', '439 Accident'),
                                          ('5', '455 Last X-ray'),
                                          ('6', '471 Prescription'),
                                          ('7', '090 Report Start'),
                                          ('8', '091 Report End'),
                                          ('9', '444 First Visit or Consultation')],
                                     string="Other Selection")
    dates_unable_1 = fields.Date(string="Dates Unable to Work")
    dates_unable_2 = fields.Date(string="Dates Unable to Work")
    dates_hospitalization_1 = fields.Date(string="Hospitalization")
    dates_hospitalization_2 = fields.Date(string="Hospitalization")
    outside_lab = fields.Boolean(string="Outside Lab")
    outside_lab_charge = fields.Float(string="Outside Lab charge")

    # section 4
    edit_qualifier = fields.Selection([('dk', 'DK'), ('dn', 'DN'), ('dq', 'DQ')], 'Referring Provider')
    partner_edit_doctors_id = fields.Many2one('res.partner', string="Doctors", domain=[('doctor_type', '=', 'out_doctor')])
    referring_provider_npi = fields.Char(related='partner_edit_doctors_id.npi', string="Referring Provider NPI", readonly=False)
    referring_provider = fields.Selection([('1', '0B'),
                                           ('2', '1G'),
                                           ('3', 'G2'),
                                           ('4', 'LU')], 'Referring Provider ID')
    qualifier_text = fields.Char(string="Qualifier Text")

    # section 5
    edit_additional_information = fields.Text('Additional Information')
    edit_resubmission_qualifier = fields.Selection([('1_original', '1-Original'),
                                                ('7_replacement', '7-Replacement'),
                                                ('8_void', '8-Void')], 'Resubmission Code')
    edit_resubmission_text = fields.Char('Resubmission Text')
    edit_prior_auth = fields.Char(string='Prior Auth')
    edit_clia = fields.Char('CLIA')

    # section 6
    a_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='A')
    b_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='B')
    c_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='C')
    d_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='D')
    e_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='E')
    f_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='F')
    g_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='G')
    h_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='H')
    i_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='I')
    j_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='J')
    k_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='K')
    l_diagnosis_code_id = fields.Many2one('diagnosis.setup', string='L')
    rendering_provider_npi_id = fields.Many2one(related='employee_provider_id', comodel='hr.employee', string="Rendering Provider NPI", readonly=False)
    service_referring_provider = fields.Selection([('1', '0B'),
                                           ('2', '1G'),
                                           ('3', 'G2'),
                                           ('4', 'LU')], 'Rendering Provider ID')
    patient_acct = fields.Char(string="Patient Acct #", readonly=False)
    service_qualifier_text = fields.Char(string="Qualifier Text")

    # section 7
    provider_tax = fields.Char('Federal Tax ID')
    provider_signature = fields.Char(related='rendering_provider_npi_id.name',
                                     string="Provider Signature", readonly=False)
    location_npi = fields.Char(string="NPI", readonly=False)
    bill_address_line_1 = fields.Char(string='Address Line 1')
    bill_address_line_2 = fields.Char(string='Address Line 2')
    bill_city = fields.Char(string='City')
    bill_zip = fields.Char(string="ZIP")
    bill_state_id = fields.Many2one('res.country.state',
                                    string='State',
                                    ondelete='restrict',
                                    help='The name of the state.')
    bill_qualifier = fields.Char('Facility Qual')
    bill_other_id = fields.Char('Facility ID')

    provider_id = fields.Many2one('res.company', string="Provider", readonly=False)
    provider_bill_address_line_1 = fields.Char(string='Address Line 1')
    provider_bill_address_line_2 = fields.Char(string='Address Line 2')
    provider_bill_city = fields.Char(string='City')
    provider_bill_zip = fields.Char(change_default=True, string="ZIP")
    provider_bill_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', help='The name of the state.')
    provider_location_npi = fields.Char(string="NPI")
    provider_bill_qualifier = fields.Char('Other ID Qual')
    provider_bill_other_id = fields.Char('Other ID')    
    ssn_ein = fields.Selection([('SSN', 'SSN'),
                                ('EIN', 'EIN'),], 'SSN/EIN')  
    accept_assignment = fields.Boolean('Accept Assignment')  

    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'submitted_to_payer':
            self.submission_date = fields.date.today()

    @api.model
    def create(self, vals):
        if vals and not vals.get('sequence', False):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('claim.number')
        return super(ClaimManager, self).create(vals)

    def action_open_invoice(self):
        if self.account_move_id.id:
            return {'name': _('Insurance Invoice'),
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'views': [(self.env.ref('account.view_move_form').id, 'form')],
                    'res_id': self.account_move_id.id,
                    'type': 'ir.actions.act_window',
                    }
        else:
            raise exceptions.AccessDenied("Invoice ref not found.")

    # def action_open_patient_profile(self):
    #     context = dict(self._context) or {}
    #     context.update({'create': False, 'delete': False, 'default_patient': True})
    #     return {'name': _('Patient Profile'),
    #             'view_mode': 'form',
    #             'res_model': 'res.partner',
    #             'views': [(self.env.ref('opt_custom.view_patent_profile_form').id, 'form')],
    #             'domain': [('id', '=', self.patient_id.id)],
    #             'res_id': self.patient_id.id,
    #             'type': 'ir.actions.act_window',
    #             'context': context
    #             }

    def action_open_patient_profile_edit_claim(self):
        context = dict(self._context) or {}
        context.update({'default_patient': True,
                        'from_edit_claim':True,
                        })
        return {'name': _('Patient Profile'),
                'view_mode': 'form',
                'res_model': 'res.partner',
                'views': [(self.env.ref('opt_custom.view_patent_profile_form').id, 'form')],
                'domain': [('id', '=', self.patient_id.id)],
                'res_id': self.patient_id.id,
                'type': 'ir.actions.act_window',
                'context': context
                }

    def action_on_hold(self):
        self.write({'state': 'on_hold'})

    def action_reject_claim(self):
        self.write({'state': 'rejected'})

    def action_cancel_claim(self):
        self.write({'state': 'cancelled'})

    def action_edit_claim_open(self):
        context = dict(self._context) or {}
        context.update({'create': False})
        return {'name': _('Claim Attachment'),
                'view_mode': 'form',
                'res_model': 'claim.manager',
                'views': [(self.env.ref('opt_insurance.edit_claim_form_view').id, 'form')],
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'context': context
                }

    @api.onchange('provider_id', 'primary_insurance_company_id', 'company_id')
    def _onchange_other_insured_name_33(self):
        if self.provider_id:
            self.provider_location_npi = self.provider_id.npi
            self.provider_bill_address_line_1 = self.provider_id.street
            self.provider_bill_address_line_2 = self.provider_id.street2
            self.provider_bill_city = self.provider_id.city
            self.provider_bill_zip = self.provider_id.zip
            self.provider_bill_state_id = self.provider_id.state_id.id
            # if self.provider_id.billing_provider == 'location':
            #     self.provider_bill_address_line_1 = self.company_id.street
            #     self.provider_bill_address_line_2 = self.company_id.street2
            #     self.provider_bill_city = self.company_id.city
            #     self.provider_bill_zip = self.company_id.zip
            #     self.provider_bill_state_id = self.company_id.state_id
            # if self.provider_id.billing_provider_npi == 'location':
            #     self.provider_location_npi = self.company_id.npi

            # if self.provider_id.billing_provider == 'company':
            #     company_id = self.env.company
            #     self.provider_bill_address_line_1 = company_id.street
            #     self.provider_bill_address_line_2 = company_id.street2
            #     self.provider_bill_city = company_id.city
            #     self.provider_bill_zip = company_id.zip
            #     self.provider_bill_state_id = company_id.state_id
            # if self.provider_id.billing_provider_npi == 'company':
            #     self.provider_location_npi = company_id.npi

            # if self.provider_id.billing_provider == 'physician':
            #     self.provider_bill_address_line_1 = self.employee_provider_id.street
            #     self.provider_bill_address_line_2 = self.employee_provider_id.street2
            #     self.provider_bill_city = self.employee_provider_id.city
            #     self.provider_bill_zip = self.employee_provider_id.zip
            #     self.provider_bill_state_id = self.employee_provider_id.state_id
            # if self.provider_id.billing_provider_npi == 'physician':
            #     self.provider_location_npi = self.employee_provider_id.npi

        if self.company_id:
            self.location_npi = self.company_id.npi
            self.bill_address_line_1 = self.company_id.street
            self.bill_address_line_2 = self.company_id.street2
            self.bill_city = self.company_id.city
            self.bill_zip = self.company_id.zip
            self.bill_state_id = self.company_id.state_id.id

    @api.onchange('insurance_company_id', 'primary_insurance_company_id')
    def _onchange_get_fedral_tax(self):
        if self.insurance_company_id:
            if self.insurance_company_id.federal_tax_id == 'company_tax_id':
                self.provider_tax = self.company_id.vat
            elif self.insurance_company_id.federal_tax_id == 'physicians_ssn':
                self.provider_tax = self.employee_provider_id.ssn
            elif self.insurance_company_id.federal_tax_id == 'physicians_tax_id':
                self.provider_tax = self.employee_provider_id.ein

    def action_open_claim_supplemental(self):
        context = dict(self._context) or {}
        return {'name': _('Claim Attachment'),
                'view_mode': 'form',
                'res_model': 'claim.manager',
                'views': [(self.env.ref('opt_custom.edit_claim_form_view_button').id, 'form')],
                'domain': [('id', '=', self.id)],
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'context': context
                }

    @api.onchange('plan_id')
    def _onchange_plan(self):
        self.edit_prior_auth = ''
        if self.plan_id and self.plan_id.prior_authorization_required == 'yes':
            self.edit_prior_auth = self.authorization

    @api.onchange('patient_id', 'primary_insurance_company_id', 'secondary_insurance_company_id')
    def _onchange_lang_localization(self):
        if self.patient_id and self.primary_insurance_company_id:
            self.insured_id = self.insured_sequence = self.insured = ''
            primary_insurance = self.env['spec.insurance'].search([('partner_id', '=', self.patient_id.id),
                                                              ('priority', '=', 'primary'),
                                                              ('carrier_id', '=', self.primary_insurance_company_id.id)], limit=1)
            self.insured_id = primary_insurance.id
            self.insured_sequence = primary_insurance.sequence
            self.insured = primary_insurance.name
        if self.primary_insurance_company_id and self.primary_insurance_company_id.pop_ref_ord_phy == 'yes':
            self.qualifier = 'dk'
            self.partner_doctors_id = self.employee_provider_id.address_home_id
        if self.primary_insurance_company_id and self.primary_insurance_company_id.pop_ref_ord_phy == 'no':
            self.qualifier = ''
            self.partner_doctors_id = False
        self.relationship = self.subscriber_name = self.subscriber_address_line_1 = \
            self.subscriber_address_line_2 = self.subscriber_city = self.subscriber_zip = \
            self.subscriber_phone = ''
        self.subscriber_state_id = self.subscriber_date_of_birth = self.subscriber_gender = False
        if self.patient_id and self.insurance_company_id:
            primary_insurance = self.env['spec.insurance'].search([('partner_id', '=', self.patient_id.id),
                                                              ('priority', '=', 'primary'),
                                                              ('carrier_id', '=', self.insurance_company_id.id)], limit=1)
            if primary_insurance:
                self.relationship = primary_insurance.relationship
                self.subscriber_name = primary_insurance.name
                self.subscriber_address_line_1 = primary_insurance.address_line_1
                self.subscriber_address_line_2 = primary_insurance.address_line_2
                self.subscriber_city = primary_insurance.city
                self.subscriber_zip = primary_insurance.zip
                self.subscriber_state_id = primary_insurance.state_id.id
                self.subscriber_date_of_birth = primary_insurance.date
                self.subscriber_gender = primary_insurance.gender
                self.subscriber_phone = primary_insurance.phone
        # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        self.relationship_other = self.secondary_patient_name = self.secondary_patient_address_line_1 = \
            self.secondary_patient_address_line_2 = self.secondary_patient_city = self.secondary_patient_zip = \
            self.secondary_patient_phone = ''
        self.secondary_patient_state_id = self.secondary_patient_date_of_birth = self.secondary_patient_gender = self.secondary_plan_id = False
        if self.patient_id and self.secondary_insurance_company_id:
            secondary_insurance = self.env['spec.insurance'].search([('partner_id', '=', self.patient_id.id),
                                                              ('carrier_id', '=', self.secondary_insurance_company_id.id)], limit=1)
            if secondary_insurance:
                self.relationship_other = secondary_insurance.relationship
                self.secondary_patient_name = secondary_insurance.name
                self.secondary_patient_address_line_1 = secondary_insurance.address_line_1
                self.secondary_patient_address_line_2 = secondary_insurance.address_line_2
                self.secondary_patient_city = secondary_insurance.city
                self.secondary_patient_zip = secondary_insurance.zip
                self.secondary_patient_state_id = secondary_insurance.state_id.id
                self.secondary_patient_date_of_birth = secondary_insurance.date
                self.secondary_patient_gender = secondary_insurance.gender
                self.secondary_patient_phone = secondary_insurance.phone
                self.insured_sequence_other = secondary_insurance.sequence
                self.secondary_plan_id = secondary_insurance.plan_id.id
        self.patient_acct = ''
        if self.patient_id and self.patient_id.bank_ids and self.patient_id.bank_ids[0]:
            self.patient_acct = self.patient_id.bank_ids[0].acc_number


class ClaimLine(models.Model):
    _name = "claim.line"
    _description = "Claim Line"

    claim_manager_id = fields.Many2one('claim.manager', string="Insurance Claim")
    procedure_code = fields.Char('CPT/HCPCS')
    spec_modifier_ids = fields.Many2many('spec.lens.modifier',
                                        'claim_line_modifiers_rel',
                                        'claim_id', 'modifiers_id',
                                         string='Modifiers')
    retail = fields.Float("Charges")
    pt_total = fields.Float("Pt Total")
    payments = fields.Float("Payments")
    ins_receivable = fields.Float("Ins Receivable")
    procedure_code_id = fields.Many2one('spec.procedure.code', string='CPT/HCPCS')
    name = fields.Char('Description', related='procedure_code_id.description')
    service_date = fields.Date(string='Date of Service')
    place_of_service = fields.Char('Place of Service')
    facility = fields.Selection([('telehealth', '02-Telehealth'), ('school', '03-School'), ('india_fee_standin', '05-Indian Health Service Free-standin Facility'),
                                ('india_provide_based', '06-Indian Health Service Provider-based Facility'), ('tribal_fee_standin', '07-Tribal 638 Free-standing Facility'),
                                ('tribal_provide_based', '08-Tribal 638 Provider-based Facility'), ('prison_correctional_facility', '09-Prison/Correctional Facility'), ('office', '11-Office'),
                                ('home', '12-Home'), ('assisted_living_facility', '13-Assisted Living Facility'), ('group_home', '14-Group Home'), ('mobile_unite', '15-Mobile Unit'),
                                ('temporary_lodging', '16-Temporary Lodging'), ('health_clinick', '17-Walk-in Retail Health Clinic'), ('place_employment_works', '18-Place of Employment Worksite'),
                                ('outpaatient_hospital', '19-Off Campus-Outpatient Hospital'), ('skilled_nursing_facility', '31-Skilled Nursing Facility'), ('nursing_facility', '32-Nursing Facility'),
                                ('hospice', '34-Hospice'), ('comprehensive_inpatient_rehabilitation', '61-Comprehensive Inpatient Rehabilitation Facility'),
                                ('comprehensive_outpatient_rehabilitation', '62-Comprehensive Outpatient Rehabilitation Facility'), ('other_place_service', '99-Other Place of Service')],
                                string="facility", default='office')
    quantity = fields.Float('Quantity')
    emg_svc = fields.Boolean('Emg')
    days_units = fields.Integer('Days/Units')
    epsdt = fields.Selection([('a_v', 'AV'),
                            ('s_2', 'S2'),
                            ('s_t', 'ST'),
                            ('n_u', 'NU')], string="EPSDT")
    diagnosis_code_ids = fields.Many2many('diagnosis.setup',
                                        'claim_line_diagnosis_rel',
                                        'claim_id', 'diagnosis_id',
                                         string='Dx Pointer')


class ClaimSupplementalInformation(models.Model):
    _name = "claim.supplemental.information"
    _description = "Claim Supplemental Information"

    report_code_id = fields.Many2one('report.code', string='Report Code', required='1')
    transmission_type_id = fields.Many2one('transmission.type', string='Transmission Type', required='1')
    attachment_control_number = fields.Char('Attachment Control Number')
    claim_manager_id = fields.Many2one('claim.manager', string="Insurance Claim")
    edit_claim_id = fields.Many2one('edit.claim', string="Edit Claim")


class ReportCode(models.Model):
    _name = "report.code"
    _description = "Report Code"

    name = fields.Char('Report Code', required='1')
    code = fields.Char(string="Code")

    def name_get(self):
        result = []
        for record in self:
            name = str(record.code) + '-' + str(record.name)
            result.append((record.id, name))
        return result

class TransmissionType(models.Model):
    _name = "transmission.type"
    _description = "Transmission Type"

    name = fields.Char('Transmission Type', required='1')
    code = fields.Char(string="Code")

    def name_get(self):
        result = []
        for record in self:
            name = str(record.code) + '-' + str(record.name)
            result.append((record.id, name))
        return result


# class EditClaim(models.Model):
#     _name = "edit.claim"
#     _description = "Edit Claim"
#     _rec_name = 'claim_id'

#     claim_id = fields.Many2one('claim.manager', string="Insurance Claim")


