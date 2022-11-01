from odoo import api, fields, models, tools


class PosSaleReportLabel(models.Model):
    _inherit = "report.all.channels.sales"

    company_id = fields.Many2one('res.company', 'Branch', readonly=True)

class UtmCampaignLabel(models.Model):
    _inherit = 'utm.campaign'

    company_id = fields.Many2one('res.company', string='Branch', readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, default=lambda self: self.env.company)

class SaleOrderLabel(models.Model):
    _inherit = "sale.order"

    company_id = fields.Many2one('res.company', 'Branch', required=True, index=True, default=lambda self: self.env.company)


class SaleReportLabel(models.Model):
    _inherit = "sale.report"

    company_id = fields.Many2one('res.company', 'Branch', readonly=True)
