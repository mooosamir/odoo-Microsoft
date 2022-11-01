from odoo import models


class SpecInsurance(models.Model):
    _inherit = 'spec.insurance'

    def name_get(self):
        result = []

        for rec in self:
            result.append((rec.id, '%s' % (
                                        rec.carrier_id.name)
                           ))

        return result
