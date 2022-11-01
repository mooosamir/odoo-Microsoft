from odoo import api, fields, models, _, exceptions
from odoo.exceptions import UserError
from collections import defaultdict

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}


class MultiInvoicePayment(models.TransientModel):
    _name = 'multi.invoice.payment'
    _description = 'Register Payment'

    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    reference_number = fields.Char(copy=False, help="Sale, Eyecare payment reference", string='Reference #')

    partner_id = fields.Many2one('res.partner', readonly=True)
    journal_id = fields.Many2one('account.journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    type = fields.Selection([
            ('sale', 'Sales'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ], related="journal_id.type")
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True,
                                        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"
                                        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"
                                        "Check: Pay bill by check and print it from Odoo.\n"
                                        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"
                                        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    invoice_ids = fields.Many2many('account.move', string="Invoices", copy=False, readonly=True)
    invoice_lines = fields.One2many('multi.invoice.lines', 'multi_invoice_payment_id')
    amount = fields.Float(default=0, string="Amount", readonly=True)
    so_change = fields.Float(default=0, readonly=True, string="Change")
    so_cash = fields.Float(default=0, string="Cash")
    reverse_invoice = fields.Boolean(default=0)

    @api.onchange('so_cash', 'invoice_lines')
    def _onchange_so_cash(self):
        so_cash = 0
        iteration = 0
        for invoice_line in self.invoice_lines.filtered(lambda x: x.fixed_amount > 0):
            iteration += 1
            so_cash += invoice_line.fixed_amount
        if len(self.invoice_lines) == iteration:
            self.so_cash = so_cash
        if len(self.invoice_lines) > 1:
            if so_cash > self.so_cash:
                self.so_cash = so_cash
        if self.reverse_invoice:
            self.so_change = (self.amount - self.so_cash)
        else:
            self.so_change = (self.amount - self.so_cash) * -1
        amount = 0
        for invoice_line in self.invoice_lines:
            if invoice_line.fixed_amount == 0:
                amount += invoice_line.balance

        total_so_cash = self.so_cash - so_cash
        for lines in self.invoice_lines:
            lines.update({
                'amount':(total_so_cash/amount) * lines.balance if lines.fixed_amount == 0 else lines.fixed_amount,
            })
        if self.so_change < 0:
            self.so_change = 0

    @api.model
    def default_get(self, fields):
        rec = super(MultiInvoicePayment, self).default_get(fields)
        active_ids = self._context.get('active_ids', False)
        invoice_id = self._context.get('invoice_id', False)
        # if not active_ids:
        #     return rec
        journal_id = self.env['account.journal']
        if 'journal_id' not in rec:
            journal_id = self.env['account.journal'].search([('company_id', '=', self.env.company.id), ('type', 'in', ['bank', 'cash'])], limit=1)
            rec['journal_id'] = journal_id.id
        if 'payment_method_id' not in rec:
            so = self.env['sale.order'].search([('id', '=', active_ids[0])])
            if self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', so.name)],limit=1).is_inbound() and invoice_id == 0:
                domain = [('payment_type', '=', 'inbound')]
            else:
                domain = [('payment_type', '=', 'outbound')]
            rec['payment_method_id'] = self.env['account.payment.method'].search(domain, limit=1).id
        account_move_ids = []
        invoice_lines = [(5, 0, 0)]
        amount = 0
        # if 'invoice_lines' in rec:
        #     invoice_lines = rec['invoice_lines']
        #     invoices = rec['invoices']
        if 'invoice_lines' in fields:
            if invoice_id != 0:
                inv = self.env['account.move'].search([('id', '=', invoice_id)])
                if inv.id:
                    so = self.env['sale.order'].search([('name', '=', inv.invoice_origin)], limit=1)
                    balance = self.env['account.payment']._compute_payment_amount(inv, inv.currency_id, journal_id,
                                                                                  self.payment_date)
                    if balance:
                        invoice_lines.append((0, 0, {
                            'invoice_id': inv.id,
                            'sale_order_id': so.id,
                            'partner_id': inv.partner_id.id,
                            'balance': balance * -1 if inv.is_outbound() else balance,
                            'amount': 0,
                        }))
                        amount += balance

                invoices = self.env['account.move'].browse(inv.id)
                rec['invoice_lines'] = invoice_lines
                rec['amount'] = amount * -1 if inv.is_outbound() else amount
                rec['so_cash'] = amount * -1 if inv.is_outbound() else amount
                rec['so_amount'] = amount * -1 if inv.is_outbound() else amount
                rec['partner_id'] = inv.partner_id.id
            else:
                # partner_id = set(self.env['sale.order'].browse(active_ids).mapped(lambda x: x.partner_id).ids)
                partner_id = max(self.env['sale.order'].browse(active_ids), key=lambda x:x['date_fo_birth']).partner_id
                # if len(set(self.env['sale.order'].browse(active_ids).mapped(lambda x: x.partner_id).ids)) > 1:
                #     raise exceptions.ValidationError("All selected sales order must have same partner.")
                for data in active_ids:
                    so = self.env['sale.order'].search([('id', '=', data)])
                    inv = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', so.name)],limit=1)
                    if inv.id:
                        balance = self.env['account.payment']._compute_payment_amount(inv, inv.currency_id, journal_id, self.payment_date)
                        if balance:
                            invoice_lines.append((0, 0, {
                                'invoice_id': inv.id,
                                'sale_order_id': so.id,
                                'partner_id': inv.partner_id.id,
                                'balance': balance,
                                'amount': 0,
                            }))
                            account_move_ids.append(inv.id)
                            amount += balance

                invoices = self.env['account.move'].browse(account_move_ids)
                rec['invoice_lines'] = invoice_lines
                rec['amount'] = amount
                rec['so_cash'] = amount
                rec['so_amount'] = amount
                rec['partner_id'] = partner_id.id
        else:
            if invoice_id != 0:
                inv = self.env['account.move'].search([('id', '=', invoice_id)])
            else:
                for data in active_ids:
                    so = self.env['sale.order'].search([('id', '=', data)])
                    inv = self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', so.name)],limit=1)
                    if inv.id:
                        balance = self.env['account.payment']._compute_payment_amount(inv, inv.currency_id, journal_id, self.payment_date)
                        account_move_ids.append(inv.id)

            invoices = self.env['account.move'].browse(account_move_ids)
        # Check all invoices are open
        # if any(invoice.state != 'posted' or invoice.invoice_payment_state != 'not_paid' or not invoice.is_invoice() for invoice in invoices):
        #     raise UserError(_("You can only register payments for open invoices"))

        if any(inv.company_id != invoices[0].company_id for inv in invoices):
            raise UserError(_("You can only register at the same time for payment that are all from the same company"))
        # Check the destination account is the same for each payment group
        if 'invoice_ids' not in rec:
            rec['invoice_ids'] = [(6, 0, invoices.ids)]
        return rec

    @api.onchange('journal_id', 'invoice_ids')
    def _onchange_journal(self):
        active_ids = self._context.get('active_ids', False)
        invoice_id = self._context.get('invoice_id', False)
        if invoice_id:
            invoices = self.env['account.move'].browse(invoice_id)
            # self.reverse_invoice = True
        else:
            so = self.env['sale.order'].search([('id', 'in', active_ids)])
            invoices = self.env['account.move']
            for data in so:
                invoices += self.env['account.move'].search([('type', '=', 'out_invoice'), ('invoice_origin', '=', data.name)])

            # invoices = self.env['account.move'].browse(active_ids)
        if self.journal_id and invoices:
            if invoices[0].is_inbound():
                domain_payment = [('payment_type', '=', 'inbound'), ('id', 'in', self.journal_id.inbound_payment_method_ids.ids)]
            else:
                domain_payment = [('payment_type', '=', 'outbound'), ('id', 'in', self.journal_id.outbound_payment_method_ids.ids)]
            domain_journal = [('type', 'in', ('bank', 'cash')), ('company_id', '=', invoices[0].company_id.id)]
            return {'domain': {'payment_method_id': domain_payment, 'journal_id': domain_journal}}
        return {}

    def _prepare_communication(self, invoices):
        '''Define the value for communication field
        Append all invoice's references together.
        '''
        return " ".join(i.invoice_payment_ref or i.ref or i.name for i in invoices)

    def _prepare_payment_vals(self, invoices, payment_transaction_id, payment_token_id):
        '''Create the payment values.

        :param invoices: The invoices/bills to pay. In case of multiple
            documents, they need to be grouped by partner, bank, journal and
            currency.
        :return: The payment values as a dictionary.
        '''
        amount = self.invoice_lines.filtered(lambda x:x.invoice_id.id == invoices.id).amount
        if invoices.is_outbound():
            amount = amount * -1
        # amount = self.env['account.payment']._compute_payment_amount(invoices, invoices[0].currency_id, self.journal_id, self.payment_date)
        values = {
            'sale_order_session_id': self.env['sale.order.session'].search([("state", 'in', ['in_progress'])]).id,
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self._prepare_communication(invoices),
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': ('inbound' if amount > 0 else 'outbound'),
            'amount': abs(amount),
            'currency_id': invoices[0].currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'partner_bank_account_id': invoices[0].invoice_partner_bank_id.id,
            'reference_number': self.reference_number,
        }
        if payment_transaction_id:
            values['journal_id'] = self.env['account.journal'].search([('name', '=', 'Stripe Backend')]).id
            values['payment_transaction_id'] = payment_transaction_id
            values['payment_token_id'] = payment_token_id
            values['payment_method_id'] = self.env['account.payment.method'].search([('name', '=', 'Electronic')]).id
        return values

    def create_payments(self, payment_transaction_id=False, payment_token_id=False):
        Payment = self.env['account.payment']
        for invoices in self.invoice_ids:
            payment_id = Payment.create(self._prepare_payment_vals(invoices, payment_transaction_id, payment_token_id))
            payment_id.post()
            if payment_transaction_id:
                self.env['payment.transaction'].browse(payment_transaction_id).update({
                    'payment_id': payment_id.id
                })

    # def create_payments_for_stripe(self, payment_transaction_id):
    #     Payment = self.env['account.payment']
    #     for invoices in self.invoice_ids:
    #         payments = Payment.create(self._prepare_payment_vals(invoices, payment_transaction_id))
    #         payments.post()

    def open_stripe_gateway(self):
        is_outbound = 0
        if len(self.invoice_ids.filtered(lambda x: x.is_outbound())) > 0:
            is_outbound = 1
            if self.so_cash > self.amount:
                raise exceptions.UserError("Specify an amount less then total amount")
            # raise exceptions.UserError("Can't use stripe for Customer Notes.")
        # else:
        if self.so_cash <= 0:
            raise exceptions.UserError("Specify an amount greater then 0")
        return {
            'type': 'ir.actions.client',
            'name': 'Stripe Checkout',
            'tag': 'stripe_checkout',
            'target': 'new',
            'context': {
                'multi_invoice_payment_id': self.id,
                'is_outbound': is_outbound,
            },
        }


class MultiInvoiceLines(models.TransientModel):
    _name = 'multi.invoice.lines'
    _description = 'Register Payment Lines'

    multi_invoice_payment_id = fields.Many2one('multi.invoice.payment')
    invoice_id = fields.Many2one('account.move', required=True)
    sale_order_id = fields.Many2one('sale.order', required=True)
    partner_id = fields.Many2one('res.partner', required=True)
    balance = fields.Float(default=0, string="Balance")
    amount = fields.Float(default=0, string="Amount")
    fixed_amount = fields.Float(default=0, string="Amount")

    # @api.onchange('fixed_amount')
    # def _onchange_amount(self):
    #     if self.fixed_amount < 0:
    #         raise exceptions.ValidationError("value can't be negative.")
    #     self.multi_invoice_payment_id._onchange_so_cash()
    #     for data in self:
    #         amount = 0
    #         for line in data.multi_invoice_payment_id.invoice_lines:
    #             amount += line.amount
    #         data.multi_invoice_payment_id.update({'so_cash': amount})

    @api.model
    def create(self, values):
        res = super(MultiInvoiceLines, self).create(values)
        return res

    def write(self, values):
        res= super(MultiInvoiceLines, self).write(values)
        return res
