# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class BalanceReporting(models.TransientModel):
    _name = 'balance.reporting.wizard'
    _description = 'post sale balance reporting'

    sale_order_id = fields.Many2one('sale.order', required=True)
    balance_reporting_line_wizard_id = fields.One2many("balance.reporting.line.wizard", "balance_reporting_wizard_id")

    @api.model
    def default_get(self, fields_list):
        if self.env.context['active_model'] == 'account.payment':
            account_payment_id = self.env[self.env.context['active_model']].browse(self.env.context['active_ids'])
            res = super(BalanceReporting, self).default_get(fields_list)
            if len(account_payment_id.invoice_ids.partner_id.ids) > 0:
                balance_reporting_line_wizard_ids = [(5, 0, 0)]
                for invoice in account_payment_id.invoice_ids:
                    sale_order_id = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit=1)
                    if invoice.partner_id.id == sale_order_id.partner_id.id:
                        balance_reporting_line_wizard_ids.append((0, 0, {
                            'display_type': 'line_section',
                            'name': invoice.name,
                            'currency_id': self.env.user.company_id.currency_id.id,
                            }))

                        for hcpcs_lines in invoice.line_ids.lab_details_id.hcpcs_id:
                            balance_reporting_line_wizard_ids.append((0, 0, {
                                'display_type': hcpcs_lines.display_type,
                                'name': hcpcs_lines.name,
                                'product_id': hcpcs_lines.product_id.id,
                                'hcpcs_code': hcpcs_lines.hcpcs_code.ids,
                                'hcpcs_modifier': hcpcs_lines.hcpcs_modifier.id,
                                # 'qty': order_line.pt_total - ((patient_invoices_total/pt_total) * order_line.pt_total) if patient_invoices_total > 0 and pt_total > 0 else order_line.pt_total,
                                'qty': hcpcs_lines.qty,
                                'pt_total': hcpcs_lines.pt_total,
                                'insurance': hcpcs_lines.insurance,
                                'allocation': (account_payment_id.amount/invoice.amount_total_signed) * hcpcs_lines.pt_total,
                                'currency_id': self.env.user.company_id.currency_id.id,
                            }))
                        if invoice.amount_tax != 0:
                            balance_reporting_line_wizard_ids.append((0, 0, {
                                'display_type': False,
                                'name': "Tax",
                                'product_id': False,
                                'hcpcs_code': False,
                                'hcpcs_modifier': False,
                                'qty': 1,
                                'pt_total': invoice.amount_tax,
                                'insurance': 0,
                                'allocation': (account_payment_id.amount/invoice.amount_total_signed) * invoice.amount_tax,
                                'currency_id': self.env.user.company_id.currency_id.id,
                            }))

                res['balance_reporting_line_wizard_id'] = balance_reporting_line_wizard_ids
        return res


class BalanceReportingLine(models.TransientModel):
    _name = 'balance.reporting.line.wizard'
    _description = 'post sale balance reporting lines'

    balance_reporting_wizard_id = fields.Many2one('balance.reporting.wizard', readonly=True)
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], default=False, help="Technical field for UX purpose.", readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    name = fields.Char('Name', readonly=True)
    product_id = fields.Many2one('product.product', readonly=True)
    hcpcs_code = fields.Many2many('spec.procedure.code',string='HCPCS Code')
    hcpcs_modifier = fields.Many2one('spec.lens.modifier',string='HCPCS Modifier', readonly=True)
    qty = fields.Float('QTY', default=1, readonly=True)
    pt_total = fields.Float('PT Total', readonly=True)
    insurance = fields.Float('Ins due', readonly=True)
    allocation = fields.Float(string="Allocation", readonly=True)
