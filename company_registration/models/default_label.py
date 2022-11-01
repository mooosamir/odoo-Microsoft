from odoo import models, fields, api


class DefaultLabel(models.Model):
    _name = 'default.label'
    _description = 'default.label'

    name = fields.Char(string='Label')
