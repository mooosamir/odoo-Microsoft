
from odoo import models, fields
from datetime import date


class ContactLensInherit(models.Model):
    _inherit = 'spec.contact.lenses'

    gls_computer_lens = fields.Boolean(string="Computer Lens")
    gls_anti_reflective = fields.Boolean(string="Anti-Reflective")

    def name_get(self):
        dateformat = self.env['res.lang'].search([('code', '=', self._context.get('lang'))], limit=1).date_format or '%Y/%m/%d'
        result = []
        for record in self:
            name = record.id
            if record.exam_date:
                name = str(record.exam_date.strftime(dateformat)) + ' ' + str(record.rx_type_char)
                if record.expiration_date and record.expiration_date < date.today():
                    name += ' (EXPIRED)'
            result.append((record.id, name))
        return result