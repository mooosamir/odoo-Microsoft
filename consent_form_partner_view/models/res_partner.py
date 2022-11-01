# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def open_consent_form(self):
        tree = self.env.ref('acs_consent_form.view_acs_consent_form_tree_in_patient', False)
        return {
            'name': "Consent Forms",
            'type': 'ir.actions.act_window',
            'res_model': 'acs.consent.form',
            'view_mode': 'form',
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
            'views': [(tree and tree.id, 'tree'),(None, 'form')],
            'context': {'default_partner_id': self.id,
                        'default_user_id': self.user_ids[0].id if len(self.user_ids) else None}
        }
