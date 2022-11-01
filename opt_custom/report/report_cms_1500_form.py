# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import ustr


class ReportCMS1500(models.AbstractModel):
    _name = 'report.opt_custom.report_cms_1500'

    def __init__(self, cr, uid):
        super(ReportCMS1500, self).__init__(cr, uid)
        self.other_insurences = []

    def _get_other_insured_name_9(self, claim):
        other_insurences = claim.patient_id.insurance_ids.filtered(lambda l: l != claim.insured_id
                                                                   and l.insurance_type == claim.insured_id.insurance_type)
        self.other_insurences = other_insurences
        result = ','.join(other_insurences.mapped('name'))
        return result

    def _get_other_insured_name_9a(self, claim):
        result = ','.join(self.other_insurences.mapped('sequence'))
        return result

    def _get_other_insured_name_9d(self, claim):
        result = ','.join(self.other_insurences.mapped('plan_id.name'))
        return result

    def _get_other_insured_name_33(self, claim):
        billing_provider = claim.primary_insurance_company_id.billing_provider
        data_33 = {}
        result = []
        if billing_provider == 'location':
            if claim.clame_location_id.street:
                result.append(ustr(claim.clame_location_id.street))
            if claim.clame_location_id.street2:
                result.append(' ' + ustr(claim.clame_location_id.street2))
            if claim.clame_location_id.city:
                result.append(' ' + ustr(claim.clame_location_id.city))
            if claim.clame_location_id.state_id.name:
                result.append(' ' + ustr(claim.clame_location_id.state_id.name))
            if claim.clame_location_id.zip:
                result.append(' ' + ustr(claim.clame_location_id.zip))
            if claim.clame_location_id.country_id.name:
                result.append(' ' + ustr(claim.clame_location_id.country_id.name))

        if billing_provider == 'company':
            company_id = self.env.company
            if company_id.street:
                result.append(ustr(company_id.street))
            if company_id.street2:
                result.append(' ' + ustr(company_id.street2))
            if company_id.city:
                result.append(' ' + ustr(company_id.city))
            if company_id.state_id.name:
                result.append(' ' + ustr(company_id.state_id.name))
            if company_id.zip:
                result.append(' ' + ustr(company_id.zip))
            if company_id.country_id.name:
                result.append(' ' + ustr(company_id.country_id.name))
        if billing_provider == 'physician':
            if claim.employee_provider_id.street:
                result.append(ustr(claim.employee_provider_id.street))
            if claim.employee_provider_id.street2:
                result.append(' ' + ustr(claim.employee_provider_id.street2))
            if claim.employee_provider_id.city:
                result.append(' ' + ustr(claim.employee_provider_id.city))
            if claim.employee_provider_id.state_id.name:
                result.append(' ' + ustr(claim.employee_provider_id.state_id.name))
            if claim.employee_provider_id.zip:
                result.append(' ' + ustr(claim.employee_provider_id.zip))
            if claim.employee_provider_id.country_id.name:
                result.append(' ' + ustr(claim.employee_provider_id.country_id.name))
        if result:
            data_33.update({'address': result})

        billing_provider_npi = claim.primary_insurance_company_id.billing_provider_npi
        npi = ''
        if billing_provider_npi == 'location':
            npi = claim.clame_location_id.npi
        if billing_provider_npi == 'company':
            npi = company_id.npi
        if billing_provider_npi == 'physician':
            npi = claim.employee_provider_id.npi
        if npi:
            data_33.update({'npi': npi})

        billing_provider_other_id = claim.primary_insurance_company_id.billing_provider_other_id
        other = ''
        if billing_provider_other_id == 'location':
            other = claim.clame_location_id.vat
        if billing_provider_other_id == 'company':
            other = company_id.vat
        if billing_provider_other_id == 'physician':
            other = claim.employee_provider_id.license
        if other:
            data_33.update({'other': other})
        return data_33

    def _get_other_insured_name_11d(self, claim):
        result = False
        if self.other_insurences:
            result = True
        return result

    def _get_other_insured_name_24i(self, claim):
        result = False
        datas = {'state_license_number': '0B - State License Number',
                 'provider_upin_number': '1G-Provider UPIN Number',
                 'provider_commercial_number': 'G2-Provider Commercial Number',
                 'location_number': 'LU-Location Number',
                 'provider': 'ZZ-Provider',
                 'taxonomy': 'Taxonomy'}
        if claim.primary_insurance_company_id.rendering_provider_qualifier:
            result = datas[claim.primary_insurance_company_id.rendering_provider_qualifier] + '  ' + ustr(claim.primary_insurance_company_id.rendering_provider_qualifier_char)
        return result

    @api.model
    def _get_report_values(self, docids, data=None):

        return {
            'doc_ids': docids,
            'doc_model': 'claim.manager',
            'docs': self.env['claim.manager'].browse(docids),
            'report_type': data.get('report_type') if data else '',
            'get_other_insured_name_9': self._get_other_insured_name_9,
            'get_other_insured_name_9a': self._get_other_insured_name_9a,
            'get_other_insured_name_9d': self._get_other_insured_name_9d,
            'get_other_insured_name_11d': self._get_other_insured_name_11d,
            'get_other_insured_name_24i': self._get_other_insured_name_24i,
            'get_other_insured_name_33': self._get_other_insured_name_33,

        }
