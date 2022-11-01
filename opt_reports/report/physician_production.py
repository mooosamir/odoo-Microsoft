# -*- coding: utf-8 -*-

import json
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class ReportAppointment(models.AbstractModel):
    _name = 'report.opt_reports.physician_production'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order.line.wizard'].browse(docids)
        length = len(docs.sale_order_line_ids.filtered(lambda x: x.lab_details_id.physician_id != False).mapped(
            'lab_details_id').mapped('physician_id')) - 1
        colors = self.get_colors_from_input("0x000000", "0xf70303", length)

        return {
            'doc_ids': docids,
            'docs': docs,
            'o': docs[0] if len(docs) > 1 else docs,
            'doc_model': 'appointment.report.wizard',
            'report_type': data.get('report_type') if data else '',
            'currency_id': self.env['res.users'].browse(self._uid).company_id.currency_id,
            'datetime': datetime,
            'fields': fields,
            'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,
            'json': json,
            'colors': colors,
            'len': len,
        }

    def get_colors_from_input(self, color1, color2, n):
        # Extract color coordinates
        r1, g1, b1 = [int(x, 16)
                      for x in [color1[i:i + 2] for i in range(2, 8, 2)]]
        r2, g2, b2 = [int(x, 16)
                      for x in [color2[i:i + 2] for i in range(2, 8, 2)]]

        # Build the coordinate-wise distribution
        # We could have used `range`, but using floats prevents some rounding errors
        dec_cols = zip(
            [int(r1 + x * (r2 - r1) / (n + 1)) for x in range(n + 2)],
            [int(g1 + x * (g2 - g1) / (n + 1)) for x in range(n + 2)],
            [int(b1 + x * (b2 - b1) / (n + 1)) for x in range(n + 2)])

        # Format back the coordinates to strings.
        # We used a small hack with `str.replace` to make sure coordinates have two digits
        return [''.join(hex(x).replace('x', '')[-2:]
                               for x in color) for color in dec_cols]
