# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ManufacturerOptions(models.TransientModel):
    _name = "manufacturer.options.wizard"
    # _order = "create_date DESC"

    product_template_id = fields.Many2one('product.template')
    product_product_ids = fields.Many2many('product.product')
    base_curve = fields.Many2one('base.curve.lines.wizard', string='Base Curve')
    color = fields.Many2one('spec.contact.lens.color.type', string='Color')

    sphere = fields.Char(string='Sphere')
    cylinder = fields.Char(string='Cylinder')
    axis = fields.Char(string='Axis')
    add = fields.Char(string='Add')
    # multi_focal = fields.Char(string='Multi Focal')
    multi_focal = fields.Many2one('multi.focal.lines.wizard', string='Multi Focal')

    @api.onchange('product_template_id')
    def get_color_domain(self):
        if self.product_template_id:
            return {"domain": {"color": [('id', 'in', list(set(self.product_template_id.product_variant_ids.color_type_id.ids)))]}}

    @api.onchange('product_template_id')
    def get_base_curve_domain(self):
        base_curves = []
        base_curve_ids = self.env['base.curve.lines.wizard']
        for product_variant_lines in self.product_template_id.product_variant_ids:
            base_curve = product_variant_lines.bc
            if base_curve not in base_curves and base_curve != '' and base_curve != False:
                base_curves.append(base_curve)
                base_curve_ids |= base_curve_ids.create({
                    'name': base_curve
                })
        return {"domain": {"base_curve": [('id', 'in', base_curve_ids.ids)]}}

    @api.onchange('product_template_id')
    def get_multi_focal_domain(self):
        multi_focals = []
        multi_focal_ids = self.env['multi.focal.lines.wizard']
        for product_variant_lines in self.product_template_id.product_variant_ids:
            multi_focal = product_variant_lines.multi_focal
            if multi_focal not in multi_focals and multi_focal != '' and multi_focal != False:
                multi_focals.append(multi_focal)
                multi_focal_ids |= multi_focal_ids.create({
                    'name': multi_focal
                })
        return {"domain": {"multi_focal": [('id', 'in', multi_focal_ids.ids)]}}

    @api.onchange('product_template_id', 'base_curve', 'color', 'sphere', 'cylinder', 'axis', 'add', 'multi_focal')
    def _product_product_lines(self):
        domain = []
        if self.product_template_id:
            domain.append(('product_tmpl_id', '=', self.product_template_id.id))
        if self.base_curve:
            domain.append(('bc', '=', self.base_curve.name))
        if self.color:
            domain.append(('color_type_id', '=', self.color.id))
        if self.sphere:
            domain.append(('sphere', '=', self.sphere))
        if self.cylinder:
            domain.append(('cylinder', '=', self.cylinder))
        if self.axis:
            domain.append(('axis', '=', self.axis))
        if self.add:
            domain.append(('add', '=', self.add))
        if self.multi_focal:
            domain.append(('multi_focal', '=', self.multi_focal.name))
        self.product_product_ids = self.env['product.product'].search(domain)


class BaseCurveLines(models.TransientModel):
    _name = "base.curve.lines.wizard"
    # _order = "create_date DESC"

    name = fields.Char()


class MultiFocalLines(models.TransientModel):
    _name = "multi.focal.lines.wizard"
    # _order = "create_date DESC"

    name = fields.Char()
