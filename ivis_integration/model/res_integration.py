from odoo import fields, models


class ResIntegration(models.Model):
    _name = 'res.integration'

    name = fields.Char(string='Name', required=True)
    res_integration_lines = fields.One2many('res.integration.line', 'res_integration_id')
    company_id = fields.Many2one('res.company', string='Company')
    active = fields.Boolean(string='Active', default=True)


class IntegrationLine(models.Model):
    _name = "res.integration.line"

    res_integration_id = fields.Many2one('res.integration')
    key = fields.Char(string='Key', required=True)
    value = fields.Char(string='Value', required=True)
