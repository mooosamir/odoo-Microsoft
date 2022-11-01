from odoo import fields, models, api


class LensTreatment(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, vals):
        if self._context.get('default_prd_categ_name') and self._context.get('default_prd_categ_name') == 'Lens Treatment':
            self.uom_id = self.env.ref('uom.product_uom_unit').id
        return super(LensTreatment, self).default_get(vals)

    category_id = fields.Many2one('spec.lens.category', string='Category')
    vw_code = fields.Char(String="VW Code")
    vw_description = fields.Char(String="VW Description")
    incompatible_treatments_ids = fields.Many2many('product.template',
                                                    'procuct_template_template_rel',
                                                    'parent_id','child_id',
                                                    string="Incompatible Treatments")

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id.id:
            parent_category_id = self.env['product.category'].search([('name', '=', 'Lens Treatment')])
            if not parent_category_id.id:
                parent_category_id = self.env['product.category'].create({
                    'name': 'Lens Treatment'
                })
            product_category_id = self.env['product.category'].search([('name', '=', self.category_id.name),
                                                                       ('parent_id', '=', parent_category_id.id)])
            if not product_category_id.id:
                product_category_id = self.env['product.category'].create({
                    'name': self.category_id.name,
                    'parent_id': parent_category_id.id
                })
            self.categ_id = product_category_id.id
        else:
            self.categ_id = 0
