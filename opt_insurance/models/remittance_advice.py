# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RemittanceAdvice(models.Model):
    _name = "remittance.advice"
    _description = 'Remittance Advice'
    _rec_name = 'sequence'

    sequence = fields.Char(string='Remittance Advice Number')
    remittance_date = fields.Date(string="Remittance Date")
    deposit_date = fields.Date(string="Deposit Date")
    insurance_company_id = fields.Many2one('res.partner', string="Insurance", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    Check_numbr = fields.Char(string='Check #')
    payment_method_id = fields.Many2one('account.journal', string='Payment Type', domain="[('insurance', '=', True)]")
    amount_paid = fields.Float(string='Paid')
    notes = fields.Text('Notes')
    payment_amount = fields.Float("Payment Amount")
    payment_allocated = fields.Float("Payment Allocated")
    total_chargeback = fields.Float("Total Chargeback")
    payment_remaining = fields.Float("Payment Remaining")
    state = fields.Selection([('new', 'New'),
                              ('in_progress', 'In Progress'),
                              ('completed', 'Completed')],
                                string="Status", default='new')
    claim_information_ids = fields.One2many('remittance.advice.line',
                                            'remittance_advice_id',
                                            string="Claim Information")
    currency_id = fields.Many2one('res.currency', string="currency", readonly=1,
    					default=lambda self: self.env.user.company_id.currency_id)

    @api.model
    def create(self, vals):
        if vals and not vals.get('sequence', False):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('remittance.advice')
        return super(RemittanceAdvice, self).create(vals)

    @api.onchange('insurance_company_id')
    def _onchange_insurance_company(self):
        self.claim_information_ids = False
        claim_info_list = []
        if self.insurance_company_id:
            claim_datas = self.env['claim.manager'].search([('primary_insurance_company_id', '=', self.insurance_company_id.id)])

            for claim in claim_datas:
                total_retail = total_discount = total_pt_resp = total_ins_receivable = total_amt_applied = 0.0
                claim_datas = self.env['claim.line'].search([('claim_manager_id', '=', claim.id)])
                for claim_line in claim_datas:
                    total_retail += claim_line.retail
                    total_pt_resp += claim_line.pt_resp
                    total_ins_receivable += claim_line.ins_receivable
                    total_amt_applied += claim_line.payments
                data_dict = {
                    'claim_id':claim.id,
                    'claim_status':claim.state,
                    'sale_order_id':claim.sale_order_id.id,
                    'service_date':claim.service_date,
                    'patient_id':claim.patient_id.id,
                    'insurance_company_id':claim.primary_insurance_company_id.id,
                    'retail':total_retail,
                    'discount':total_discount,
                    'pt_resp':total_pt_resp,
                    'ins_receivable':total_ins_receivable,
                    'amt_applied':total_amt_applied
                }

                claim_info_list.append((0, 0, data_dict))
            self.update({'claim_information_ids': claim_info_list})


class RemittanceAdviceLine(models.Model):
    _name = "remittance.advice.line"
    _description = 'Remittance Advice'
    _rec_name = 'claim_id'

    claim_id = fields.Many2one('claim.manager', string="Claim Number")
    claim_status = fields.Char(string='Claim Status')
    sale_order_id = fields.Many2one('sale.order', string="Order Number")
    service_date = fields.Date(string='Service Date')
    patient_id = fields.Many2one('res.partner', string="Patient", domain=[('patient', '=', True)])
    insurance_company_id = fields.Many2one('res.partner', string="Primary Insurance", domain="[('is_company','=',1), ('is_insurance','=',1)]")
    retail = fields.Float("Retail")
    discount = fields.Float("Discount")
    pt_resp = fields.Float("Pt Resp")
    ins_receivable = fields.Float("Ins Receivable")
    amt_applied = fields.Float("Amt Applied")
    remittance_advice_id = fields.Many2one('remittance.advice', string="Remittance Advice")
    currency_id = fields.Many2one('res.currency', string="currency", readonly=1,
                    default=lambda self: self.env.user.company_id.currency_id)
    remittance_advice_payment_ids = fields.One2many('remittance.advice.payment',
                                        'remittance_advice_id',
                                        string="Claim Information")
    total_ins_paid = fields.Float("Ins Paid")
    total_lab_chag = fields.Float("Lab Chag")
    total_net_ins_paid = fields.Float("Net Ins Paid")
    total_pt_resp = fields.Float("Pt Resp")
    total_transfer = fields.Float("Transfer")
    new_record = fields.Boolean("New Record")

    def action_payment_details(self):
        context = dict(self._context)
        context.update({'sale_order_id': self.sale_order_id,
                        'default_retail': self.retail,
                        'default_pt_resp': self.pt_resp,
                        'default_ins_receivable': self.ins_receivable})
        return {
        'name': _('Payments'),
        'view_mode': 'form',
        'res_model': 'remittance.advice.line',
        'type': 'ir.actions.act_window',
        'views': [(self.env.ref('opt_custom.remittance_advice_view_payments_form_view').id, 'form')],
        'context': context,
        'res_id': self.id,
        'target': 'fullscreen'
    }

    def btn_dummy(self):
        return True


class RemittanceAdvicePayment(models.Model):
    _name = "remittance.advice.payment"
    _description = 'Payments'
    _rec_name = 'pro_code_id'

    @api.depends('ins_receivable', 'ins_paid')
    def _compute_write_off(self):
        for rec in self:
            rec.write_off = rec.ins_receivable - rec.ins_paid

    @api.depends('write_off')
    def _compute_pt_resp_other(self):
        for rec in self:
            rec.pt_resp_other = rec.ins_receivable - rec.ins_paid - rec.write_off

    @api.depends('pt_resp_other')
    def _compute_transfer(self):
        for rec in self:
            rec.transfer = rec.ins_receivable - rec.ins_paid - rec.write_off - rec.pt_resp_other

    @api.depends('ins_paid')
    def _compute_bonus(self):
        for rec in self:
            value = 0.0
            context = dict(rec._context)
            if context.get('ins_paid'):
                value = context.get('ins_paid') - rec.ins_paid
            rec.bonus = value

    @api.depends('bonus')
    def _compute_covered_service_fee(self):
        for rec in self:
            value = 0.0
            context = dict(rec._context)
            if context.get('ins_paid'):
                value = context.get('ins_paid') - rec.ins_paid - rec.bonus
            rec.covered_service_fee = value

    @api.depends('covered_service_fee')
    def _compute_dispensing(self):
        for rec in self:
            value = 0.0
            context = dict(rec._context)
            if context.get('ins_paid'):
                value = context.get('ins_paid') - rec.ins_paid - rec.bonus - rec.covered_service_fee
            rec.dispensing = value

    pro_code_id = fields.Many2one('spec.procedure.code', string='CPT/HCPCS')
    retail = fields.Float(related='remittance_advice_id.retail', string="Retail")
    pt_resp = fields.Float(related='remittance_advice_id.pt_resp', string="Pt Resp")
    ins_receivable = fields.Float(related='remittance_advice_id.ins_receivable', string="Ins Receivable")
    ins_paid = fields.Float("Ins Paid")
    lab_chgs = fields.Float("Lab Chgs")
    write_off = fields.Float(compute='_compute_write_off', string="Write Off", store=True, readonly=False)
    pt_resp_other = fields.Float(compute='_compute_pt_resp_other' , string="Pt Resp", store=True, readonly=False)
    transfer = fields.Float(compute='_compute_transfer' , string="Transfer", store=True, readonly=False)
    patient_id = fields.Many2one('res.partner', string="Transfer to", domain=[('patient', '=', True)])
    currency_id = fields.Many2one('res.currency', string="currency", readonly=1,
                    default=lambda self: self.env.user.company_id.currency_id)
    remittance_advice_id = fields.Many2one('remittance.advice.line', string="Remittance Advice")
    bonus = fields.Float(compute='_compute_bonus', string="Bonus", store=True, readonly=False)
    covered_service_fee = fields.Float(compute='_compute_covered_service_fee', store=True, string="Covered Service Fee", readonly=False)
    dispensing = fields.Float(compute='_compute_dispensing', string="Dispensing", store=True, readonly=False)
    pt_selection = fields.Selection([('1', '1-Deductible'),
                                            ('2', '2-Coinsurance'),
                                            ('3', '3-Copay')], 'Pt Resp')
    note_ids = fields.One2many('remittance.advice.payment.notes',
                                        'payment_id',
                                        string="Notes")
    new_record = fields.Boolean("New Record")


    def btn_dummy(self):
        return True

    def action_add_notes(self):
        context = dict(self._context)
        context.update({'default_payment_id': self.id})
        return {
        'name': _('Notes'),
        'view_mode': 'form',
        'res_model': 'remittance.advice.payment',
        'type': 'ir.actions.act_window',
        'views': [(self.env.ref('opt_custom.remittance_advice_payment_notes_tree_views').id, 'form')],
        'context': context,
        'res_id': self.id,
        'target': 'new'
    }

    def action_open_add_amounts(self):
        context = dict(self._context)
        context.update({'create': False, 'form_view_initial_mode': 'edit', 'ins_paid':self.ins_paid})
        return {
        'name': _('Allocation'),
        'view_mode': 'form',
        'res_model': 'remittance.advice.payment',
        'type': 'ir.actions.act_window',
        'res_id': self.id,
        'views': [(self.env.ref('opt_custom.remittance_advice_payment_view_form_view').id, 'form')],
        'context': context,
        'target': 'new'
    }


class RemittancePaymentNotes(models.Model):
    _name = "remittance.advice.payment.notes"
    _description = 'Payments Notes'

    name = fields.Text('Notes')
    payment_id = fields.Many2one('remittance.advice.payment', string="payment")
