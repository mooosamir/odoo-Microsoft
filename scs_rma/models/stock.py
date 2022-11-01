# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    rma_id = fields.Many2one('rma.ret.mer.auth', string='RMA')
    rma_done = fields.Boolean("RMA is Done")


class StockMove(models.Model):
    _inherit = 'stock.move'

    rma_id = fields.Many2one('rma.ret.mer.auth', string='RMA')

class RmaProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        args = args or []
        context = self._context or {}
        if context.get('rma_product') and context.get('partner_id'):
            supplier_ids = self.env['product.supplierinfo'].search([('name','=',context.get('partner_id'))])
            product_list = supplier_ids.mapped('product_tmpl_id').ids
            if product_list:
               args.append(('product_tmpl_id', 'in', tuple(product_list)))
        return super(RmaProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
