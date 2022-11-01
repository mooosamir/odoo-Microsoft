from odoo import api, fields, models, _

class ProductReplenishLabel(models.TransientModel):
    _inherit = 'product.replenish'

    company_id = fields.Many2one('res.company', string='Branch')

class ReportStockQuantityLabel(models.Model):
    _inherit = 'report.stock.quantity'

    company_id = fields.Many2one('res.company', readonly=True, string='Branch')

class ReportStockForecatLabel(models.Model):
    _inherit = 'report.stock.forecast'

    company_id = fields.Many2one('res.company', string='Branch', readonly=True)


class StockScrapLabel(models.Model):
    _inherit = 'stock.scrap'

    company_id = fields.Many2one('res.company', string='Branch', default=lambda self: self.env.company, required=True, states={'done': [('readonly', True)]})

class StockRuleLabel(models.Model):
    _inherit = 'stock.rule'

    company_id = fields.Many2one('res.company', 'Branch',
                                 default=lambda self: self.env.company)

class QuantPackageLabel(models.Model):
    _inherit = "stock.quant.package"

    company_id = fields.Many2one(
        'res.company', 'Branch', compute='_compute_package_info',
        index=True, readonly=True, store=True)

class StockQuantLabel(models.Model):
    _inherit = 'stock.quant'

    company_id = fields.Many2one(related='location_id.company_id', string='Branch', store=True, readonly=True)

class ProductionLotLabel(models.Model):
    _inherit = 'stock.production.lot'

    company_id = fields.Many2one('res.company', 'Branch', required=True, stored=True, index=True)

class PickingLabel(models.Model):
    _inherit = "stock.picking"

    company_id = fields.Many2one(
        'res.company', string='Branch', related='picking_type_id.company_id',
        readonly=True, store=True, index=True)

class PickingTypeLabel(models.Model):
    _inherit = "stock.picking.type"

    company_id = fields.Many2one(
        'res.company', 'Branch', required=True,
        default=lambda s: s.env.company.id, index=True)

class StockPackageLevelLabel(models.Model):
    _inherit = 'stock.package_level'

    company_id = fields.Many2one('res.company', 'Branch', required=True, index=True)




