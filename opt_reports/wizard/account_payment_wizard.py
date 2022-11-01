# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta
from imp import reload
from odoo import tools
import logging
import sys

try:
    from num2words import num2words
except ImportError:
    logging.getLogger(__name__).warning(
        "The num2words python library is not installed, l10n_mx_edi features won't be fully available.")
    num2words = None


class AccountPaymentWizard(models.TransientModel):
    _name = 'account.payment.wizard'
    _description = 'account.payment.wizard'

    account_payment_ids = fields.Many2many('account.payment')

    partner_id = fields.Many2one('res.partner', default=lambda self:self.env.user.partner_id)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company.id)
    from_date = fields.Date(string='Date From', required=True)
    to_date = fields.Date(string='Date To')
    is_payment_transaction = fields.Boolean()

    is_payment_summary = fields.Boolean()

    def print_report(self):
        domain = []
        if self.is_payment_transaction:
            domain = [('payment_date', '<=', self.to_date), ('payment_date', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id)]
            self.account_payment_ids = self.env['account.payment'].search(domain, order='payment_type')
            action = self.env.ref('opt_reports.report_action_payment_transactions').report_action(self)
        elif self.is_payment_summary:
            domain = [('payment_date', '<=', self.to_date), ('payment_date', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id)]
            self.account_payment_ids = self.env['account.payment'].search(domain)
            action = self.env.ref('opt_reports.report_action_payment_summary').report_action(self)
        action.update({'close_on_report_download': True})
        return action

    def _get_street(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.street:
            address = "%s" % (partner.street)
        if partner.street2:
            address += ", %s" % (partner.street2)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False

    def _get_address_details(self, partner):
        self.ensure_one()
        res = {}
        address = ''
        if partner.city:
            address = "%s" % (partner.city)
        if partner.state_id.name:
            address += ", %s" % (partner.state_id.name)
        if partner.zip:
            address += ", %s" % (partner.zip)
        # if partner.country_id.name:
        #     address += ", %s" % (partner.country_id.name)
        reload(sys)
        html_text = str(tools.plaintext2html(address, container_tag=True))
        data = html_text.split('p>')
        if data:
            return data[1][:-2]
        return False
