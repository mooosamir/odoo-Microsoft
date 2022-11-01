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


class SaleOrderLineWizard(models.TransientModel):
    _name = 'sale.order.line.wizard'
    _description = 'sale.order.line.wizard'

    sale_order_line_ids = fields.Many2many('sale.order.line')

    partner_id = fields.Many2one('res.partner', default=lambda self:self.env.user.partner_id)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company.id)
    from_date = fields.Date(string='Date From', required=True)
    to_date = fields.Date(string='Date To')
    product_type = fields.Selection([('frame', 'Frames'),
                                     ('lens', 'lens'),
                                     ('contact_lens', 'Contact Lens'),
                                     ('accessory', 'Accessory'),
                                     ('service', 'Service'),
                                     ('lens_treatment', 'Lens Treatments'),
                                     ('lens_parameter', 'Lens Parameter')], string='Product Type')
    categ_id = fields.Many2one('product.category')
    is_product_sales = fields.Boolean()

    hr_employee_id = fields.Many2many('hr.employee', string='Provider')
    is_physician_production = fields.Boolean()

    def print_report(self):
        domain = []
        if self.is_product_sales:
            domain = [('order_id.date_order', '<=', self.to_date), ('order_id.date_order', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id), ('categ_id', '!=', False)]
            if self.categ_id:
                domain.append(('categ_id', '=', self.categ_id.id))
            self.sale_order_line_ids = self.env['sale.order.line'].search(domain, order='categ_id')
            self.sale_order_line_ids = self.sale_order_line_ids.sorted('categ_id')
            action = self.env.ref('opt_reports.report_action_product_sales').report_action(self)
        elif self.is_physician_production:
            domain = [('order_id.date_order', '<=', self.to_date), ('order_id.date_order', '>=', self.from_date),
                      ('company_id', '=', self.company_id.id)]
            if self.hr_employee_id:
                domain.append(('lab_details_id.physician_id', 'in', self.hr_employee_id.ids))
            self.sale_order_line_ids = self.env['sale.order.line'].search(domain)
            action = self.env.ref('opt_reports.report_action_physician_production').report_action(self)

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
