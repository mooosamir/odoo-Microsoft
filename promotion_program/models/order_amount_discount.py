from odoo import api, fields, models, _


class OrderAmountDiscounts(models.Model):
    _name = 'order.amount.discount'
    _description = 'order.amount.discount'

    min_amount = fields.Char(string='Min Amt')
    max_amount = fields.Char(string='Max Amt')
    discount = fields.Float(string='Discount')
    type = fields.Selection([('amount','Amount'),('percent','Percent')],string='Type')
    promotion_form_id = fields.Many2one('promotion.form', string='Inventory Details')