from odoo import api, fields, models, _


class AccountTax(models.Model):
    _inherit = 'account.tax'

    test_field = fields.Text(string='Test Field')
    amount_type_copy = fields.Selection(string="Tax Computation", required=False,
                                   selection=[('group', 'Group of Taxes'),
                                              ('percent', 'Percentage of Price'),
                                              
                                              ],
                                   help="""
        - Group of Taxes: The tax is a set of sub taxes.
        - Fixed: The tax amount stays the same whatever the price.
        - Percentage of Price: The tax amount is a % of the price:
            e.g 100 * 10% = 110 (not price included)
            e.g 110 / (1 + 10%) = 100 (price included)
        - Percentage of Price Tax Included: The tax amount is a division of the price:
            e.g 180 / (1 - 10%) = 200 (not price included)
            e.g 200 * (1 - 10%) = 180 (price included)
            """)
    TYPE_TAX_USE = [
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('sale_and_purchase','Sales & Purchases'),
        ('none', 'None'),
    ]
    type_tax_use = fields.Selection(TYPE_TAX_USE, string='Tax Scope', required=True, default="sale",
                                    help="Determines where the tax is selectable. Note : 'None' means a tax can't be used by itself, however it can still be used in a group. 'adjustment' is used to perform tax adjustment.")
    # taxes_id = fields.Many2one('account.tax', string="")
    # group_of_taxes_id = fields.One2many('account.tax','taxes_id',string='')


    @api.onchange('amount_type_copy')
    def onchangeAmountType(self):
        self.amount_type = self.amount_type_copy

    @api.onchange('amount_type_copy', 'type_tax_use')
    def _onchange_computation(self):
        resObj = self.env['account.tax'].search([('amount_type_copy', '=', 'percent'),('active','=',True),('type_tax_use','=',self.type_tax_use)])

        ml = [(5,0,0)]
        for r in resObj:
            print(r)
            ml.append((4,r.id))

        self.children_tax_ids = ml

    # @api.onchange('type_tax_use')
    # def _onchange_scope(self):
    #     resObj = self.env['account.tax'].search(
    #         [('amount_type_copy', '=', 'percent'), ('active', '=', True), ('type_tax_use', '=', self.type_tax_use)])
    #
    #     ml = []
    #     for r in resObj:
    #         print(r)
    #         ml.append((4, r.id))
    #
    #     self.children_tax_ids = ml
    #
