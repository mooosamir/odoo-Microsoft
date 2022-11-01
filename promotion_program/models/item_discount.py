from odoo import api, fields, models, _



class ItemDiscount(models.Model):
    _name = 'item.discount'

    inventory_category = fields.Selection([
        ('frame__frame_manufacturer_id', 'Frame/Manufacturer'),
        ('frame__brand_id', 'Frame/Brand'),
        ('frame__collection_id', 'Frame/Collection'),
        ('frame__is_sunclass', 'Frame/Sunglasses'),
        ('lens__lens_type_id', 'Lens/Type'),
        ('lens__material_id', 'Lens/Material'),
        ('lens__filter_id', 'Lens/Filter'),
        ('lens__name', 'Lens/Name'),
        ('lens_treatment__name', 'Lens Treatment/Name'),
        ('lens_treatment__category_id', 'Lens Treatment/Category'),
        ('contact_lens__replacement_schedule_id', 'Contact Lens/Replacement Schedule'),
        ('contact_lens__name', 'Contact Lens/Name'),
        ('accessory__acc_category_id', 'Accessories/Category'),
        ('accessory__accessory_brand_id', 'Accessories/Brand'),
        ('accessory__accessory_header_name', 'Accessories/Name'),
        ('services__name', 'Services/Name'),
        ('services__ser_pro_code_id', 'Services/CPT'),
    ], string='Inventory Category', required=True)
    selection_frame_manufacturer = fields.Many2many('spec.frame.manufacturer',string='Selection')
    selection_frame_collection = fields.Many2many('spec.collection.collection', string='Selection')
    many2many_field_selection = fields.Many2many('product.template', string='Selection')
    many2many_brand_selection = fields.Many2many('spec.brand.brand', string='Selection')
    selection_lens_type = fields.Many2many('spec.lens.type',string='Selection')
    selection_lens_material = fields.Many2many('spec.lens.material', string='Selection')
    selection_lens_filter = fields.Many2many('spec.lens.filter', string='Selection')
    selection_lens_treatment_category = fields.Many2many('spec.lens.category', string='Selection')
    selection_contact_lens_replacement_schedule = fields.Many2many('spec.contact.lens.replacement.schedule', string='Selection')
    selection_accessories_category = fields.Many2many('spec.accessory.category', string='Selection')
    selection_services_cpt = fields.Many2many('spec.procedure.code', string='Selection')
    compute_selection = fields.Char(compute='compute_selection_field', string='Selection')
    quantity = fields.Integer(string='Qty')
    min_retail = fields.Char(string='Min Retail')
    max_retail = fields.Char(string='Max Retail')
    discount = fields.Integer(string='Discount')
    discount_type = fields.Selection([('amount', 'Amount'), ('percent', 'Percent')], string='Type')
    promotion_form_id = fields.Many2one('promotion.form', string='Inventory Details')

    @api.onchange('inventory_category')
    def on_change(self):
        if self.inventory_category == 'frame__is_sunclass':
            return {'domain':{'many2many_field_selection':[('is_sunclass','=',True)]}}
        elif self.inventory_category == 'lens__name':
            return {'domain': {'many2many_field_selection': [('prd_categ_name','=','Lens')]}}
        elif self.inventory_category == 'lens_treatment__name':
            return {'domain':{'many2many_field_selection':[('prd_categ_name','=','Lens Treatment')]}}
        elif self.inventory_category == 'contact_lens__name':
            return {'domain':{'many2many_field_selection':[('prd_categ_name','=','Contact Lens')]}}
        elif self.inventory_category == 'accessories__accessory_header_name':
            return {'domain':{'many2many_field_selection':[('prd_categ_name','=','Accessory')]}}
        elif self.inventory_category == 'services__name':
            return {'domain':{'many2many_field_selection':[(('prd_categ_name','=','Services'))]}}
        elif self.inventory_category == 'frame__brand_id':
            return {'domain':{'many2many_brand_selection':[(('brand_type','=','frame'))]}}
        elif self.inventory_category == 'accessory__accessory_brand_id':
            return {'domain':{'many2many_brand_selection':[(('brand_type','=','accessory'))]}}

    @api.depends('selection_frame_manufacturer','selection_frame_collection','many2many_field_selection',
                 'many2many_brand_selection','selection_lens_type','selection_lens_material',
                 'selection_lens_filter','selection_lens_treatment_category','selection_contact_lens_replacement_schedule',
                 'selection_accessories_category','selection_services_cpt')
    def compute_selection_field(self):
        for s in self:
            s.compute_selection = ""
            if s.selection_frame_manufacturer:
                for val in s.selection_frame_manufacturer:
                    s.compute_selection += val.name + ", "
            elif s.selection_frame_collection:
                for val in s.selection_frame_collection:
                    s.compute_selection += val.name + ", "
            elif s.many2many_field_selection:
                for val in s.many2many_field_selection:
                    s.compute_selection += val.name + ", "
            elif s.many2many_brand_selection:
                for val in s.many2many_brand_selection:
                    s.compute_selection += val.name + ", "
            elif s.selection_lens_type:
                for val in s.selection_lens_type:
                    s.compute_selection += val.name + ", "
            elif s.selection_lens_material:
                for val in s.selection_lens_material:
                    s.compute_selection += val.name + ", "
            elif s.selection_lens_filter:
                for val in s.selection_lens_filter:
                    s.compute_selection += val.name + ", "
            elif s.selection_lens_treatment_category:
                for val in s.selection_lens_treatment_category:
                    s.compute_selection += val.name + ", "
            elif s.selection_contact_lens_replacement_schedule:
                for val in s.selection_contact_lens_replacement_schedule:
                    s.compute_selection += val.name + ", "
            elif s.selection_accessories_category:
                for val in s.selection_accessories_category:
                    s.compute_selection += val.name + ", "
            elif s.selection_services_cpt:
                for val in s.selection_services_cpt:
                    s.compute_selection += val.name + ", "

            s.compute_selection = s.compute_selection[0:-2]


