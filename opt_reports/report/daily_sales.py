# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class ReportAppointment(models.AbstractModel):
    _name = 'report.opt_reports.daily_sales'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move.line.wizard'].browse(docids)

        return {
            'doc_ids': docids,
            'docs': docs,
            'o': docs[0] if len(docs) > 1 else docs,
            'doc_model': 'account.move.line.wizard',
            'report_type': data.get('report_type') if data else '',
            'currency_id': self.env['res.users'].browse(self._uid).company_id.currency_id,
            'datetime': datetime,
            'fields': fields,
            'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,
            'json':json,
        }
