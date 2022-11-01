# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    _description = 'stock return picking'

    def _post_sale_onchange_picking_id(self):
        move_dest_exists = False
        product_return_moves = [(5,)]
        if self.picking_id and self.picking_id.state != 'done':
            raise UserError(_("You may only return Done pickings."))
        # In case we want to set specific default values (e.g. 'to_refund'), we must fetch the
        # default values for creation.
        line_fields = [f for f in self.env['stock.return.picking.line']._fields.keys()]
        product_return_moves_data_tmpl = self.env['stock.return.picking.line'].default_get(line_fields)
        post_sale_orderlines = self.env.context.get('post_sale_orderlines', {})
        return_post_sale_orderlines = self.env['post.sale.transactions.lines']
        for move in self.picking_id.move_lines:
            if move.state == 'cancel':
                continue
            if move.scrapped:
                continue
            if move.move_dest_ids:
                move_dest_exists = True
            product_return_moves_data = dict(product_return_moves_data_tmpl)
            product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move(move))
            product_return_moves.append((0, 0, product_return_moves_data))
        new_product_return_moves = [(5,)]
        move_id = []
        for post_sale_orderline in post_sale_orderlines:
            product_return_mov = []
            uom_qty = post_sale_orderline.uom_qty / post_sale_orderline.account_move_line_id.quantity if post_sale_orderline.uom_qty and post_sale_orderline.account_move_line_id.quantity else 0
            for product_return_move in product_return_moves:
                 if len(product_return_move) > 1 and \
                     product_return_move[2]['product_id'] == post_sale_orderline.product_id.id \
                     and product_return_move[2]['quantity'] >= (post_sale_orderline.qty * uom_qty) \
                         and product_return_move[2]['move_id'] not in move_id:
                    product_return_mov.append(product_return_move)
            if len(product_return_mov):
                return_post_sale_orderlines += post_sale_orderline
                product_return_mov = product_return_mov[0]
                product_return_mov[2]['quantity'] = post_sale_orderline.return_qty * uom_qty
                move_id.append(product_return_mov[2]['move_id'])
                new_product_return_moves.append(product_return_mov)
            else:
                print("ERROR, POS Delivery RETURN")
        product_return_moves = new_product_return_moves
        if self.picking_id and not product_return_moves:
            raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)."))
        if self.picking_id:
            self.product_return_moves = product_return_moves
            self.move_dest_exists = move_dest_exists
            self.parent_location_id = self.picking_id.picking_type_id.warehouse_id and self.picking_id.picking_type_id.warehouse_id.view_location_id.id or self.picking_id.location_id.location_id.id
            self.original_location_id = self.picking_id.location_id.id
            # location_id = self.picking_id.location_id.id
            # if self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
            #     location_id = self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
            # self.location_id = location_id
        return return_post_sale_orderlines
