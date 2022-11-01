# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        action = super(StockQuant, self)._get_quants_action(domain=domain, extend=extend)
        if self._context.get('default_prd_categ_name') == 'Frames':
            action.update({
                'view_mode': 'tree',
                'views': [
                    (self.env.ref('opt_custom.view_stock_quant_tree').id, 'list'),
                ],
            })
        return action
