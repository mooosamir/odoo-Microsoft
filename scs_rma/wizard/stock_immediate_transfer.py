# See LICENSE file for full copyright and licensing details.

from odoo import models


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        for rec in self:
            rma = rec.pick_ids.rma_id
            if not rma.rma_type == 'customer':
                if rec.pick_ids and rec.pick_ids.rma_id:
                    if rma.stock_picking_ids and rma.state == 'approve':
                        picking_done = []
                        for pick in rma.stock_picking_ids:
                            if pick.state == 'done':
                                picking_done.append(pick.id)
                        if len(picking_done) == len(
                                rma.stock_picking_ids.ids):
#                            rma.write({'state': 'close'})
                            if rma.rma_type == 'supplier':
                                rma.purchase_order_id.rma_done = True
                            else:
                                rma.picking_rma_id.rma_done = True

        return res
