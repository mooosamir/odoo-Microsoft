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


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'sale.order.wizard'

    sale_order_ids = fields.Many2many('sale.order')

    partner_id = fields.Many2one('res.partner', default=lambda self:self.env.user.partner_id)

    from_date = fields.Date(string='Date From')
    to_date = fields.Date(string='Date To', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company.id)
    post_sale_reason = fields.Many2one('post.sale.reasons', string="Post Sale Reason")
    is_post_sale_transaction_report = fields.Boolean()

    promotion_form_ids = fields.Many2many('promotion.form')
    is_promotions = fields.Boolean()

    discount_reason_ids = fields.Many2many('discount.reason')
    is_sales_order_discounts = fields.Boolean()

    is_patient_aged_receivables = fields.Boolean(string="Patient Aged Receivables")
    is_insurance_aged_receivables = fields.Boolean(string="Insurance Aged Receivables")
    is_aged_receivables = fields.Boolean(string="Insurance Aged Receivables")

    def print_report(self):
        domain = []
        if self.is_post_sale_transaction_report:
            domain = [('date_order', '<=', self.to_date), ('date_order', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id)]
            if self.post_sale_reason.id:
                domain.append(('post_sale_reasons_id', '=', self.post_sale_reason.id))
            else:
                domain.append(('post_sale_reasons_id', 'not in', [False]))
            self.sale_order_ids = self.env['sale.order'].search(domain)
            action = self.env.ref('opt_reports.report_action_post_sale_transactions_report').report_action(self)
        elif self.is_promotions:
            domain = [('date_order', '<=', self.to_date), ('date_order', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id), ('has_promotion_lines', '=', True)]
            if self.promotion_form_ids:
                domain.append(('order_line.promotion_id', 'in', self.promotion_form_ids.ids))
            self.sale_order_ids = self.env['sale.order'].search(domain)
            action = self.env.ref('opt_reports.report_action_promotions').report_action(self)
        elif self.is_sales_order_discounts:
            domain = [('date_order', '<=', self.to_date), ('date_order', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id), ('order_line.discount_reason', 'not in', [False])]
            if self.discount_reason_ids:
                domain.append(('order_line.discount_reason', 'in', self.discount_reason_ids.ids))
            self.sale_order_ids = self.env['sale.order'].search(domain)
            action = self.env.ref('opt_reports.report_action_sales_order_discounts').report_action(self)
        elif self.is_aged_receivables:
            domain = [('date_order', '<=', self.to_date),('company_id', '=', self.company_id.id)]
            self.sale_order_ids = self.env['sale.order'].search(domain)
            action = self.env.ref('opt_reports.report_action_aged_receivables').report_action(self)

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
