from odoo import api, fields, models, _
from datetime import datetime


class PromotionForm(models.Model):
    _name = 'promotion.form'
    _description = "Promotion"
    # _inherit = 'category.discount'
    _rec_name = 'promotion_name'


    promotion_name = fields.Char(string="Promo Name", required=True )
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date")
    code_entry = fields.Boolean(string="Code Entry Required")
    code_entry_box = fields.Text()
    promotion_type = fields.Selection([
        ('order_amount_discount', 'Order Amount Discount'),
        ('category_discount', 'Category Discount'),
        ('item_discount', 'Item Discount'),
        ('package_discount', 'Package Discount'),
        ('contact_lens_annual_supply', 'Contact Lens Annual Supply'),
        ('buy_x_get_y', 'Buy X, Get Y'),
        ], required=True)
    additional_notes = fields.Text(string='Notes')
    category_discount_id = fields.One2many('category.discount', 'promotion_form_id',string='Inventory Details', copy=True)
    order_amount_discount_id = fields.One2many('order.amount.discount', 'promotion_form_id', string='Total Order Amounts', copy=True)
    item_discount_id = fields.One2many('item.discount', 'promotion_form_id', string='Inventory Details', copy=True)
    package_discount_id = fields.One2many('package.discount', 'promotion_form_id', string='Inventory Details', copy=True)
    package_amount = fields.Float(string='Package Amount')
    allow_upgrade = fields.Boolean(string='Allow Upgrade')
    contact_lens_id = fields.One2many('contact.lens.annual.supply', 'promotion_form_id', string='Inventory Details', copy=True)
    buyx_gety_id = fields.One2many('buyx.gety', 'promotion_form_id', string='Inventory Details - BUY', copy=True)
    buyx_gety2_id = fields.One2many('buyx.gety', 'promotion_form_id2', string='Inventory Details - GET', relation='buyx_gety2', copy=True)