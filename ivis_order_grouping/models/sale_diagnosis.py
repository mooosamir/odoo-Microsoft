
from odoo import models, fields, api, exceptions, _


class SaleDiagnosis(models.Model):
    _name = 'sale.diagnosis.setup'
    _description = 'sale.diagnosis.setup'
    _rec_name = 'diagnosis_code_id'

    sale_id = fields.Many2one('sale.order')
    move_id = fields.Many2one('account.move')
    diagnosis_code_id = fields.Many2one('diagnosis.setup', string='Diagnosis', required=True)
    seq = fields.Char(string="Diagnosis Pointer")

    # def unlink(self):
    #     print("RUN!")
    #     res = super(SaleDiagnosis, self).unlink()
    #     for i in range(len(self.sale_id.diagnosis_lines) + 65):
    #         self.write({'seq': chr(i)})
    #     return res

    @api.model
    def default_get(self, fields_list):
        res = super(SaleDiagnosis, self).default_get(fields_list)
        if (len(self._context.get('diagnosis_lines', [])) + 65) < 77:
            res.update({'seq': chr(len(self._context.get('diagnosis_lines', [])) + 65)})
        else:
            raise exceptions.ValidationError(_('The ability to enter diagnosis pointer is A-L'))
        return res