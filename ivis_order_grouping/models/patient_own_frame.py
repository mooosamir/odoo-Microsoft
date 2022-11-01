
from odoo import models


class PatientOwnFrameInherit(models.Model):
    _inherit = 'patient.own.frame'

    def name_get(self):
        result = []
        for record in self:
            if record.model_number:
                name = str(record.model_number) + ' ' + str(record.color) + ' ' + str(record.edge_id.name)
            else:
                name = record.id
            result.append((record.id, name))
        return result