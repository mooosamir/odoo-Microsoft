# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductLensParameters(models.Model):
    _inherit = "product.template"
    _description = 'Finish-Semi Finish Lens'

    sequence = fields.Integer(string='Sequence')
    wholesale = fields.Char(string='Listed Wholesale each')
    lens_type_id = fields.Many2one('spec.lens.type', string='Lens Type')
    material_id = fields.Many2one('spec.lens.material', string='Material')
    coating_id = fields.Many2one('product.template', string='Coating', domain="[('categ_id.name','=','Lens Treatment')]")
    filter_id = fields.Many2one('spec.lens.filter', string='Filter')
    color_id = fields.Many2one('spec.lens.colors', string='Lens Color')
    manufacturer_id = fields.Many2one('spec.lens.brand', string='Manufacturer')
    asherical = fields.Boolean(string='Asherical')
    finish_semi = fields.Selection([('semi', 'Semi'), ('finished', 'Finished')], default='finished', string='Semi/Finished')
    finish_child_ids = fields.One2many('spec.finish.lens.child', 'product_finish_lens_id', string='Finish Lens Child Table')
    semi_finish_child_ids = fields.One2many('spec.semi.finish.lens.child', 'product_finish_lens_id', string='Semi Finish Lens Child Table')
    template_treatment_id = fields.Many2one('product.template', string='Product Treatment')
    lens_selection_id = fields.Many2one('spec.lens.selection', string='Lens Priority Group')
    vendor_id = fields.Many2one('res.partner', string="Vendor")

    @api.onchange('lens_type_id', 'vendor_id')
    def _onchange_lens_type_vendor(self):
        if self._context.get('default_prd_categ_name') and self._context.get('default_prd_categ_name') == 'Lens Parameter':
            self.name = ''
            if self.lens_type_id and self.vendor_id:
                self.name = self.vendor_id.name + " " +self.lens_type_id.name
