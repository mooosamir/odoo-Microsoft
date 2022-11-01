# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from datetime import date, datetime
import dateutil.rrule as rrule
import re
from dateutil.relativedelta import relativedelta
from email.policy import default
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class ResPartner(models.Model):
    _inherit = 'res.partner'

    insurance_ids = fields.One2many('spec.insurance', 'partner_id', string="Insurance")
    insurance_authorizations_ids = fields.One2many('spec.insurance.authorizations', 'partner_id', string="Insurance Authorizations")


class InsuranceAuthorizations(models.Model):
    _name = 'spec.insurance.authorizations'
    _description = 'Insurance Authorizations'

    authorizations_type = fields.Selection([('authorization', 'Authorization'), ('referral', 'Referral')], string="Type",  default='authorization')
    insurance_id = fields.Many2one('spec.insurance', string="Insurance")
    plan_id = fields.Many2one('spec.insurance.plan', string="Plan")
    authorizations_number = fields.Char(string="Authorization")
    authorizations_date = fields.Date(string='Start', default=fields.Date.today())
    expiration_date = fields.Date(string='End')
    employee_id = fields.Many2one('hr.employee', string="Verified By", default=lambda self: self.env.user.employee_id.id)
    name = fields.Char(string="Name")
    address = fields.Char(string="Address")
    phone = fields.Char(string="Phone")
    exam = fields.Boolean(string="Exam", default=True)
    farme = fields.Boolean(string="Frame", default=True)
    lenses = fields.Boolean(string="Lenses", default=True)
    contact_lens = fields.Boolean(string="Contact Lens", default=True)
    vision_medical = fields.Selection([('vision', 'Vision'), ('medical', 'Medical')], string="Vision Medical", default='vision')
    """Vision Fileds"""
    exam_copay = fields.Char(string="Exams")
    medical_copay = fields.Char(string="Material/Lens")
    frame_allowance = fields.Char(string="Frame")
    frame_range = fields.Char(string="Frame Range")
    frame_range_to = fields.Char(string="Frame Range")
    contact_lens_allowance = fields.Char(string="Contact Lens")
    total_allowance = fields.Char(string="Total Allowance")
    post_contact_glasses = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Post Cataract Glasses", default="no")
    surgery_date = fields.Date(string="Surgery Date")
    referring_provider = fields.Many2one('hr.employee', string="Referring Provider")
    """Medical"""
    office_copay = fields.Char(string="Office Copay")
    deductible_amount = fields.Char(string="Deductible Amount")
    remaining_deductible_amount = fields.Char(string="Remaining Deductible Amount")
    specialist_deductible = fields.Char(string="Specialist Deductible")
    family_deductible_amount = fields.Char(string="Family Deductible Amount")
    family_remaining_deductible = fields.Char(string="Family Remaining Deductible")
    co_insurance = fields.Char(string="Co-insurance")
    out_of_pocket_max = fields.Char(string="Out of Pocket Max")
    remaining_out_pocket_max = fields.Char(string="Remaining Out of Pocket")
    cataract_co_manage = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Cataract Co-Manage")
    cataract_referring_provider = fields.Many2one('hr.employee', string="Referring Provider")
    cataract_surgery_date = fields.Date(string="Surgery Date")
    cataract_asm = fields.Date(string="ASM")
    cataract_rql = fields.Date(string="RQL")
    cataract_second_surgery = fields.Boolean(string="Second Surgery")
    yag_co_manage = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="YAG Co-Manage")
    yag_surgery_date = fields.Date(string="Surgery Date")
    yag_referring_provider = fields.Many2one('hr.employee', string="Referring Provider")
    yag_asm = fields.Date(string="ASM")
    yag_rql = fields.Date(string="RQL")
    yag_second_surgery = fields.Boolean(string="Second Surgery")
    currency_id = fields.Many2one('res.currency', string="currency", default=lambda self: self.env.user.company_id.currency_id, readonly="1")
    """Referral Fields"""
    referring_physician = fields.Many2one('hr.employee', string="Referring Provider")
    referring_physician_npi = fields.Char(string="Referring Provider NPI")
    referring_physician_tel = fields.Char(string="Referring Provider Tel")
    date_of_vist = fields.Date(string="Date of Visit")
    number_of_vist = fields.Char(string="Number of Visit")
    procedure_code = fields.Char(string="Procedure Code")
    diagnosis_code = fields.Char(string="Diagnosis Code")
    benefit_char = fields.Char(string="Benefits")
    notes = fields.Text(string="Notes")
    partner_id = fields.Many2one('res.partner', string="Partner")

    @api.onchange('authorizations_date')
    def _onchange_authorizations_date(self):
        if self.authorizations_date:
            self.expiration_date = self.authorizations_date + relativedelta(months= +1)
        if self.authorizations_date.month == 12:
            self.expiration_date = self.authorizations_date + relativedelta(days= +31)

    @api.onchange('cataract_surgery_date')
    def _onchange_cataract_surgery_date(self):
        if self.cataract_surgery_date:
            self.cataract_rql = self.cataract_surgery_date + relativedelta(months= +3)

    @api.onchange('yag_surgery_date')
    def _onchange_yag_surgery_date(self):
        if self.yag_surgery_date:
            self.yag_rql = self.yag_surgery_date + relativedelta(months= +3)

    @api.onchange('insurance_id')
    def _onchange_insurance_id(self):
        if self.insurance_id:
            self.plan_id = self.insurance_id.plan_id

    @api.constrains('vision_medical')
    def check_exam(self):
        for rec in self:
            if rec.authorizations_type == 'authorization' and rec.vision_medical == 'vision':
                if not rec.exam and not rec.farme and not rec.lenses and not rec.contact_lens:
                    raise ValidationError('In Authorization please select one of the (Exam, Frame, Lenses, Contact Lenses)')

    @api.onchange('referring_physician_tel')
    def _onchange_referring_physician_tel(self):
        if self.referring_physician_tel and self.referring_physician_tel.isdigit():
            if len(self.referring_physician_tel) >= 10:
                self.referring_physician_tel = '({}) {}-{}'.format(self.referring_physician_tel[:3], self.referring_physician_tel[3:6], self.referring_physician_tel[6:])

    @api.onchange('vision_medical', 'exam', 'lenses', 'contact_lens', 'farme')
    def _onchange_name(self):
        name = ''
        if self.vision_medical == 'vision':
            if self.exam:
                name += 'E' + ' ' or ''
            if self.farme:
                name += 'F' + ' ' or ''
            if self.lenses:
                name += 'L' + ' ' or ''
            if self.contact_lens:
                name += 'CL' + ' ' or ''
        if self.vision_medical == 'medical':
            name += 'Medical' + ' ' or ''
        self.benefit_char = name or ''

    # @api.onchange('vision_medical', 'exam', 'lenses', 'contact_lens', 'farme')
    # def check_medical(self):
    #     if self.vision_medical == 'medical':
    #         if self.exam or self.lenses or self.farme or self.contact_lens:
    #             self.vision_medical = 'vision'
    #             return {'warning': {'title': _("User Alert!"),
    #                     'message': _("You can not select medical when vision and one of the (Exam, Frame, Lenses, Contact Lenses) selected")}}
