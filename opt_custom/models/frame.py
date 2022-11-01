# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class Brand(models.Model):
    _name = "spec.brand.brand"
    _description = 'Spectacle Brand'
    _inherit = ['image.mixin']
    _order = 'name'

    name = fields.Char('Name')
    brand_type = fields.Selection([('frame', 'Frame'), ('accessory', 'Accessory')], string='Type')
    bfmid = fields.Char('BrandFramesMasterID',required=True)
    mfmid = fields.Many2one('spec.frame.manufacturer', string='ManufacturerFramesMasterID',required=True)


class Collection(models.Model):
    _name = "spec.collection.collection"
    _inherit = ['image.mixin']
    _description = 'Spectacle Collection'

    name = fields.Char('Name')
    brand_id = fields.Many2one('spec.brand.brand', string='Brand', copy=False,
                                domain="[('brand_type', '=', 'frame')]",required=True)
    cfmid = fields.Char('CollectionFramesMasterID',required=True)


class PartCategory(models.Model):
    _name = "spec.part.category"
    _description = 'Part Category'

    name = fields.Char('Name')


class LensesType(models.Model):
    _name = "spec.lenses.type"
    _description = 'Lenses Type'

    name = fields.Char('Name')


class Part(models.Model):
    _name = "spec.part.part"
    _rec_name = 'part_category_id'
    _description = 'Spectacle Part'

    part_category_id = fields.Many2one(
        'spec.part.category', string='Part Type Category')
    brand_id = fields.Many2one('spec.brand.brand', string='Brand', domain="[('brand_type', '=', 'frame')]")
    collection_ids = fields.Many2many('spec.collection.collection', 'part_collection_rel',
                                      'part_id', 'collection_id', string='Collection', copy=False)
    part_item_ids = fields.One2many(
        'spec.part.items', 'part_id', string='Part Items')

    @api.onchange('brand_id')
    def onchange_brand_id(self):
        """Onchange on brand id"""
        self.collection_ids = False


class PartItems(models.Model):
    _name = "spec.part.items"
    _description = 'Spectacle Part'

    name = fields.Char(string='Part Description')
    color_id = fields.Many2one('spec.color.family', string='Color')
    size = fields.Char(string='Size')
    price = fields.Float(string='Price')
    part_id = fields.Many2one('spec.part.part', string='Part')

    def name_get(self):
        result = []
        for part in self:
            color = part.color_id and part.color_id.name or ''
            size = part.size or ''
            name = part.name + ' ' + color + ' ' + size
            result.append((part.id, name))
        return result


class RimlessPart(models.Model):
    _name = "spec.rimless.part"
    _description = 'Rimless Default Parts'
    _rec_name = 'part_item_id'

    part_type_id = fields.Many2one('spec.part.part', string='Part Type')
    part_item_id = fields.Many2one('spec.part.items', string='Description')
    color_id = fields.Many2one(related='part_item_id.color_id', string='Color')
    size = fields.Char(related='part_item_id.size', string='Size')
    price = fields.Float(related='part_item_id.price', string='Price')
    frame_id = fields.Many2one('product.template', string='Frame')

    @api.onchange('part_type_id')
    def _onchange_part_type(self):
        self.part_item_id = False


class FrameMaterial(models.Model):
    _name = "spec.frame.material"
    _description = 'Frame Material'

    name = fields.Char(string='Frame Material Name')


class TempleMaterial(models.Model):
    _name = "spec.temple.material"
    _description = 'Temple Material'

    name = fields.Char(string='Temple Material Name')


class Shape(models.Model):
    _name = "spec.shape.shape"
    _description = 'Lens Shape'

    name = fields.Char(string='Shape')


class ColorFamily(models.Model):
    _name = "spec.color.family"
    _description = 'Color Family'

    name = fields.Char(string='Color Family')

class ColorCode(models.Model):
    _name = "spec.color.code.family"
    _description = 'Color Code Family'

    name = fields.Char(string='Color Code')

class GeoFit(models.Model):
    _name = "spec.geo.fit"
    _description = 'Geo Fit / Bridge'

    name = fields.Char(string='Geo Fit / Bride')


class HingeType(models.Model):
    _name = "spec.hinge.type"
    _description = 'Hinge Type'

    name = fields.Char(string='Hinge Type')


class EdgeType(models.Model):
    _name = "spec.edge.type"
    _description = 'Edge Type'

    name = fields.Char(string='Edge Type')


class FrameTag(models.Model):
    _name = "spec.frame.tag"
    _description = 'Frame Tag'

    name = fields.Char(string='Tags')


class PartTab(models.Model):
    _name = "spec.part.tab"
    _description = 'Part'

    part_type_id = fields.Many2one('spec.part.category', string='Part Type')
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    per_amt = fields.Selection([('percentage', 'Percentage'), (
        'amount', 'Amount')], default='amount', string='Percentage/Amount')
    frame_id = fields.Many2one('product.template', string='Frame')


class LensShapeCatelog(models.Model):
    _name = "spec.lens.shape.catalog"
    _description = 'Lens Shape Catalog'

    name = fields.Char(string='Lens Shape Name')
    brand_id = fields.Many2one('spec.brand.brand', string='Brand', domain="[('brand_type', '=', 'frame')]")
    collection_id = fields.Many2one(
        'spec.collection.collection', string='Collection')
    datas = fields.Binary(string="Import Trace File", attachment=True)
    datas_fname = fields.Char('File Name')
    a = fields.Float(string='A')
    b = fields.Float(string='B')
    ed = fields.Float(string='ED')
    ed_axis = fields.Float(string='ED Axis')
    demo_lens_base = fields.Float(string='Demo Lens Base')
    edge_id = fields.Many2one('spec.edge.type', string='Edge Type')


class BusinessType(models.Model):
    _name = "spec.business.type"
    _description = 'Business Type'
    name = fields.Char(string='Business Type')


# class ResUser(models.Model):
#     _inherit = "res.users"
#
#     business_type = fields.Char(string='Business Type')
#     collection_ids = fields.Many2many(
#         'spec.collection.collection', 'user_id', 'collection_id', string='Collection')


class GenderType(models.Model):
    _name = 'spec.gender.type'
    _description = 'Gender Type'

    name = fields.Char(string='Gender Type')


class FrameType(models.Model):
    _name = 'spec.frame.type'
    _description = 'Frame Type'

    vw_code = fields.Char(string='VW Code')
    name = fields.Char(string="Frame Type")
    frames_data = fields.Char(string='Frames Data')


class FrameManufacturer(models.Model):
    _name = 'spec.frame.manufacturer'
    _description = 'Frame Manufacturer'

    name = fields.Char(string='Manufacturer')
    mfmid = fields.Char(string='ManufacturerFramesMasterID',required=True)


class Frame(models.Model):
    _inherit = "product.template"

    def _compute_variant_on_hand(self):
        for res in self:
            res.variant_on_hand = int(sum(res.product_variant_ids.mapped('qty_available')))
    # name = fields.Char('Name', compute='_get_name', readonly=False,
    #                    index=True, translate=True, store=True)
    variant_on_hand = fields.Integer(string='On Hand', compute="_compute_variant_on_hand")
    model_number = fields.Char(string='Model Number')
    sfmid = fields.Char(string='Model Id (frames data)')
    brand_id = fields.Many2one(
        'spec.brand.brand', string='Brand', domain="[('brand_type', '=', 'frame')]")
    collection_id = fields.Many2one(
        'spec.collection.collection', string='Collection')
    discont_date = fields.Date(string='Discontinue Date')
    frames_data_last_sync = fields.Date(string='FramesData Last Sync')
    color_name = fields.Char(string='Color Name')
    color = fields.Char(string='Color #')
    frame_upc = fields.Char(string='Frame UPC')
    size = fields.Char(string='Size')
    bridge = fields.Char(string='Bridge')
    temple = fields.Char(string='Temple')
    fpc = fields.Char(string='FPC')
    tag_ids = fields.Many2many(
        'spec.frame.tag', 'spec_frame_tag_rel', 'frame_id', 'tag_id', string='Tags')
    sku_bar = fields.Char(string='SKU Bar')
    hsn_code = fields.Char(string='HSN Code')
    location_retail = fields.Float(string='Location Retail')
    min_allow_retail = fields.Float(string='Min Allowed Retail')
    suggested_retail = fields.Float(string='Suggested Retail')
    min_advertise_retail = fields.Float(string='Min Advertise Retail')
    listed_whole_sale = fields.Float(string='Listed Whole Sale')
    frame_material_id = fields.Many2one(
        'spec.temple.material', string='Front Material')
    temple_material_id = fields.Many2one(
        'spec.temple.material', string='Temple Material')
    shap_id = fields.Many2one('spec.shape.shape', string='Shape')
    color_family_id = fields.Many2one(
        'spec.color.family', string='Color Family')
    geo_fit_id = fields.Many2one('spec.geo.fit', string='Geo fit / Bridge')
    hinge_type_id = fields.Many2one('spec.hinge.type', string='Hinge Type')
    lens_color = fields.Char(string='Lens Color')
    discontinue = fields.Boolean(string='Discontinued')
    a = fields.Float(string='A')
    b = fields.Float(string='B')
    ed = fields.Float(string='ED')
    ed_axis = fields.Float(string='ED Axis')
    edge_id = fields.Many2one('spec.edge.type', string='Edge Type')
    dbl = fields.Float(string='DBL')
    wrap = fields.Float(string='Wrap')
    frame_lens_base = fields.Float(string='Frame Lens Base')
    datas = fields.Binary(string="Import Trace File", attachment=True)
    datas_fname = fields.Char('File Name')
    part_tab_ids = fields.One2many('spec.part.tab', 'frame_id', string='Part')
    rimless_part_ids = fields.One2many(
        'spec.rimless.part', 'frame_id', string='Rimless Parts')
    rimless_eye = fields.Boolean(string='Rimless Eyewear')
    lens_shape_catalog_id = fields.Many2one('spec.lens.shape.catalog', string='Default Lens Shape')
    is_part_image = fields.Boolean(string='Is Part Image')
    # gender_ids = fields.Many2many('spec.gender.type', 'frame_gender_rel', 'frame_id', 'gender_id', string='Gender Type')
    gender_ids = fields.Many2one('spec.gender.type', string='Gender Type')
    part_image = fields.Image("Part Image", attachment=True, max_width=1920, max_height=1920)
    spec_product_type = fields.Selection([('frame', 'Frames'),
                                          ('lens', 'lens'),
                                          ('contact_lens', 'Contact Lens'),
                                          ('accessory', 'Accessory'),
                                          ('service', 'Service'),
                                          ('lens_treatment', 'Lens Treatments'),
                                          ('lens_parameter', 'Lens Parameter')], string='Spec Product Type')
    """New Fields"""
    frame_manufacturer_id = fields.Many2one('spec.frame.manufacturer', string='Manufacturer')
    material_fix = fields.Selection([('carbon', 'Carbon'), ('memory_metals', 'Memory Metals'), ('metal', 'Metal'),
                                     ('nylon', 'Nylon'), ('other', 'Other'), ('plastic', 'Plastic'), ('rubber', 'Rubber'),
                                     ('tech_alloy', 'Tech Alloy'), ('titanium', 'Titanium'), ('wood', 'Wood')], string="Material")
    precious_metal = fields.Selection([('gold_filled', 'Gold – filled'), ('gold_other', 'Gold – other'),
                                       ('gold_plated', 'Gold – plated'), ('gold_solid', 'Gold – solid'),
                                       ('other', 'Other'), ('silver_other', 'Silver – other'),
                                       ('silver_plated', 'Silver - plated')], string="Precious Metal")
    shape = fields.Selection([('aviator', 'Aviator'), ('cat_eye', 'Cat Eye'), ('Frames_Shape', 'Chassis'),
                              ('geometric', 'Geometric'), ('modified_oval', 'Modified Oval'), ('modified_round', 'Modified Round'),
                              ('navigator', 'Navigator'), ('oval', 'Oval'), ('rectangle', 'Rectangle'),
                              ('round', 'Round'), ('shield', 'Shield'), ('square', 'Square')], string="Shape")
    gender = fields.Selection([('female', 'Female'), ('male', 'Male'), ('unisex', 'Unisex')], string="Gender")
    age = fields.Selection([('adult', 'Adult'), ('child', 'Child'), ('child_adult', 'Child & Adult'),
                            ('infant', 'Infant'), ('youth_teen', 'Youth/Teen')], string="Age")
    rim = fields.Selection([('piece_compression', '3-Piece Compression'), ('piece_screw', '3-Piece Screw'), ('full_rim', 'Full Rim'),
                            ('half_Rim', 'Half Rim'), ('inverted_half_Rim', 'Inverted Half Rim'), ('none', 'None'), ('other', 'Other'),
                            ('semi_rimless', 'Semi-Rimless'), ('shield', 'Shield')], string="Rim")
    frame_type = fields.Selection([('metal_edge', 'Metal Edge'), ('zyl_edge', 'Zyl Edge'), ('drilled_rimless', 'Drilled Rimless'),
                                   ('grooved_rimless', 'Grooved Rimless'), ('industrial_edge', 'Industrial Edge')], string="Frame Type")
    frame_type_id = fields.Many2one('spec.frame.type', string="Frame Type", ondelete='restrict')
    rx = fields.Selection([('other', 'Other'), ('prescription_available_adaptable.', 'Prescription available & Rx adaptable.'),
                           ('prescription_adaptable', 'Prescription available.'), ('rx_daptable.', 'Rx adaptable.')], string="Rx")
    # lenses = fields.Selection([('uv_protection', '100% UV protection'), ('acrylic', 'Acrylic'), ('cr_39', 'CR-39'), ('glass', 'Glass'),
    #                            ('mirrored', 'Mirrored'), ('other', 'Other'), ('photochromic', 'Photochromic'), ('polarized', 'Polarized'),
    #                            ('polycarbonate', 'Polycarbonate'), ('resin', 'Resin'), ('tempered', 'Tempered')], string="Lenses")
    lenses = fields.Many2one('spec.lenses.type', string="Lenses")
    edge_type = fields.Selection([('beveled', 'Beveled'), ('drill_mount', 'Drill-mount'), ('grooved', 'Grooved'), ('industrial', 'Industrial'),
                                  ('other', 'Other')], string="Edge Type")
    # edge_type_2 = fields.Many2one('spec.frame.type', string="Edge Type")
    hinge = fields.Selection([('hingeless', 'Hingeless'), ('micro_spring_hinge', 'Micro spring Hinge'), ('regular_hinge', 'Regular Hinge'),
                              ('screwless_hinge', 'Screwless Hinge'), ('spring_hinge', 'Spring Hinge')], string="Hinge")
    bridge_fix = fields.Selection([('adjustable_nose_pads', 'Adjustable nose pads'), ('double', 'Double'), ('keyhole', 'Keyhole'), ('other', 'Other'),
                                   ('saddle', 'Saddle'), ('single_Bridge', 'Single bridge'), ('unifit', 'Unifit'), ('universal', 'Universal')], string="Bridge")
    temple_fix = fields.Selection([('cable', 'Cable'), ('skull', 'Skull'), ('straight', 'Straight'), ('strap', 'Strap'), ('telescoping', 'Telescoping'),
                                   ('wraparound', 'Wraparound')], string="Temple")
    clip_on_option = fields.Selection([('available_sunglass.', 'Available as a Sunglass.'), ('clip_available', 'Clip-on Available'), ('clip_included', 'Clip-on included.'),
                                       ('magnetic_clip_available', 'Magnetic clip-on available.'), ('magnetic_clip_included', 'Magnetic clip-on included.'), ('other', 'Other')], string="Clip-On Option")
    side_shields = fields.Selection([('detachable', 'Detachable'), ('flat_fold', 'Flat fold'), ('other', 'Other'), ('permanent', 'Permanent')], string="Side Shields")
    case = fields.Selection([('box_available', 'Box available.'), ('box_included', 'Box included.'), ('case_available', 'Case available.'), ('case_included', 'Case included.'), ('hard_case_available', 'Hard case available.'),
                             ('hard_case_included', 'Hard case included.'), ('other', 'Other'), ('pouch_available', 'Pouch available.'), ('pouch_included', 'Pouch included.'), ('soft_case_available', 'Soft case available.'),
                             ('soft_base_included', 'Soft case included.')], string="Case")
    warranty = fields.Selection([('1_year_arranty', '1-year warranty.'), ('2_year_arranty', '2-year warranty.'), ('3_year_arranty', '3-year warranty.'), ('lifetime_year_arranty', 'Lifetime warranty on manufacturer’s defects'),
                                 ('12_year_arranty', 'Material defects or workmanship: 12 month warranty.'), ('24_year_arranty', 'Material defects or workmanship: 24 month warranty.'), ('other', 'Other'),
                                 ('unconditional_year_arranty', 'Unconditional lifetime warranty.')], string="Warranty")
    wholesale_cost = fields.Monetary(string="Wholesale Cost")
    material_frame_id = fields.Many2one(
        'spec.frame.material', string='Material')
    is_sunclass = fields.Boolean(string='Sunglasses')

    @api.model
    def default_get(self, vals):
        if self._context.get('default_prd_categ_name') and self._context.get('default_prd_categ_name') == 'Frames':
            self.categ_id = self.env.ref('opt_custom.product_category_frame').id
        return super(Frame, self).default_get(vals)

    @api.onchange('brand_id')
    def _onchange_branch(self):
        self.collection_id = False

    @api.onchange('discontinue')
    def _onchange_discontinue(self):
        if self.discontinue:
            self.discont_date = fields.Date.today()
        else:
            self.discont_date = False

    @api.onchange('model_number', 'collection_id')
    def _onchange_model_collection(self):
        name = ''
        if self.collection_id and self.collection_id.name:
            name += self.collection_id.name + ' '
        if self.model_number:
            name += self.model_number
        self.name = name

    @api.onchange('part_image', 'model_number')
    def onchange_image(self):
        for rec in self:
            if rec.part_image:
                frame_ids = self.search(
                    [('model_number', '=', rec.model_number)])
                if frame_ids:
                    for image in frame_ids:
                        image.part_image = rec.part_image
                else:
                    rec.part_image = None
            else:
                frame_image_id = self.search(
                    [('model_number', '=', rec.model_number), ('part_image', '!=', None)], limit=1)
                if frame_image_id:
                    rec.part_image = frame_image_id.part_image
