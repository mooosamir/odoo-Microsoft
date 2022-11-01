from odoo import api, fields, models, tools, _, SUPERUSER_ID


class ProductTemplateLabel(models.Model):
    _inherit = "product.template"

    company_id = fields.Many2one(
        'res.company', 'Company', index=1)

class SupplierInfoLabel(models.Model):
    _inherit = "product.supplierinfo"

    company_id = fields.Many2one(
        'res.company', 'Branch',
        default=lambda self: self.env.company.id, index=1)

class ProductPackagingLabel(models.Model):
    _inherit = "product.packaging"

    company_id = fields.Many2one('res.company', 'Branch', index=True)

class PricelistItemLabel(models.Model):
    _inherit = "product.pricelist.item"

    company_id = fields.Many2one(
        'res.company', 'Branch',
        readonly=True, related='pricelist_id.company_id', store=True)


class Pricelistlabel(models.Model):
    _inherit = "product.pricelist"

    company_id = fields.Many2one('res.company', 'Branch')