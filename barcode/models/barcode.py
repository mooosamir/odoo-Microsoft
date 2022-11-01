from odoo import models, fields, api, _

class Barcode(models.Model):
    _inherit = 'product.product'

    product = fields.Char(string='Product', compute='product_compute')
    variant = fields.Char(string='Variant', compute='product_compute')
    description = fields.Char(string='Description')

    @api.depends('product_tmpl_id')
    def product_compute(self):
        for s in self:
            if s.product_tmpl_id.categ_id.name == 'Frames':
                # for frame product name
                if s.collection_id.name and s.name:
                    s.product = str(s.collection_id.name) + " " +  str (s.name)
                elif s.collection_id.name:
                    s.product = str(s.collection_id.name)
                elif s.name:
                    s.product = str(s.name)
                else:
                    s.product = ""

                # for frame variant
                s.variant = ""
                variants = [s.color_id.name, s.eye, s.bridge, s.temple ]
                for variant in variants:
                    if variant:
                        s.variant += " " + variant

            elif s.product_tmpl_id.categ_id.name == 'Lens':
                # for lens product name
                if s.name:
                    s.product = str(s.name)
                else:
                    s.product = ""
                s.variant = ""

            elif s.product_tmpl_id.categ_id.name == 'Lens Treatment':
                # for lens treatment product name
                if s.name:
                    s.product = str(s.name)
                else:
                    s.product = ""
                s.variant = ""

            elif s.product_tmpl_id.categ_id.name == 'Contact Lens':
                # for contact lens product name
                if s.name and s.uom_id.name:
                    s.product = str(s.name) + " " + str(s.uom_id.name)
                elif s.name:
                    s.product = str(s.name)
                elif s.uom_id.name:
                    s.product = s.uom_id.name
                else:
                    s.product = ""

                # for contact lens variant
                s.variant = ""
                variants = [s.bc, s.sphere, s.cylinder, s.axis, s.add, s.multi_focal, s.color_type_id.name ]
                for variant in variants:
                    if variant:
                        s.variant += " " + variant

            elif s.product_tmpl_id.categ_id.name == 'Services':
                # for service product name
                if s.name:
                    s.product = str(s.name)
                else:
                    s.product = ""
                s.variant = ""

            elif s.product_tmpl_id.categ_id.name == 'Accessory':
                # for accessory product name
                if s.acc_category_id.name and s.name:
                    s.product = s.acc_category_id.name + " " + s.name
                elif s.acc_category_id.name:
                    s.product = s.acc_category_id.name
                elif s.name:
                    s.product = s.name
                else:
                    s.product = ""


                if s.description:
                    s.variant = s.description
                else:
                    s.variant = ""
            else:
                s.product = ''
                s.variant = ''








