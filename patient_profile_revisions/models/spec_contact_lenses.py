# -*- coding: utf-8 -*-

import os
import time
import pytz
import base64
import logging
import operator
from typing import re
from dateutil import tz
from twilio.rest import Client
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo import api, fields, models, tools, _
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from twilio.base.exceptions import TwilioRestException
from ...opt_custom import models as timestamp_UTC


class SpecContactLenses(models.Model):
    _inherit = 'spec.contact.lenses'
    # _order = "create_date DESC"

    provider_recommendation = fields.Char(compute='_provider_recommendation', string='Provider Recommendation')

    # def show_manufacturer_options_wizard(self, _id):
    #     form = self.env.ref('patient_profile_revisions.manufacturer_options_wizard_form', False)
    #     return {
    #         'name': _('Select Manufacturer Data'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'manufacturer.options.wizard',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'view_id': [(form and form.id)],
    #         'views': [(form and form.id, 'form')],
    #         'context': {
    #             'default_product_template_id': _id,
    #             'form_view_ref': 'patient_profile_revisions.manufacturer_options_wizard_form',
    #         }
    #     }

    @api.onchange('exam_date', 'rx')
    def _onchange_exam_date(self):
        if self.rx == 'glasses':
            self.expiration_date = self.exam_date + relativedelta(years=int(
                self.env['res.company'].search(
                    [('id', '=', self.partner_id.company_id.id)]).rx_expiration_contacts))
        else:
            self.expiration_date = self.exam_date + \
                                   relativedelta(years=int(self.env['res.company'].search(
                                       [('id', '=', self.partner_id.company_id.id)]).rx_expiration_lens))

    def rx_email_button(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()

        report_template_id = self.env.ref('patient_profile_revisions.action_prescription_report').render_qweb_pdf(
            self.id)
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Prescription Report",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)

        lang = self.env.context.get('lang')
        ctx = {
            'default_followers_show': False,
            'default_model': 'spec.contact.lenses',
            'default_res_id': self.ids[0],
            'default_partner_ids': self.partner_id.ids,
            'default_attachment_ids': [(6, 0, [data_id.id])],
            'defualt_email_from': self.env.user.email,
            'default_composition_mode': 'comment',
            'default_is_log ': True,
            'default_subject': "Prescription Report",
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def rx_report_button(self):
        # docs = self.env['res.partner'].browse(self.id)
        # spec_contact_lenses = self.env['spec.contact.lenses']
        # for data in self.contact_lens_ids:
        #     if data.check_box:
        #         spec_contact_lenses |= self.env['spec.contact.lenses'].browse(data.id)
        #         self.env['spec.contact.lenses'].browse(data.id).update({
        #             'check_box': False,
        #         })
        # args = {
        #     'data' : spec_contact_lenses,
        #     'doc_ids': self.ids,
        #     'doc_model': 'res.partner',
        #     'docs': self,
        # }

        # docs.contact_lens_ids = spec_contact_lenses
        # return self.env.ref('opt_custom.action_prescription_report').report_action(docs, data=args)
        return self.sudo().env.ref('patient_profile_revisions.action_prescription_report').report_action(self)

    def _provider_recommendation(self):
        for s in self:
            s.provider_recommendation = ""
            demo_list = []
            if s.gls_lens_style_id:
                s.provider_recommendation += s.gls_lens_style_id.name + ", "

            if s.gls_lens_material_id:
                s.provider_recommendation += s.gls_lens_material_id.name + ", "
            if s.gls_ar_coating:
                s.provider_recommendation += "AR Coating" + ", "
            if s.gls_photochromic:
                s.provider_recommendation += "Photochromic" + ", "
            if s.gls_polarized:
                s.provider_recommendation += "Polarized" + ", "
            if s.gls_tint:
                s.provider_recommendation += "Tint" + ", "

            s.provider_recommendation = s.provider_recommendation[0:-2]
