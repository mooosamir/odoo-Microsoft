from odoo import models, fields, api


class CategoryBasedTax(models.Model):
    _name = 'category.based.tax'

    product_category = fields.Many2one('product.category', string='Product Category')
    tax_applied = fields.Many2one('account.tax', string='Tax Applied')
    company_field = fields.Many2one('res.company', string='')

    @api.onchange('tax_applied')
    def on_change(self):
        res = self.env['product.template'].search([('categ_id','=',self.product_category.name)])
        for r in res:
            r.taxes_id = [(4,self.tax_applied.id)]
