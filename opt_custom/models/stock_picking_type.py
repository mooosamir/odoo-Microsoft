from odoo import api, fields, models, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def write(self, vals):
        if 'params' in self.env.context and 'model' in self.env.context['params'] and self.env.context['params']['model'] == 'res.config.settings':
            self = self.sudo()
        return super(StockPickingType, self).write(vals)
