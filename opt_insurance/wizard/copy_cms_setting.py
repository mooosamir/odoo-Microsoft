# -*- coding: utf-8 -*-

from odoo import fields, models


class CopyCmsSetting(models.Model):
    _name = 'spec.copy.cms.setting'
    _description = 'COPY CMS Settings'

    insurance_company_ids = fields.Many2many('res.partner', 'insurance_company_copy_rel',
                                             'insurance_company_id', 'copy_cms_id', string="Insurance Company",
                                             domain="[('is_company','=',1), ('is_insurance','=',1)]")

    def action_copy_cms_setting(self):
        """Method to Copy CMS Setting."""
        active_id = self._context.get('active_id')
        insurance_id = self.env['res.partner'].browse(active_id)
        for insurance_company_id in self.insurance_company_ids:
            if insurance_company_id:
                insurance_company_id.generate_claims = insurance_id.generate_claims
                insurance_company_id.claim_output = insurance_id.claim_output
                insurance_company_id.pop_sec_ins_cms = insurance_id.pop_sec_ins_cms
                insurance_company_id.pop_ref_ord_phy = insurance_id.pop_ref_ord_phy
                insurance_company_id.place_of_service = insurance_id.place_of_service
                insurance_company_id.contract_lens_unites = insurance_id.contract_lens_unites
                insurance_company_id.rendering_provider_qualifier = insurance_id.rendering_provider_qualifier
                insurance_company_id.rendering_provider_qualifier_char = insurance_id.rendering_provider_qualifier_char
                insurance_company_id.accept_assignment = insurance_id.accept_assignment
                insurance_company_id.amount_paid = insurance_id.amount_paid
                insurance_company_id.federal_tax_id = insurance_id.federal_tax_id
                insurance_company_id.signature_physician_supplier = insurance_id.signature_physician_supplier
                insurance_company_id.service_facility_other_id = insurance_id.service_facility_other_id
                insurance_company_id.service_facility_other_id_char = insurance_id.service_facility_other_id_char
                insurance_company_id.billing_provider = insurance_id.billing_provider
                insurance_company_id.billing_provider_npi = insurance_id.billing_provider_npi
                insurance_company_id.billing_provider_other_id = insurance_id.billing_provider_other_id
