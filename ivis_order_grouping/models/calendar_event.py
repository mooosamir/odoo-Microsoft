# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = 'calendar.event'
    _description = "Appointment"

    @api.onchange('patient_id')
    def _compute_invoice_balance(self):
        for data in self:
            if data.patient_id.id:
                invoices = self.env['account.move'].search([('partner_id', 'in', data.patient_id.family_ids.ids), ('type', '=', 'out_invoice')])
                data.family_balance = sum([invoice.amount_residual for invoice in invoices])
                invoices = self.env['account.move'].search([('partner_id', '=', data.patient_id.id), ('type', '=', 'out_invoice')])
                data.patient_balance = sum([invoice.amount_residual for invoice in invoices])
            else:
                data.family_balance = 0.00
                data.patient_balance = 0.00

    family_balance = fields.Float(default=0.00, compute='_compute_invoice_balance')
    patient_balance = fields.Float(default=0.00, compute='_compute_invoice_balance')
