from odoo import models

class SpecInsuranceAuthorization(models.Model):
    _inherit = 'spec.insurance.authorizations'

    def name_get(self):
        result = []

        for rec in self:
            result.append((rec.id, rec.authorizations_number if rec.authorizations_number else ''))

        return result