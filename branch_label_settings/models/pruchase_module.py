from odoo import api, fields, models, tools

READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
}

class PurchaseBillUnionLabel(models.Model):
    _inherit = 'purchase.bill.union'

    company_id = fields.Many2one('res.company', 'Branch', readonly=True)

class PurchaseReportLabel(models.Model):
    _inherit = "purchase.report"

    company_id = fields.Many2one('res.company', 'Branch', readonly=True)


class PurchaseOrderLabel(models.Model):
    _inherit = "purchase.order"

    company_id = fields.Many2one('res.company', 'Branch', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.company.id)


class PurchaseOrderLineLabel(models.Model):
    _inherit = 'purchase.order.line'

    company_id = fields.Many2one('res.company', related='order_id.company_id', string='Branch', store=True, readonly=True)



