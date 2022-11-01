# -*- coding: utf-8 -*-

from odoo import fields, models, api


class Accessory(models.Model):
    _inherit = "product.template"

    acc_category_id = fields.Many2one('spec.accessory.category', string='Category', ondelete="restrict")
    accessory_brand_id = fields.Many2one('spec.brand.brand', string='Brand',
                                         copy=False, ondelete="restrict",
                                         domain="[('brand_type', '=', 'accessory')]")
    acc_suggested_retail = fields.Float(string="Suggested  Retail")
    pro_code_id = fields.Many2one('spec.procedure.code', string='Procedure')
    modifier_id = fields.Many2one('spec.lens.modifier', string='Modifier')
    image = fields.Image(string="Image", attachment=True)
    currency_id = fields.Many2one('res.currency', string="currency", readonly=1,
    					default=lambda self: self.env.user.company_id.currency_id)
    cost_price = fields.Monetary(string="Cost")
    upc = fields.Integer(string='UPC')
    accessory_header_name = fields.Char(compute="_compute_accessory_header_name", string='Header')

    @api.depends('name')
    def _compute_accessory_header_name(self):
        if self._context.get('default_prd_categ_name') and self._context.get('default_prd_categ_name') == 'Accessory':
            for rec in self:
                rec.accessory_header_name = rec.name

class AccessoryCategory(models.Model):
    _name = 'spec.accessory.category'
    _description = 'Accessory Category'

    name = fields.Char(string='Category')


