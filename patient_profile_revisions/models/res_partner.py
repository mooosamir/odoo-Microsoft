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

from odoo.osv.expression import select_from_where
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from twilio.base.exceptions import TwilioRestException
from ...opt_custom import models as timestamp_UTC

_logger = logging.getLogger(__name__)


def lazy_name_get(self):
    names = tools.lazy(lambda: dict(self.dob_name_get()))
    return [(rid, tools.lazy(operator.getitem, names, rid)) for rid in self.ids]


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = "last_name"

    def _compute_patient_search(self):
        for res in self:
            res.patient_search_1 = "%s %s %s %s" % (res.first_name.lower() if res.first_name else '', res.last_name.lower(
            ) if res.last_name else '', res.date_of_birth.strftime('%m/%d/%Y') if res.date_of_birth else 'N/A', res.id),
            res.patient_search_2 = "%s %s %s" % (res.first_name.lower(
            ) if res.first_name else '', res.date_of_birth.strftime('%m/%d/%Y') if res.date_of_birth else 'N/A', res.id),

    patient_search_1 = fields.Char(compute='_compute_patient_search')
    patient_search_2 = fields.Char(compute='_compute_patient_search')
    display_name = fields.Char(
        compute='_compute_display_name', store=False, index=True)
    display_name1 = fields.Char(
        compute='_compute_display_name', store=False, index=True)

    @api.depends('debit', 'credit')
    def _balance(self):
        for data in self:
            data.balance = data.debit - data.credit

    @api.model
    def check_condition_show_dialog(self, record_id, data_changed):
        if record_id:
            current_record = self.search([('id', '=', record_id)])
            if current_record.first_name == data_changed['first_name'] and current_record.last_name == data_changed['last_name']:
                if current_record.date_of_birth:
                    if current_record.date_of_birth.strftime("%Y-%m-%d") == data_changed['date_of_birth']:
                        return False

        records = self.search_count([('first_name', '=', data_changed['first_name']), ('last_name', '=', data_changed['last_name']),
                                     ('date_of_birth', '=', data_changed['date_of_birth']), ("patient", "=", True), ("id", "!=", record_id)])
        if records > 0:
            return True
        else:
            return False

    def patients_list(self, record_id):
        form = self.env.ref('opt_custom.view_patent_profile_form', False)
        return {
            'name': _('Select Patient'),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'res_id': record_id,
            'view_mode': 'form',
            'target': 'current',
            'view_id': [(form and form.id)],
            'views': [(form and form.id, 'form')],
        }

    def dob_name_get(self):
        result = []
        name = "date_of_birth"
        dateformat = self.env['res.lang'].search(
            [('code', '=', self._context.get('lang'))], limit=1).date_format or '%Y/%m/%d'
        for record in self:
            if record.is_insurance or record.is_lab:
                result.append((record.id, "%s" % record.name))
            elif record.type == 'delivery':
                result.append((record.id, record.street))
            else:
                result.append((record.id, "%s (DOB: %s) (ID: %s)" % (
                    record.name, record[name].strftime(dateformat) if record[name] else 'N/A', record.id)))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name != '':
            # if name.rfind('/') != -1:
            #     name = '-'.join(name.split('/')[::-1])
            #     # if len(name.split('/')[-1]) == 4:
            # args += ['|', ('date_of_birth', operator, name), ('name', operator, name)]
            if self._context.get('default_patient', False):
                ids = self.search([]).filtered(lambda x: name.lower(
                ) in x.patient_search_1 or name.lower() in x.patient_search_2).ids
                args = [('id', 'in', ids)]
            else:
                if name.rfind('/') != -1:
                    args += ['&', ('date_of_birth', operator, name[name.rfind(' ') + 1:].replace(
                        '/', '-')), ('last_name', operator, name[:name.rfind(' ')])]
                # name = '-'.join(name.split('/')[::-1])
                    # if len(name.split('/')[-1]) == 4:
                elif name.rfind(' ') != -1:
                    args += ['&', ('first_name', operator, name[name.rfind(' ') + 1:]),
                             ('last_name', operator, name[:name.rfind(' ')])]
                else:
                    args += [('last_name', operator, name)]

        ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        recs = self.browse(ids)
        return lazy_name_get(recs.with_user(name_get_uid))

    def _get_name(self):
        name = super(ResPartner, self)._get_name()
        if self._context.get('name_dob'):
            name = "%s (DOB: %s) (ID: %s)" % (self.name, self.date_of_birth.strftime(
                '%Y/%m/%d') if self.date_of_birth else 'N/A', self.id)
        return name

    def name_get(self):
        result = []
        if self._context.get('name_dob'):
            for res in self:
                result.append((res.id, "%s (DOB: %s) (ID: %s)" % (res.name, res.date_of_birth.strftime(
                    '%Y/%m/%d') if res.date_of_birth else 'N/A', res.id)))
        elif self._context.get('name_id'):
            for res in self:
                result.append((res.id, "%s (ID: %s)" % (res.name, res.id)))
        else:
            result = super(ResPartner, self).name_get()
        return result

    @api.depends('is_company', 'name', 'parent_id.display_name', 'type', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None,
                    show_email=None, html_format=None, show_vat=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            if self._context.get('default_supplier_rank', False) and self.company_type == 'person':
                partner.display_name = (" " + partner.first_name if partner.first_name else '')\
                    + (" " + partner.middle_name if partner.middle_name else '')\
                    + (" " + partner.last_name if partner.last_name else '')\
                    + (", " + partner.commercial_company_name if partner.commercial_company_name else '')
            else:
                first_name = partner.first_name if partner.first_name else ''
                middle_name = partner.middle_name if partner.middle_name else ''
                last_name = partner.last_name if partner.last_name else ''
                partner.display_name = (first_name + ' ' + middle_name + ' ' + last_name) + '( ' + (
                    partner.gender if partner.gender else '') + ' ' + str(partner.date_of_birth if partner.date_of_birth else '') + ' )'
                partner.display_name1 = (
                    first_name + ' ' + middle_name + ' ' + last_name)
