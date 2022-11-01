from odoo import models, fields, api


class IntegratedPartners(models.Model):
    _name = 'integrated.partners'
    _description = 'integrated.partners'

    name = fields.Char(string='Service Provider Name')