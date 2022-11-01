# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import ustr


class ReportCMS1500New(models.AbstractModel):
    _name = 'report.opt_insurance.report_cms_1500_new'
    _description = 'report.opt_insurance.report_cms_1500_new'

    def __init__(self, cr, uid):
        super(ReportCMS1500New, self).__init__(cr, uid)
        self.claim_managers = False

    def _get_claim_data(self):
        line_datas = []
        claim_datas = []
        n = 6
        for claim in self.claim_managers:
            for line in claim.claim_line_ids:
                line_datas.append(line)
            final_datas = [line_datas[i * n:(i + 1) * n] for i in range((len(line_datas) + n - 1) // n )] 
            if len(final_datas) != 0:
                for datas in final_datas:
                    claim_datas.append({
                        'doc': claim,
                        'line': datas
                    })
            else:
                claim_datas.append({'doc': claim,
                                    'line': []})
        return claim_datas

    @api.model
    def _get_report_values(self, docids, data=None):
        claim_managers = self.env['claim.manager'].browse(docids)
        self.claim_managers = claim_managers 
        return {
            'doc_ids': docids,
            'doc_model': 'claim.manager',
            'docs': claim_managers,
            'report_type': data.get('report_type') if data else '',
            'get_claim_data': self._get_claim_data,

        }