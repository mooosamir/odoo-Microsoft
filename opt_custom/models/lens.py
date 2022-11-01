# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning, UserError


class LensType(models.Model):
    _name = 'spec.lens.type'
    _description = 'Lens Type'
    
    name = fields.Char(string='Lens Type')
    code = fields.Char(string='Lens Code')


class LensBrand(models.Model):
    _name = 'spec.lens.brand'
    _description = 'Lens Brand'
    
    name = fields.Char(string='Lens Brand')


class LensStyle(models.Model):
    _name = 'spec.lens.style'
    _description = 'Lens Style'
    
    name = fields.Char(string='Lens Style')
    code = fields.Char(string="Lens Code")


class LensMaterial(models.Model):
    _name = 'spec.lens.material'
    _description = 'Lens Material'
    
    name = fields.Char(string='Lens Material')
    code = fields.Char(string="Material Code")


class LensFilter(models.Model):
    _name = 'spec.lens.filter'
    _description = 'Lens Filter'
    
    name = fields.Char(string='Lens Filter')
    code = fields.Char(string='Lens Code')
    

class LensColors(models.Model):
    _name = 'spec.lens.colors'
    _description = 'Lens Colors'
    
    name = fields.Char(string='Lens Colors')
    code = fields.Char(string='Color Code')
    
    
class ProcedureCode(models.Model):
    _name = 'spec.procedure.code'
    _description = 'Procedure Code'
    
    name = fields.Char(string='Procedure')
    description = fields.Char(string='Description')
    lens_type_id = fields.Many2one('spec.lens.type', string='Lens Type')
    sphere_or_cyclinder = fields.Selection([('sphere','Sphere'),('sphereocyclinder','Spherocylinder')],
                                           string='Sphere/Sphereocylinder')
    min_sphere = fields.Float('Min Sphere')
    max_sphere = fields.Float('Max Sphere')
    min_sphere_2 = fields.Float('Min Sphere Negative')
    max_sphere_2 = fields.Float('Max Sphere Negative')
    min_cylinder = fields.Float('Min Cylinder')
    max_cylinder = fields.Float('Max Cylinder')
    min_cylinder_2 = fields.Float('Min Cylinder Negative')
    max_cylinder_2 = fields.Float('Max Cylinder Negative')

    def name_get(self):
        result = []
        for record in self:
            name = str(record.name) + ' ' + str(record.description)
            result.append((record.id, name))
        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        args = args or []
        context = self._context or {}
        if context.get('payment_product_code') and context.get('remittance_sale_order_id'):
            sale_order_id = self.env['sale.order'].browse(context.get('remittance_sale_order_id'))
            sale_products = sale_order_id.order_line.mapped('product_id').product_tmpl_id.ids
            treatment_line = self.env['spec.lens.treatment.line'].search([('template_treatment_id', 'in', sale_products)])
            treatment_line_codes = treatment_line.mapped('pro_code_id').ids
            if treatment_line_codes:
               args.append(('id', 'in', tuple(treatment_line_codes)))
        return super(ProcedureCode, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


class Modifier(models.Model):
    _name = 'spec.lens.modifier'
    _description = 'Lens Modifier'

    name = fields.Char(string='Modifier')


class LensCategory(models.Model):
    _name = 'spec.lens.category'
    _description = 'Lens Category'

    short_code = fields.Char(string='Short Code', required=1)
    name = fields.Char(string='Lens Category', required=1)


class LensTreatment(models.Model):
    _name = 'spec.lens.treatment'
    _description = 'Lens Treatment'
    
    category_id = fields.Many2one('spec.lens.category', string='Category')
    brand_id = fields.Many2one('spec.lens.brand', string='Brand')
    name = fields.Char(string='Description')
    treatment_line_ids = fields.One2many('spec.lens.treatment.line', 'treatment_id', string='Treatment Line')
    pair_each = fields.Selection([('pair', 'Pair'), ('each', 'Each')], string='Pair/Each')


class LensTreatmentChildLine(models.Model):
    _name = 'spec.lens.treatment.line'
    _description = 'Lens Treatment Line'
    _rec_name = 'pro_code_id'

    pro_code_id = fields.Many2one('spec.procedure.code', string='Procedure')
    price = fields.Float(string='Price')
    treatment_id = fields.Many2one('spec.lens.treatment', string='Treatment')
    template_treatment_id = fields.Many2one('product.template', string='Product Treatment')
    modifier_id = fields.Many2one('spec.lens.modifier', string='Modifier')
    currency_id = fields.Many2one('res.currency', string='Currency',
                         default=lambda self: self.env.company.currency_id)


class LensMeasurementType(models.Model):
    _name = 'spec.lens.measurement.type'
    _description = 'Lens Measurement'
    
    name = fields.Char(string='Measurement')
    min_value = fields.Integer(string='Minimum Value')
    max_value = fields.Integer(string='Maximum Value')


class EdgeType(models.Model):
    _inherit = "spec.edge.type"
 
    procedure_code_id = fields.Many2one('spec.procedure.code', string='Procedure')
    suggested_retail = fields.Float(string='Suggested Retail')


class LensPowerGrid(models.Model):
    _name = "spec.lens.power.grid"
    _description = 'Lens Power Grid'
        
    name = fields.Char(string='Power Grid Name')
    pair_each = fields.Selection([('pair', 'Pair'), ('each', 'Each')], default='pair', string='Pair/Each')
    add_power_ids = fields.One2many('spec.power.grid.power', 'power_grid_id', string='ADD Power')
    power_grid_param_ids = fields.One2many('spec.sphere.cylinder.grid', 'sphere_cylinder_grid_id', string='Sphere')

    @api.model
    def default_get(self, fields):
        result = super(LensPowerGrid,self).default_get(fields)
        power_list = [3.25, 3.50, 3.75, 4.00, 4.25, 4.50, 4.75, 5.00]
        dic_list = []
        for power in power_list:
            dic_list.append((0,0, {'power': power}))
        result['add_power_ids'] = dic_list
        return result


class PowerGridPower(models.Model):
    _name = "spec.power.grid.power"
    _description = 'Power Grid Add Power'
 
    power = fields.Float(string='Power')
    suggested_retail = fields.Float(string='Suggested Retail')
    power_grid_id = fields.Many2one('spec.lens.power.grid', string='Power Gird')


class SphereCylinderGrid(models.Model):
    _name = "spec.sphere.cylinder.grid"
    _description = 'Spec Sphere Cylinder Grid'

    sphere_from = fields.Float(string='Sphere From')
    sphere_to = fields.Float(string='Sphere To')
    cylinder_from = fields.Float(string='Cylinder From')
    cylinder_to = fields.Float(string='Cylinder To')
    suggested_retail = fields.Float(string='Suggested Retail')
    sphere_cylinder_grid_id = fields.Many2one('spec.lens.power.grid', string='Sphere Cylinder Grid')


class LensPrismGrid(models.Model):
    _name = "spec.lens.prism.grid"
    _description = 'Lens Prism Grid'

    name = fields.Char(string='Prism Grid Name')
    eye_combine = fields.Selection([('per_eye', 'Per Eye'), ('combine', 'Combine')], default='combine', string='PerEye / Combined')
    add_prism_ids = fields.One2many('spec.prism.grid.power', 'prism_grid_id', string='ADD Power')

    @api.model
    def default_get(self, fields):
        result = super(LensPrismGrid,self).default_get(fields)
        prism_list = [0.00, 0.25, 0.50, 0.75, 1.00,
                      1.25, 1.50, 1.75, 2.00,
                      2.25, 2.50, 2.75, 3.00,
                      3.25, 3.50, 3.75, 4.00,
                      4.25, 4.50, 4.75, 5.00,
                      5.25, 5.50, 5.75, 6.00,
                      6.25, 6.50, 6.75, 7.00,
                      ]
        dic_list = []
        for prism in prism_list:
            dic_list.append((0,0, {'power': prism}))
        result['add_prism_ids'] = dic_list
        return result


class PrismGridPower(models.Model):
    _name = "spec.prism.grid.power"
    _description = 'Prism Grid Add Power'
    
    power = fields.Float(string='Power')
    price = fields.Float(string='Price')
    prism_grid_id = fields.Many2one('spec.lens.prism.grid', string='Prism Gird')
    

class OverSizePricing(models.Model):
    _name = "spec.oversized.pricing"
    _description = 'Lens Oversized Pricing'
    
    name = fields.Char(string='Description')
    suggested_retail = fields.Float(string='Suggested Retail')
    ed_over = fields.Boolean(string='ED Over')
    ed_over_text = fields.Char(string='ED Over Text')
    blank_size_over = fields.Boolean(string='Blank Size Over')
    blank_size_over_text = fields.Char(string='Blank Size Over Text')
    pair_each = fields.Selection([('pair', 'Pair'), ('each', 'Each')], default='pair', string='Pair/Each')
    

class LensSelection(models.Model):
    _name = "spec.lens.selection"
    _description = 'Lens Selection'
 
    name = fields.Char(string='Name')
    lens_selection_line_ids = fields.One2many('product.template', 'lens_selection_id',
                                                string="Lens Parameters")


class Coating(models.Model):
    _name = "spec.coating"
    _description = 'Coating'
 
    name = fields.Char(string='Coating')


class Manufacturer(models.Model):
    _name = "spec.manufacturer"
    _description = 'Manufacturer'
 
    name = fields.Char(string='Manufacturer')


class FinishSemiFinishLens(models.Model):
    _inherit = "product.supplierinfo"
    _description = 'Finish-Semi Finish Lens'

    sequence = fields.Integer(string='Sequence')
    wholesale = fields.Char(string='Listed Wholesale each')
    lens_type_id = fields.Many2one('spec.lens.type', string='Lens Type', required=False)
    material_id = fields.Many2one('spec.lens.material', string='Material', required=False)
    coating_id = fields.Many2one('product.template', string='Coating', required=False, domain="[('categ_id.name','=','Lens Treatment')]")
    filter_id = fields.Many2one('spec.lens.filter', string='Filter', required=False)
    color_id = fields.Many2one('spec.lens.colors', string='Lens Color', required=False)
    manufacturer_id = fields.Many2one('spec.lens.brand', string='Manufacturer', required=False)
    asherical = fields.Boolean(string='Asherical')
    finish_semi = fields.Selection([('semi', 'Semi'), ('finished', 'Finished')], required=False, default='finished', string='Semi/Finished')
    finish_child_ids = fields.One2many('spec.finish.lens.child', 'product_finish_lens_id', string='Finish Lens Child Table')
    semi_finish_child_ids = fields.One2many('spec.semi.finish.lens.child', 'product_finish_lens_id', string='Semi Finish Lens Child Table')
    template_treatment_id = fields.Many2one('product.template', string='Product Treatment')
    lens_selection_id = fields.Many2one('spec.lens.selection', string='Lens Priority Group') 


class FinishLensChild(models.Model):
    _name = "spec.finish.lens.child"
    _description = 'Finish Lens Child Table'

    diameter = fields.Float(string='Diameter')
    sphere = fields.Float(string='Sphere')
    cylinder = fields.Float(string='Cylinder')
    base_curve = fields.Float(string='Base Curve')
    center_thickness = fields.Float(string='Center Thickness')
    right_opc = fields.Char(string='Right OPC')
    left_opc = fields.Char(string='Left OPC')
    # finish_lens_id = fields.Many2one('product.supplierinfo', string='Finish Lens')
    product_finish_lens_id = fields.Many2one('product.template', string='Finish Lens')
    
    
class SemiFinishLensChild(models.Model):
    _name = "spec.semi.finish.lens.child"
    _description = 'Semi Finish Lens Child Table'

    diameter = fields.Float(string='Diameter')
    base_curve = fields.Float(string='Base Curve')
    add = fields.Float(string='ADD')
    true_curve = fields.Float(string='True Curve')
    front_radius = fields.Float(string='Front Radius')
    sag = fields.Float(string='50mm Sag')
    back_curve = fields.Float(string='Back Curve')
    back_radius = fields.Float(string='Back Radius')
    ct_nominal = fields.Float(string='CT Nominal')
    et_nominal = fields.Float(string='ET Nominal')
    drop = fields.Float(string='Drop')
    inset = fields.Float(string='Inset')
    right_opc = fields.Char(string='Right OPC')
    left_opc = fields.Char(string='Left OPC')
    # finish_lens_id = fields.Many2one('product.supplierinfo', string='Finish Lens')
    product_finish_lens_id = fields.Many2one('product.template', string='Finish Lens')


class LensListParameters(models.Model):
    _name = "spec.lens.list.parameter"
    _description = 'Lens List Parameters'
    
    procedure_code_id = fields.Many2one('spec.procedure.code', string='Procedure')
    price = fields.Float(string='Price')
    lens_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Lens')]", string='Lens')
    

class LensList(models.Model):
    _inherit = "product.template"
    
    retail_price = fields.Float(string='Retail Price')
    pair_each = fields.Selection([('pair', 'Pair'), ('each', 'Each')], default='pair', string='Pair/Each')


    lens_active = fields.Boolean(string='Active', default=True)
    lens_type_id = fields.Many2one('spec.lens.type', string='Lens Type')
    lens_brand_id = fields.Many2one('spec.lens.brand', string='Brand')
    style_id = fields.Many2one('spec.lens.style', string='Style')
    material_id = fields.Many2one('spec.lens.material', string='Material')
    filter_id = fields.Many2one('spec.lens.filter', string='Filter')
    color_id = fields.Many2one('spec.lens.colors', string='Lens Color')
    lens_param_ids = fields.One2many('spec.lens.list.parameter', 'lens_id', string='Lens Parameter')
    treatment_child_ids = fields.One2many('spec.lens.treatment.child', 'lens_id', string='Treatments')
    measurement_child_ids = fields.One2many('spec.lens.measurement.child', 'lens_id', string='Measurement')
    power_grid_id = fields.Many2one('spec.lens.power.grid', string='Power Grid')
    prism_grid_id = fields.Many2one('spec.lens.prism.grid', string='Prism Grid')
    oversized_id = fields.Many2one('spec.oversized.pricing', string='Oversized')
    minimum_fitting_height = fields.Char(string="Min Fitting Height")
    fitting_cross = fields.Text(string="Fitting Cross")
    manufactuering_process = fields.Char(string="Manufacturing Process")
    progressive_design_type = fields.Char(string="PAL Design Type")
    fitting_centration_chart = fields.Binary(string="Centration Chart")
    engraving_nasal = fields.Binary(string="Engravings")
    engraving_temperal = fields.Binary(string="Engraving Temperal")
    available_rebate = fields.Binary(string="Available Rebate")
    fitting_centration_chart_file_name = fields.Char(string='Fitting/Centration Chart File Name')
    engraving_nasal_file_name = fields.Char(string='Engraving Nasal File Name')
    engraving_temperal_file_name = fields.Char(string='Engraving Temperal File Name')
    available_rebate_file_name = fields.Char(string='Available Rebate File Name')
    website = fields.Char(String="Website")
    note = fields.Text(string='Notes')
    vw_code_type = fields.Char(String="VW Code Type")
    vw_code_style = fields.Char(String="VW Code Style")
    vw_code_material = fields.Char(String="VW Code Material")
    treatment_line_ids = fields.One2many('spec.lens.treatment.line', 'template_treatment_id', string='HCPCS')
    retail_price_lens = fields.Float(compute="_compute_total_retail_price", string='Total proce')
    header_name = fields.Char(compute="_compute_header_name", string='Header')
    product_lens_type = fields.Selection([
        ('consu', 'Consumable'),
        ('product', 'Storable Product')], string='Product Type', default='consu', required=True)
    semi_finish_lens_ids = fields.One2many('product.template', 'template_treatment_id', string='Lens Parameters')

    @api.onchange('product_lens_type')
    def _onchange_product_lens_type(self):
        self.type = self.product_lens_type

    @api.onchange('lens_type_id')
    def _onchange_lens_type_id(self):
        if self.lens_type_id.id:
            parent_category_id = self.env['product.category'].search([('name', '=', 'Lens')])
            if not parent_category_id.id:
                parent_category_id = self.env['product.category'].create({
                    'name': 'Lens'
                })
            product_category_id = self.env['product.category'].search([('name', '=', self.lens_type_id.name),
                                                                       ('parent_id', '=', parent_category_id.id)])
            if not product_category_id.id:
                product_category_id = self.env['product.category'].create({
                    'name': self.lens_type_id.name,
                    'parent_id': parent_category_id.id
                })
            self.categ_id = product_category_id.id
        else:
            self.categ_id = 0

    @api.model
    def default_get(self, vals):
        return super(LensList, self).default_get(vals)

    @api.depends('name')
    def _compute_header_name(self):
        if self._context.get('default_prd_categ_name') and self._context.get('default_prd_categ_name') == 'Lens':
            for rec in self:
                rec.header_name = rec.name

    @api.depends('treatment_line_ids')
    def _compute_total_retail_price(self):
        amount = 0.0
        self.retail_price_lens = 0.0
        for rec in self:
            if rec._context.get('default_prd_categ_name') and rec._context.get('default_prd_categ_name') == 'Lens':
                amount = sum(lens.price for lens in rec.treatment_line_ids)
                rec.retail_price_lens = amount
                if rec.retail_price_lens !=0:
                    rec.list_price = rec.retail_price_lens
            if rec._context.get('default_prd_categ_name') and rec._context.get('default_prd_categ_name') == 'Lens Treatment':
                amount = sum(lens.price for lens in rec.treatment_line_ids)
                rec.retail_price_lens = amount
                if rec.retail_price_lens !=0:
                    rec.list_price = rec.retail_price_lens

    def _check_pdf(self, file_name):
        """This Method check file is pdf or not"""
        valid_file_name = file_name.split('.')
        if valid_file_name[-1].lower() != 'pdf':
            raise ValidationError("You can upload only PDF file!")

    @api.constrains('fitting_centration_chart', 'engraving_nasal_file_name', 'available_rebate_file_name',
        'engraving_temperal_file_name')
    def _check_file_type(self):
        """Check available rebate file only PDF allow"""
        for record in self:
            if record.fitting_centration_chart_file_name:
                record._check_pdf(record.fitting_centration_chart_file_name)
            if record.engraving_nasal_file_name:
                record._check_pdf(record.engraving_nasal_file_name)
            if record.available_rebate_file_name:
                record._check_pdf(record.available_rebate_file_name)
            if record.engraving_temperal_file_name:
                record._check_pdf(record.engraving_temperal_file_name)


class LensTreatmentChild(models.Model):
    _name = "spec.lens.treatment.child"
    _description = 'Lens Treatment Child'

    lnclude = fields.Boolean(string='Included')
    category_id = fields.Many2one('spec.lens.category', string='Category')
    # lens_treatment_id = fields.Many2one('spec.lens.treatment', string='Description')
    lens_treatment_id = fields.Many2one('treatment.for.lens', string='Description')
    lens_selection_id = fields.Many2one('spec.lens.selection', string='Lens Selection Priority')
    lens_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Lens')]", string='Lens')

    @api.onchange('category_id')
    def _inchange_category_id(self):
        self.lens_treatment_id = False
        if self.category_id.id:
            return {'domain': {'lens_treatment_id': [('category_id', '=', self.category_id.id)]}}


class TreatmentForLens(models.Model):
    _name = "treatment.for.lens"
    _description = 'Treatments of lens'
    _rec_name = 'description'

    category_id = fields.Many2one('spec.lens.category', string='Category')
    description = fields.Char(string='Description')
    code = fields.Char(string='Vwcode')


class LensMeasurementChild(models.Model):
    _name = "spec.lens.measurement.child"
    _description = 'Lens Measurement Child'

    lnclude = fields.Boolean(string='Required')
    measurement_id = fields.Many2one('spec.lens.measurement.type', string='Measurement')
    min_value = fields.Float(string='Min Value')
    max_value = fields.Float(string='Max Value')
    lens_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Lens')]", string='Lens')
    
