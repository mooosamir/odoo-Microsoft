from odoo import api, fields, models, _



class CategoryDiscount(models.Model):
    _name = 'category.discount'

    inventory_category = fields.Selection([
        ('frame', 'Frames'),
        ('lens', 'Lens'),
        ('lens_treatment', 'Lens Treatment'),
        ('contact_lens', 'Contact Lens'),
        ('accessory', 'Accessory'),
        ('service', 'Service'),
        ('all', 'All'),
    ], string='Inventory Category')

    quantity = fields.Integer(string='Qty')
    min_retail = fields.Char(string='Min Retail')
    max_retail = fields.Char(string='Max Retail')
    discount = fields.Integer(string='Discount')
    discount_type = fields.Selection([('amount','Amount'),('percent','Percent')],string='Type')
    promotion_form_id = fields.Many2one('promotion.form', string='Inventory Details')

