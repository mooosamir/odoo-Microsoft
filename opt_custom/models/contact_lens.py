# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    wholesale_cost = fields.Float('Wholesale Cost')


class ContactLensProduct(models.Model):
    _inherit = "product.product"

    configurations_last_modified_on = fields.Date(string='FramesData Last Sync')
    bc = fields.Char(string='BC')
    diam = fields.Char(string='Diam')
    sphere = fields.Char(string='Sphere')
    cylinder = fields.Char(string='Cylinder')
    axis = fields.Char(string='Axis')
    add = fields.Char(string='Add')
    multi_focal = fields.Char(string='Multi-focal')
    color_type_id = fields.Many2one('spec.contact.lens.color.type',
                                    string='Color Type')
    color_id = fields.Many2one('spec.color.family', string='Color')
    color_code_id = fields.Many2one('spec.color.code.family', string='Color Code')
    eye = fields.Char(string='Eye')
    trial = fields.Boolean(string='Trial')
    lens_discontinue = fields.Boolean(string='Discontinued')
    lens_discont_date = fields.Date(string='Discontinue Date')
    prod_packaging_id = fields.Many2one('product.packaging', 'Package', ondelete="restrict")
    product_min_qty = fields.Float('Min Quantity')
    product_max_qty = fields.Float('Max Quantity')
    a = fields.Float(string='A')
    b = fields.Float(string='B')
    ed = fields.Float(string='ED')
    bridge = fields.Char(string='Bridge')
    temple = fields.Char(string='Temple')

    lens_color_id = fields.Many2one('spec.lens.colors', string='Lens Color')
    dbl = fields.Float(string='DBL')
    ed_angle = fields.Float(string='ED Angle')
    trace_file = fields.Binary(string="Trace File")
    product_tag_ids = fields.Many2many(
        'spec.frame.tag', 'product_product_tag_rel', 'product_id', 'tag_id', string='Tags')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        args = args or []
        context = self._context or {}
        if context.get('opt_product') and context.get('partner_id'):
            supplier_ids = self.env['product.supplierinfo'].search([('name', '=', context.get('partner_id'))])
            product_list = supplier_ids.mapped('product_tmpl_id').ids
            if product_list:
                args.append(('product_tmpl_id', 'in', tuple(product_list)))
        return super(ContactLensProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                       access_rights_uid=access_rights_uid)

    def name_get(self):
        res = super(ContactLensProduct, self).name_get()
        for rec in res:
            procuct_id = rec[0]
            product_rec = self.browse(procuct_id)
            if product_rec.product_tmpl_id.categ_id.name == 'Frames':
                frame_name = ''
                if product_rec.product_tmpl_id.model_number:
                    frame_name += ' ' + tools.ustr(product_rec.product_tmpl_id.model_number) + ' '
                if product_rec.color_id.name:
                    frame_name += ' ' + tools.ustr(product_rec.color_id.name) + ' '
                if product_rec.eye:
                    frame_name += ' ' + tools.ustr(product_rec.eye) + ' '
                if product_rec.bridge:
                    frame_name += ' ' + tools.ustr(product_rec.bridge) + ' '
                if product_rec.temple:
                    frame_name += ' ' + tools.ustr(product_rec.temple) + ' '
                if product_rec.barcode:
                    frame_name += ' ' + tools.ustr(product_rec.barcode) + ' '
                product_index = res.index(rec)
                res.pop(product_index)
                res.append((procuct_id, frame_name))
            if product_rec.product_tmpl_id.categ_id.name == 'Contact Lens':
                contact_lens_name = ''
                if product_rec.name:
                    contact_lens_name += ' ' + tools.ustr(product_rec.name) + ' '
                if product_rec.bc:
                    contact_lens_name += ' ' + tools.ustr(product_rec.bc) + ' '
                if product_rec.sphere:
                    contact_lens_name += ' ' + tools.ustr(product_rec.sphere) + ' '
                if product_rec.cylinder:
                    contact_lens_name += ' ' + tools.ustr(product_rec.cylinder) + ' '
                if product_rec.axis:
                    contact_lens_name += ' ' + tools.ustr(product_rec.axis) + ' '
                if product_rec.add:
                    contact_lens_name += ' ' + tools.ustr(product_rec.add) + ' '
                if product_rec.multi_focal:
                    contact_lens_name += ' ' + tools.ustr(product_rec.multi_focal) + ' '
                if product_rec.barcode:
                    contact_lens_name += ' ' + tools.ustr(product_rec.barcode) + ' '
                if product_rec.color_type_id.id:
                    contact_lens_name += ' ' + tools.ustr(product_rec.color_type_id.name) + ' '
                product_index = res.index(rec)
                res.pop(product_index)
                res.append((procuct_id, contact_lens_name))
            if product_rec.product_tmpl_id.categ_id.name == 'Accessory':
                accessory_name = ''
                if product_rec.description:
                    accessory_name += ' ' + tools.ustr(product_rec.description) + ' '
                if product_rec.barcode:
                    accessory_name += ' ' + tools.ustr(product_rec.barcode) + ' '

                product_index = res.index(rec)
                res.pop(product_index)
                res.append((procuct_id, accessory_name))
            if product_rec.product_tmpl_id.categ_id.name == 'Lens':
                lens_name = ''
                if product_rec.name:
                    lens_name += ' ' + tools.ustr(product_rec.name) + ' '
                if product_rec.barcode:
                    lens_name += ' ' + tools.ustr(product_rec.barcode) + ' '

                product_index = res.index(rec)
                res.pop(product_index)
                res.append((procuct_id, lens_name))
        return res

    def init(self):
        # res = super(ContactLensProduct, models.Model).init()
        tools.drop_index(self._cr, 'product_product_combination_unique', self._table)
        # return res

    def write(self, vals):
        res = super(ContactLensProduct, self).write(vals)
        stock_obj = self.env['stock.warehouse.orderpoint']
        for rec in self:
            orderpoint = stock_obj.search([('product_id', '=', rec.id)], limit=1)
            if orderpoint:
                if vals.get('product_min_qty'):
                    if vals.get('product_min_qty') < 0:
                        raise UserError(_('Min Quantity must be greater than zero.'))
                    orderpoint.update({'product_min_qty': vals.get('product_min_qty')})
                if vals.get('product_max_qty'):
                    if vals.get('product_max_qty') < 0:
                        raise UserError(_('Min Quantity must be greater than zero.'))
                    orderpoint.update({'product_max_qty': vals.get('product_max_qty')})
            elif not self._context.get('no_create'):
                if rec.product_max_qty != 0:
                    vals = {'product_id': rec.id,
                            'product_min_qty': rec.product_min_qty,
                            'product_max_qty': rec.product_max_qty}
                    rec.orderpoint_ids = [(0, 0, vals)]
        return res

    @api.model
    def create(self, vals):
        res = super(ContactLensProduct, self).create(vals)
        product_template_obj = self.env['product.template']
        product_attribute_value_obj = self.env['product.attribute.value']
        product_attribute_line_obj = self.env['product.template.attribute.line']
        product_temp_attribute_value_obj = self.env['product.template.attribute.value']
        if not self._context.get('create_product_product') and vals.get('barcode'):
            product_template = product_template_obj.browse(vals.get('product_tmpl_id'))
            product_attribute = self.env.ref('opt_custom.product_attribute_upc')

            product_attribute_value = self.env['product.attribute.value'].search(
                [('attribute_id', '=', product_attribute.id), ('name', '=', vals.get('barcode'))], limit=1)
            if not product_attribute_value.id:
                product_attribute_value = product_attribute_value_obj.create({'name': vals.get('barcode'),
                                                                              'attribute_id': product_attribute.id})
            if not product_template.attribute_line_ids:
                product_attribute_line_obj.create({'product_tmpl_id': product_template.id,
                                                   'attribute_id': product_attribute.id,
                                                   'value_ids': [(4, product_attribute_value.id)]
                                                   })
            elif product_template.attribute_line_ids:
                product_template_attribute_line = product_template.attribute_line_ids.filtered(
                    lambda l: l.attribute_id == product_attribute)
                if len(product_template_attribute_line) > 1:
                    product_template_attribute_line = product_template.attribute_line[0]
                product_template_attribute_line.sudo().write({'value_ids': [(4, product_attribute_value.id)]})

            product_temp_attribute_value = product_temp_attribute_value_obj.search(
                [('product_attribute_value_id.name', 'like', vals.get('barcode'))], limit=1)
            res.with_context(no_create=True).sudo().write(
                {'product_template_attribute_value_ids': [(4, product_temp_attribute_value.id)]})

        #  For creation of Reordering Rules
        for record in res:
            if record.product_min_qty > 0 and record.product_max_qty > 0:
                vals = {'product_id': record.id,
                        'product_min_qty': record.product_min_qty,
                        'product_max_qty': record.product_max_qty}
                record.orderpoint_ids = [(0, 0, vals)]
        return res

    # def unlink(self):
    #     self.product_template_attribute_value_ids.unlink()
    #     return super().unlink()

    @api.onchange('lens_discontinue')
    def _get_lens_discont_date(self):
        self.lens_discont_date = False
        if self.lens_discontinue:
            self.lens_discont_date = fields.Date.today()


class ContactLens(models.Model):
    _inherit = "product.template"

    discontinue = fields.Boolean(string='Discontinued')
    discont_date = fields.Date(string='Discontinue Date')
    contact_lens_manufacturer_id = fields.Many2one('spec.contact.lens.manufacturer',
                                                   string='Manufacturer', ondelete="restrict")
    units_per_box = fields.Char(string='Units Per Box', default=6)
    # color_type_id = fields.Many2one('spec.contact.lens.color.type',
    #                                 string='Color Type')
    wear_period_id = fields.Many2one('spec.contact.lens.wear.period',
                                     string='Wear Schedule')
    replacement_schedule_id = fields.Many2one('spec.contact.lens.replacement.schedule',
                                              string="Replacement Schedule")
    trial_lens_id = fields.Many2one('product.template',
                                    domain="[('prd_categ_name', '=', 'Contact Lens')]",
                                    string="Trial Lens")
    contact_lens_summary_ids = fields.One2many('spec.contact.lens.summary',
                                               'contact_lens_id',
                                               string="Contact Lens Summary")
    material = fields.Char(string="Material")
    fda_group = fields.Char(string="FDA Group")
    water_content = fields.Char(string="Water Content")
    dk = fields.Char(string="DK")
    modulus = fields.Char(string="Modulus")
    ct = fields.Char(string="CT")
    oz = fields.Char(string="OZ")
    uv_blocking = fields.Char(string="UV Blocking")
    manuf_process = fields.Char(string="Manuf. Process")
    appearance = fields.Char(string="Appearance")
    toric_type = fields.Char(string="Toric Type")
    indications_ids = fields.Char(string="Indication")
    cost = fields.Float(string="Cost")
    con_lens_suggested_retail = fields.Float(string="Suggested  Retail")
    procedure_code = fields.Many2one('spec.procedure.code', string='Procedure')
    fitting_guide_or_package_insert = fields.Binary(string="Fitting Guide or Package Insert")
    fitting_guide_or_package_insert_file_name = fields.Char(string='File Name')
    available_rebate = fields.Binary(string="Available Rebate")
    available_rebate_file_name = fields.Char(string='File Name')
    website = fields.Char(String="Website")
    note = fields.Text(string='Notes')
    extended_wear = fields.Selection([('y', "Yes"), ('n', "No")], "Extended Wear")
    wholesale_cost = fields.Float("Wholesale Cost")
    lens_type = fields.Selection([('soft', "Soft"), ('rgp', "RGP")], "Lens Type", default='soft')
    product_packaging_id = fields.Many2one('product.packaging', string='Package', ondelete="restrict")
    sty_id = fields.Char(String="STY_ID")
    ser_id = fields.Char(String="SER_ID")

    @api.model
    def default_get(self, vals):
        if self._context.get('default_prd_categ_name') and self._context.get('default_prd_categ_name') == 'Contact Lens':
            product_category_id = self.env['product.category'].search([('name', '=', 'Contact Lens')])
            if not product_category_id.id:
                product_category_id = self.env['product.category'].create({
                    'name': 'Contact Lens'
                })
            self.categ_id = product_category_id.id
        return super(ContactLens, self).default_get(vals)

    def _create_variant_ids(self):
        if not self._context.get('create_product_product') and self._context.get('disable_varients'):
            return True
        return super(ContactLens, self)._create_variant_ids()

    @api.constrains('lens_type')
    def _check_lens_type(self):
        for rec in self:
            if not rec.lens_type:
                raise UserError(_('Please select Lens Type.'))

    @api.constrains('available_rebate_file_name')
    def _check_available_rebate_file_name(self):
        """Check available rebate file only PDF allow"""
        for record in self:
            if record.available_rebate_file_name:
                file_name = record.available_rebate_file_name.split('.')
                if file_name[-1].lower() != 'pdf':
                    raise UserError("You can upload only PDF file!")

    @api.constrains('fitting_guide_or_package_insert')
    def _check_fitting_guide_or_package_insert(self):
        """Check Fitting guide or package insert only PDF allow"""
        for record in self:
            if record.fitting_guide_or_package_insert_file_name:
                file_name = record.fitting_guide_or_package_insert_file_name.split(
                    '.')
                if file_name[-1].lower() != 'pdf':
                    raise UserError("You can upload only PDF file!")

    @api.onchange('discontinue')
    def _onchange_discontinue(self):
        """Onchange on discontinue"""
        self.discont_date = self.discontinue and fields.Date.today() or False

    def name_get(self):
        result = []
        for lens in self:
            manufacturer = lens.contact_lens_manufacturer_id.name if lens.contact_lens_manufacturer_id else ''
            name = manufacturer + ' ' + lens.name
            result.append((lens.id, name))
        return result


class ContactLensSummary(models.Model):
    _name = 'spec.contact.lens.summary'
    _description = 'Contact Lens Summary'

    bc = fields.Char(string='BC')
    diam = fields.Float(string='Diam')
    sphere_from = fields.Float(string='Sphere From')
    sphere_to = fields.Float(string='Sphere To')
    sphere_step = fields.Float(string='Sphere Step')
    contact_lens_id = fields.Many2one('product.template', domain="[('categ_id.name', '=', 'Contact Lens')]",
                                      string="Contact Lens ID")


# class ContactLensConfigurations(models.Model):
#     _inherit = 'product.product'
#     _description = 'Contact Lens configurations'

#     @api.onchange('bc')
#     def get_contact_name(self):
#         for rec in self:
#             if rec.bc:
#                 rec.name = rec.bc
#                 # print("yyyyyyyyyyyy",rec.contact_lens_id, rec.product_tmpl_id)
#             else:
#                 rec.name = ''

#     bc = fields.Char(string='BC')
#     bc_id = fields.Char(string='BC')
#     diam = fields.Float(string='Diam')
#     sphere = fields.Float(string='Sphere')
#     cylinder = fields.Float(string='Cylinder')
#     axis = fields.Char(string='Axis')
#     add = fields.Char(string='Add')
#     multi_focal = fields.Char(string='Multi-focal')
#     color = fields.Char(string='Color')
#     upc = fields.Char(string='UPC')

# class ContactLensType(models.Model):
#     _name = 'spec.contact.lens.type'
#     _description = 'Lens Style'

#     name = fields.Char(string='Lens Type')


class ContactLensColorType(models.Model):
    _name = 'spec.contact.lens.color.type'
    _description = 'Contact Lens Color Style'

    name = fields.Char(string='Color Type')


class ContactWearPeriod(models.Model):
    _name = 'spec.contact.lens.wear.period'
    _description = 'Contact Lens Wear Period'

    name = fields.Char(string='Wear Period')


class ContactLensReplacementSchedule(models.Model):
    _name = 'spec.contact.lens.replacement.schedule'
    _description = 'Contact Lens Replacement schedule'

    name = fields.Char(string='Replacement Schedule')
    code = fields.Char(string='Code')


class ContactLensManufacturer(models.Model):
    _name = 'spec.contact.lens.manufacturer'
    _description = 'Contact Lens Manufacturer'

    name = fields.Char(string='Manufacturer')
    code = fields.Char(string='Manufacturer Id')
