from odoo import api, fields, models


class SaleCouponRule(models.Model):
    _inherit = 'sale.coupon.rule'
    _description = "Sales Coupon Rule"

    rule_products_domain = fields.Char(string="Based on Products", default='', help="On Purchase of selected product, reward will be given")


class SaleCouponReward(models.Model):
    _inherit = 'sale.coupon.reward'
    _description = "Sales Coupon Reward"

    discount_apply_on_new = fields.Selection(selection=[('on_order', 'On Order')], default="on_order", help="On Order - Discount on whole order")
    reward_type = fields.Selection(selection_add=[('package_price', 'Package Price'),
        ], string='Reward Type',
        help="Package Price - Package Price will be provided as discount.")

    @api.onchange('discount_apply_on_new')
    def _onchange_discount_apply_on_new(self):
        self.discount_apply_on = self.discount_apply_on_new
