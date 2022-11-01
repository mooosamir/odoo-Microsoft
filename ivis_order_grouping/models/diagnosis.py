
from odoo import models, api


class DiagnosisInherit(models.Model):
    _inherit = 'diagnosis.setup'

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', ('name', operator, name), ('description', operator, name)]
        return super(DiagnosisInherit, self).search(domain, limit=limit).name_get()

    def name_get(self):
        result = []

        for rec in self:
            result.append((rec.id, '%s - %s ' % (rec.name, rec.description)))

        return result
