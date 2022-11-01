from odoo import api, fields, models, _


class GroupOfTaxes(models.Model):
    _name = 'group.of.taxes'
    _description = 'group.of.taxes'

    tax_name = fields.Char(string='Tax Name')
    tax_computation = fields.Selection(string="Tax Computation", required=False,
                                   selection=[('group', 'Group of Taxes'),
                                              ('percent', 'Percentage of Price'),
                                              ],)
    amount = fields.Float(string='Amount')
    taxes_id = fields.Many2one('account.tax', string='Taxes')


