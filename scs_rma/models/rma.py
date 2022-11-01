# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RMARetMerAuth(models.Model):
    """Data model for RMARetMerAuth."""

    _name = 'rma.ret.mer.auth'
    _description = "Return Merchandise Authorization"

    @api.depends('rma_sale_lines_ids.refund_price')
    def _amount_all(self):
        """Compute the total amounts of the SO."""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.rma_sale_lines_ids:
                amount_untaxed += line.refund_price
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('rma_purchase_lines_ids.refund_price')
    def _purchase_amount_all(self):
        """Compute the total amounts of the PO."""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.rma_purchase_lines_ids:
                amount_untaxed += line.refund_price
                amount_tax += line.price_tax
            order.update({
                'purchase_amount_untaxed': amount_untaxed,
                'purchase_amount_tax': amount_tax,
                'purchase_amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('rma_picking_lines_ids')
    def _picking_amount_all(self):
        """Compute the total amounts of the PO."""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.rma_picking_lines_ids:
                amount_untaxed += line.refund_price
                amount_tax += line.price_tax
            order.update({
                'picking_amount_untaxed': amount_untaxed,
                'picking_amount_tax': amount_tax,
                'picking_amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('stock_picking_ids')
    def _count_picking_ids(self):
        """ Compute total count of pickings """
        for rma in self:
            if rma.stock_picking_ids:
                rma.pick_count = len(rma.stock_picking_ids.ids)
            else:
                rma.pick_count = 0

    @api.depends('invoice_ids')
    def _count_invoice_ids(self):
        """ Compute total count of invoices """
        for rma in self:
            if rma.invoice_ids:
                rma.inv_count = len(rma.invoice_ids.ids)
            else:
                rma.inv_count = 0

    def _get_company(self):
        return self.env.user.company_id

    name = fields.Char('RMA No', readonly=True, default='New RMA')
    rma_type = fields.Selection(
        [('customer', 'Sale Order'), ('supplier', 'Purchase Order'),
         ('picking', 'Picking'), ('lot', 'Serial No')],
        default='supplier')
    problem = fields.Text('Notes')
    rma_date = fields.Date('RMA Date', help='Date')
    vendor_rma = fields.Char(string="Vendor RMA #")
    date = fields.Date('Date', default=fields.Date.context_today, help='Date')
    shipping_method_id = fields.Many2one("delivery.carrier", string="Shipping Method")
    shipping_date = fields.Date('Date', help='Shipping Date')
    tracking_number = fields.Char(string="Tracking Number")
    partner_id = fields.Many2one('res.partner', 'Customer')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    assign_owner_id = fields.Many2one('res.partner', 'Assign Owner')
    picking_partner_id = fields.Many2one('res.partner', 'Partner')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order',
                                    copy=False)
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order',
                                        copy=False)
    picking_rma_id = fields.Many2one('stock.picking', 'Picking',
                                     copy=False, editable=False,
                                     )
    rma_lot = fields.Char("Serial No", copy=False)
    rma_sale_lines_ids = fields.One2many('rma.sale.lines', 'rma_id',
                                         string='Order Lines', states={
                                             'resolved': [('readonly', True)],
                                             'close': [('readonly', True)],
                                             'approve': [('readonly', True)],
                                         }, copy=False)
    rma_purchase_lines_ids = fields.One2many('rma.purchase.lines', 'rma_id',
                                             string='Purchase Order Lines',
                                             states={
                                                 'resolved': [
                                                     ('readonly', True)],
                                                 'close': [('readonly', True)],
                                                 'approve': [
                                                     ('readonly', True)],
                                             }, copy=False)
    rma_picking_lines_ids = fields.One2many('rma.picking.lines', 'rma_id',
                                            string='Picking Lines',
                                            states={
                                                'resolved': [
                                                    ('readonly', True)],
                                                'close': [('readonly', True)],
                                                'approve': [
                                                    ('readonly', True)],
                                            }, copy=False)
    stock_picking_ids = fields.One2many('stock.picking', 'rma_id',
                                        string='Stock Pickings', copy=False)
    invoice_ids = fields.One2many('account.move', 'rma_id', string='Invoices',
                                  copy=False)
    pick_count = fields.Integer(string='Pickings Count', compute='_count_picking_ids')
    inv_count = fields.Integer(string='Invoice Count', compute='_count_invoice_ids')
    state = fields.Selection([('new', 'New'),
                              ('verification', 'Waiting for RA'),
                              ('resolved', 'Waiting For Delivery'),
                              ('approve', 'Approved'),
                              ('shipped', 'Shipped'),
                              ('close', 'Done')
                              ], string='Status', default='new')
    type = fields.Selection([('return', 'Return'), ('exchange', 'Exchange')],
                            string='Actions')
    amount_untaxed = fields.Float(string='Untaxed Amount', store=True,
                                  readonly=True, compute='_amount_all')
    amount_tax = fields.Float(string='Taxes', store=True, readonly=True,
                              compute='_amount_all')
    amount_total = fields.Float(string='Total', store=True, readonly=True,
                                compute='_amount_all')
    purchase_amount_untaxed = fields.Float(string='Untaxed Amount',
                                           store=True,
                                           readonly=True,
                                           compute='_purchase_amount_all')
    purchase_amount_tax = fields.Float(string='Taxes',
                                       store=True, readonly=True,
                                       compute='_purchase_amount_all')
    purchase_amount_total = fields.Float(string='Total', store=True,
                                         readonly=True,
                                         compute='_purchase_amount_all')
    picking_amount_untaxed = fields.Float(string='Untaxed Amount',
                                          store=True,
                                          compute='_picking_amount_all')
    picking_amount_tax = fields.Float(string='Taxes',
                                      store=True,
                                      compute='_picking_amount_all')
    picking_amount_total = fields.Float(string='Total', store=True,
                                        compute='_picking_amount_all')
    pick_origin = fields.Char(
        string="Previous RMA",
        related='picking_rma_id.origin', readonly=True)

    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        related='company_id.currency_id',
        required=False)
    company_id = fields.Many2one(
        'res.company', string='Company', default=_get_company)
    invoice_status = fields.Selection([('pending', 'Pending'),
                                       ('paid', 'Paid')],
                                      string='Invoice Status',
                                      default='pending')
    lot_picking_id = fields.Many2one('stock.picking', "Lot Picking")
    notes = fields.Text('Notes')

    def rma_submit(self):
        """Set state to verification."""
        if self.rma_type == 'lot':
            if not self.lot_picking_id:
                raise ValidationError(_(
                    'You can not submit blank RMA.'))
        self.write({'state': 'verification'})
        return True

    @api.model
    def create(self, vals):
        """ Create Sequence for RMA """
        sequence_val = self.env['ir.sequence'].next_by_code('rma.rma') or '/'
        vals.update({'name': sequence_val})
        res = super(RMARetMerAuth, self).create(vals)
        if not res.vendor_rma:
            res.rma_submit()
        if res.vendor_rma:
            if not res.rma_purchase_lines_ids:
                raise ValidationError(_('Please Add Product Details.'))
            res.create_receive_picking()
        if res.shipping_date:
            if res.state != 'approve':
                raise ValidationError(_('Please Add Vendor RMA Details.'))
            res.write({'state': 'shipped'})
        return res

    def write(self, vals):
        res = super(RMARetMerAuth, self).write(vals)
        if vals.get('vendor_rma'):
            if not self.rma_purchase_lines_ids:
                raise ValidationError(_('Please Add Product Details.'))
            self.create_receive_picking()
        if vals.get('shipping_date'):
            if self.state != 'approve':
                raise ValidationError(_('Please Add Vendor RMA Details.'))
            self.write({'state': 'shipped'})
        return res

    def rma_close(self):
        """ Set state to Close. if all Pickings are done """
        for rec in self:
            picking = rec.stock_picking_ids.filtered(
                lambda pick: pick.state not in ['done', 'cancel'])
            if picking:
                raise ValidationError(_(
                    'Please Validate Your All Pickings First.'))
            rec.write({'state': 'close'})
            if rec.rma_type == 'customer':
                rma_ids = self.env['rma.ret.mer.auth'].search([
                    ('sale_order_id', '=', rec.sale_order_id.id),
                ])
                # Check if Sale Order is Fully Returned or Not
                # Prepare all RMA product with return qty
                rma_product_list = {}
                for rma in rma_ids:
                    for line in rma.rma_sale_lines_ids:
                        if rma_product_list.get(line.product_id.id):
                            rma_product_list[line.product_id.id] += line.refund_qty
                        else:
                            rma_product_list[line.product_id.id] = line.refund_qty
                # Prepare all SO product with Delivered qty
                so_product_list = {}
                for so_line in rma.sale_order_id.order_line:
                    if so_product_list.get(so_line.product_id.id):
                        so_product_list[so_line.product_id.id] += so_line.qty_delivered
                    else:
                        so_product_list[so_line.product_id.id] = so_line.qty_delivered
                # Check if RMA's product return qty is equal to sale order delivered
                flag = False
                for product, qty in rma_product_list.items():
                    if so_product_list.get(product) != qty:
                        flag = True
                        break
                if not flag:
                    rec.sale_order_id.rma_done = True
            rec.write({'state': 'close'})

    def rma_approve(self):
        """Set state to approve."""
        for rec in self:
            rec.write({'state': 'approve'})

    def rma_set_draft(self):
        """Set state to New."""
        for rec in self:
            for pick in rec.stock_picking_ids:
                if pick.state == 'done':
                    raise ValidationError(_(
                        'You can not set to draft as picking is already done.'))
            for inv in rec.invoice_ids:
                if inv.state == 'posted':
                    raise ValidationError(_(
                        'You can not set to draft as Invoice is already posted.'))
            rec.write({'state': 'new'})

    def check_serial(self):
        """Fetch data from serial no."""
        for rec in self:
            lot_no = self.env['stock.production.lot'].search(
                [('name', '=', rec.rma_lot)])
            move_line = self.env['stock.move.line'].search(
                [('lot_id', '=', lot_no[0].id)])[0]
            pick_id = move_line.move_id.picking_id
            if not lot_no or not pick_id:
                raise ValidationError(
                    _("No picking found for this Serial No."))
            if len(lot_no) > 1:
                raise ValidationError(
                    _("Two products found for this Serial No.\
                     Serial No. should be unique per product."))
            rec.lot_picking_id = pick_id.id
            rec.onchange_lot_picking_id()

    def create_receive_picking(self):
        """
        Create Receive picking for RMA Customer and set RMA state to.
        resolved. Create refund invoices for return type RMA.
        """
        for rma in self:
            # When Type is customer then it will create Incoming Picking
            if rma.rma_type == 'customer':
                state = 'resolved'
                exchange_move_vals = []
                stock_moves_vals = []
                invoice_line_vals = []
                exchange_inv_line_vals = []
                for rma_line in rma.rma_sale_lines_ids:
                    state = 'approve'
                    # Prepare Stock Move Vals
                    rma_move_vals_b2b = {
                        'product_id': rma_line.product_id and
                        rma_line.product_id.id or False,
                        'name': rma_line.product_id and
                        rma_line.product_id.name or False,
                        'origin': rma.name,
                        'product_uom_qty': rma_line.refund_qty or 0,
                        'location_id': rma_line.source_location_id.id or False,
                        'location_dest_id':
                        rma_line.destination_location_id.id or
                        False,
                        'product_uom': rma_line.product_id.uom_id and
                        rma_line.product_id.uom_id.id or False,
                        'rma_id': rma.id,
                        'group_id': rma.sale_order_id.procurement_group_id.id,
                        'price_unit': rma_line.price_subtotal or 0,
                    }
                    stock_moves_vals.append((0, 0, rma_move_vals_b2b))
                    inv_account_id = rma_line.product_id. \
                        property_account_income_id and \
                        rma_line.product_id. \
                        property_account_income_id.id or \
                        rma_line.product_id.categ_id. \
                        property_account_income_categ_id and \
                        rma_line.product_id.categ_id. \
                        property_account_income_categ_id.id or False
                    if not inv_account_id:
                        raise ValidationError((
                            'No account defined for product "%s".') %
                            rma_line.product_id.name)
                    prod_price = 0.0
                    if rma_line.refund_qty != 0:
                        prod_price = float(
                            (rma_line.refund_price) / float(
                                rma_line.refund_qty))
                    # Prepare Invoice Line Vals
                    inv_line_values = {
                        'product_id': rma_line.product_id and rma_line.
                        product_id.id or False,
                        'account_id': inv_account_id or False,
                        'name': rma_line.product_id and rma_line.
                        product_id.name or False,
                        'quantity': rma_line.refund_qty or 0,
                        'price_unit': prod_price or 0,
                        'currency_id': rma.currency_id.id or False,
                    }

                    if rma_line.tax_id and rma_line.tax_id.ids:
                        inv_line_values.update(
                            {'tax_ids': [(6, 0, rma_line.
                                          tax_id.ids)]})

                    invoice_line_vals.append((0, 0, inv_line_values))
                    # Check if it is exchange
                    if rma_line.type == 'exchange':
                        state = 'approve'
                        # Prepare move for exchange product
                        rma_move_vals_b2c = {
                            'product_id': rma_line.exchange_product_id and
                            rma_line.exchange_product_id.id or False,
                            'name': rma_line.exchange_product_id and
                            rma_line.exchange_product_id.name or False,
                            'origin': rma.name,
                            'product_uom_qty': rma_line.refund_qty or 0,
                            'location_id':
                            rma_line.source_location_id.id or
                            False,
                            'location_dest_id':
                            rma_line.destination_location_id.id or
                            False,
                            'product_uom':
                            rma_line.exchange_product_id.uom_id and
                            rma_line.exchange_product_id.uom_id.id or False,
                            'rma_id': rma.id,
                            'group_id':
                            rma.sale_order_id.procurement_group_id.id,
                            'price_unit': rma_line.price_subtotal or 0,
                        }
                        exchange_move_vals.append((0, 0, rma_move_vals_b2c))
                        # SO : Prepare Invoice Line for Exchange Product
                        inv_line_vals_exchange = {
                            'product_id': rma_line.exchange_product_id and
                            rma_line.exchange_product_id.id or False,
                            'account_id': inv_account_id or False,
                            'name': rma_line.exchange_product_id and rma_line.
                            exchange_product_id.name or False,
                            'quantity': rma_line.refund_qty or 0,
                            'price_unit':
                            rma_line.exchange_product_id.lst_price or 0,
                            'currency_id': rma.currency_id.id or False,
                        }

                        if rma_line.tax_id and rma_line.tax_id.ids:
                            inv_line_vals_exchange.update(
                                {'tax_ids': [(6, 0, rma_line.
                                              tax_id.ids)]})

                        exchange_inv_line_vals.append(
                            (0, 0, inv_line_vals_exchange))
                # Create Picking or Update move lines in existing pickings
                for move in stock_moves_vals:
                    picking = self.env['stock.picking'].search([
                        ('rma_id', '=', rma.id),
                        ('location_id', '=', move[2]['location_id']),
                        ('location_dest_id', '=',
                         move[2]['location_dest_id'])])
                    # If no picking found then create one
                    if not picking:
                        picking_type_id = self.env[
                            'stock.picking.type'].search([
                                ('code', '=', 'incoming'),
                                ('warehouse_id.company_id', 'in',
                                 [self.env.context.get(
                                     'company_id',
                                     self.env.user.company_id.id),
                                  False])],
                            limit=1).id
                        picking_vals = {
                            'move_type': 'one',
                            'picking_type_id': picking_type_id or False,
                            'partner_id': rma.partner_id and
                            rma.partner_id.id or
                            False,
                            'origin': rma.name,
                            'move_lines': [move],
                            'location_id': move[2]['location_id'],
                            'location_dest_id': move[2]['location_dest_id'],
                            'rma_id': rma.id,
                        }
                        picking_rec = self.env[
                            'stock.picking'].create(picking_vals)
                        picking_rec.action_confirm()
                        picking_rec.action_assign()

                    else:
                        # If picking is already exists then create its moves
                        move[2]['picking_id'] = picking.id
                        self.env['stock.move'].create(move[2])
                # Check picking for exchange product
                for vals in exchange_move_vals:
                    ex_picking = self.env['stock.picking'].search([
                        ('rma_id', '=', rma.id),
                        ('location_id', '=', vals[2]['location_id']),
                        ('location_dest_id', '=', vals[2]['location_dest_id']),
                        ('picking_type_code', '=', 'outgoing')])
                    if not ex_picking:
                        picking_type = self.env['stock.picking.type'].search([
                            ('code', '=', 'outgoing'),
                            ('warehouse_id.company_id', 'in',
                             [self.env.context.get('company_id',
                                                   self.env.user.company_id.id
                                                   ),
                              False])],
                            limit=1).id
                        exchange_picking_vals = {
                            'move_type': 'one',
                            'picking_type_id': picking_type or False,
                            'partner_id': rma.partner_id and
                            rma.partner_id.id or
                            False,
                            'origin': rma.name,
                            'move_lines': [vals],
                            'location_id': vals[2]['location_id'],
                            'location_dest_id': vals[2]['location_dest_id'],
                            'rma_id': rma.id,
                        }
                        picking_rec_ex = self.env[
                            'stock.picking'].create(exchange_picking_vals)
                        picking_rec_ex.action_confirm()
                        picking_rec_ex.action_assign()
                    else:
                        vals[2]['picking_id'] = ex_picking.id
                        self.env['stock.move'].create(vals[2])
                # SO : Create Credit Note Invoice
                if invoice_line_vals:
                    inv_values = {
                        'type': 'out_refund',
                        'invoice_origin': rma.name or '',
                        'narration': rma.problem or '',
                        'partner_id': rma.partner_id and
                        rma.partner_id.id or False,
                        'invoice_line_ids': invoice_line_vals,
                        'invoice_date': rma.rma_date or False,
                        'rma_id': rma.id,
                    }
                    self.env['account.move'].create(inv_values)
                # SO : Create Customer Invoice if Exchange Product
                if exchange_inv_line_vals:
                    ex_inv_vals = {
                        'type': 'out_invoice',
                        'narration': rma.problem or '',
                        'invoice_origin': rma.name or '',
                        'partner_id': rma.partner_id and
                        rma.partner_id.id or False,
                        'invoice_line_ids': exchange_inv_line_vals,
                        'invoice_date': rma.rma_date or False,
                        'rma_id': rma.id,
                    }
                    self.env['account.move'].create(ex_inv_vals)
                rma.write({'state': state})
            # Check for Purchase Order Return
            elif rma.rma_type == 'supplier':
                state = 'resolved'
                exchange_moves = []
                moves_vals = []
                invoice_vals = []
                supp_inv_line_vals = []
                for line in rma.rma_purchase_lines_ids:
                    state = 'approve'
                    pol = self.env['purchase.order.line'].search([
                        ('order_id', '=', rma.purchase_order_id.id),
                        ('product_id', '=', line.product_id.id)], limit=1)
                    # Prepare Move Vals for Delivery Picking
                    rma_move_vals = {
                        'product_id': line.product_id and
                        line.product_id.id or False,
                        'name': line.product_id and
                        line.product_id.name or False,
                        'origin': rma.name,
                        'purchase_line_id': pol.id or False,
                        'group_id': rma.purchase_order_id.group_id.id,
                        'product_uom_qty': line.refund_qty or 0,
                        'location_id': line.source_location_id.id or
                        False,
                        'location_dest_id': line.destination_location_id.id or
                        False,
                        'product_uom': line.product_id.uom_id and
                        line.product_id.uom_id.id or False,
                        'rma_id': rma.id,
                        'price_unit': line.price_subtotal or 0,
                    }
                    moves_vals.append((0, 0, rma_move_vals))
                    inv_ex_account_id = line.product_id. \
                        property_account_expense_id and \
                        line.product_id. \
                        property_account_expense_id.id or \
                        line.product_id.categ_id. \
                        property_account_expense_categ_id and \
                        line.product_id.categ_id. \
                        property_account_expense_categ_id.id or False
                    if not inv_ex_account_id:
                        raise ValidationError((
                            'No account defined for product "%s".') %
                            line.product_id.name)
                    prod_price = 0.0
                    if line.refund_qty != 0:
                        prod_price = float(
                            (line.refund_price) / float(
                                line.refund_qty))
                    # PO : Invoice Line vals for Vendor Refund
                    inv_line_vals = {
                        'product_id': line.product_id and line.
                        product_id.id or False,
                        # 'account_id': inv_ex_account_id or False,
                        'name': line.product_id and line.
                        product_id.name or False,
                        'quantity': line.refund_qty or 0,
                        'price_unit': prod_price or 0,
                        'currency_id': rma.currency_id.id or False,
                    }
                    if line.tax_id and line.tax_id.ids:
                        inv_line_vals.update(
                            {'tax_ids': [(6, 0, line.
                                          tax_id.ids)]})
                    invoice_vals.append((0, 0, inv_line_vals))
                    if line.type == 'exchange':
                        state = 'approve'
                        # Prepare the move lines for exchange Moves
                        rma_move_vals_ex = {
                            'product_id': line.exchange_product_id and
                            line.exchange_product_id.id or False,
                            'name': line.exchange_product_id and
                            line.exchange_product_id.name or False,
                            'origin': rma.name,
                            'purchase_line_id': pol.id or False,
                            'group_id': rma.purchase_order_id.group_id.id,
                            'product_uom_qty': line.refund_qty or 0,
                            'location_id': line.source_location_id.id or
                            False,
                            'location_dest_id':
                            line.destination_location_id.id or
                            False,
                            'product_uom': line.exchange_product_id.uom_id and
                            line.exchange_product_id.uom_id.id or False,
                            'rma_id': rma.id,
                            'price_unit': line.price_subtotal or 0,
                        }
                        exchange_moves.append((0, 0, rma_move_vals_ex))
                        supp = self.env['product.supplierinfo'].search([
                            ('product_id', '=', line.exchange_product_id.id),
                            ('name', '=', rma.supplier_id.id)])
                        # Prepare invoice lines for supplier
                        inv_line_vals_supp = {
                            'product_id': line.exchange_product_id and
                            line.exchange_product_id.id or False,
                            'account_id': inv_ex_account_id or False,
                            'name': line.exchange_product_id and
                            line.exchange_product_id.name or False,
                            'quantity': line.refund_qty or 0,
                            'price_unit': supp.price or 0,
                            'currency_id': rma.currency_id.id or False,
                        }
                        if line.tax_id and line.tax_id.ids:
                            inv_line_vals_supp.update(
                                {'tax_ids': [(6, 0, line.
                                              tax_id.ids)]})

                        supp_inv_line_vals.append(
                            (0, 0, inv_line_vals_supp))
                for move in moves_vals:
                    picking = self.env['stock.picking'].search([
                        ('rma_id', '=', rma.id),
                        ('location_id', '=', move[2]['location_id']),
                        ('location_dest_id', '=',
                         move[2]['location_dest_id'])])
                    # If already picking is not created then create one
                    if not picking:
                        picking_type_id = self.env[
                            'stock.picking.type'].search([
                                ('code', '=', 'outgoing'),
                                ('warehouse_id.company_id', 'in',
                                 [self.env.context.get(
                                     'company_id',
                                     self.env.user.company_id.id),
                                     False])],
                            limit=1).id
                        if rma.supplier_id and rma.supplier_id.id:
                            picking_partner = rma.supplier_id.id
                        if rma.assign_owner_id and rma.assign_owner_id.id:
                            picking_partner = rma.assign_owner_id.id
                        picking_re_vals = {
                            'move_type': 'one',
                            'picking_type_id': picking_type_id or False,
                            'partner_id': picking_partner or False,
                            'origin': rma.name,
                            'move_lines': [move],
                            'location_id': move[2]['location_id'],
                            'location_dest_id': move[2]['location_dest_id'],
                            'rma_id': rma.id,
                        }
                        picking_rec_re = self.env[
                            'stock.picking'].create(picking_re_vals)
                        picking_rec_re.action_confirm()
                        picking_rec_re.action_assign()
                    else:
                        # If already picking is exists then add move to picking
                        move[2]['picking_id'] = picking.id
                        self.env['stock.move'].create(move[2])
                for vals in exchange_moves:
                    ex_picking = self.env['stock.picking'].search([
                        ('rma_id', '=', rma.id),
                        ('location_id', '=', vals[2]['location_id']),
                        ('location_dest_id', '=', vals[2]['location_dest_id']),
                        ('picking_type_code', '=', 'incoming')])
                    # Create Picking for exchange product
                    if not ex_picking:
                        picking_type = self.env['stock.picking.type'].search([
                            ('code', '=', 'incoming'),
                            ('warehouse_id.company_id', 'in',
                             [self.env.context.get(
                                 'company_id',
                                 self.env.user.company_id.id),
                              False])],
                            limit=1).id
                        # Prepare exchange move vals
                        exchange_vals = {
                            'move_type': 'one',
                            'picking_type_id': picking_type or False,
                            'partner_id': rma.supplier_id and
                            rma.supplier_id.id or
                            False,
                            'origin': rma.name,
                            'move_lines': [vals],
                            'location_id': vals[2]['location_id'],
                            'location_dest_id': vals[2]['location_dest_id'],
                            'rma_id': rma.id,
                        }
                        picking_rec_exchange = self.env[
                            'stock.picking'].create(exchange_vals)
                        picking_rec_exchange.action_confirm()
                        picking_rec_exchange.action_assign()
                    else:
                        vals[2]['picking_id'] = ex_picking.id
                        self.env['stock.move'].create(vals[2])
                # Create invoice vals for refund
                if invoice_vals:
                    inv_values = {
                        'type': 'in_refund',
                        'invoice_origin': rma.name or '',
                        'narration': rma.problem or '',
                        'partner_id': rma.supplier_id and
                        rma.supplier_id.id or False,
                        'invoice_line_ids': invoice_vals,
                        'invoice_date': rma.rma_date or False,
                        'rma_id': rma.id,
                    }
                    self.env['account.move'].create(inv_values)
                # Create Customer invoice for exchange product
                if supp_inv_line_vals:
                    ex_supp_inv_vals = {
                        'type': 'in_invoice',
                        'narration': rma.problem or '',
                        'invoice_origin': rma.name or '',
                        'partner_id': rma.supplier_id and
                        rma.supplier_id.id or False,
                        'invoice_line_ids': supp_inv_line_vals,
                        'invoice_date': rma.rma_date or False,
                        'rma_id': rma.id,
                    }
                    self.env['account.move'].create(ex_supp_inv_vals)
                rma.write({'state': state})
            else:
                state = 'resolved'
                exchange_move_vals = []
                stock_moves_vals = []
                invoice_line_vals = []
                exchange_inv_line_vals = []
                for rma_line in rma.rma_picking_lines_ids:
                    state = 'approve'
                    rma_move_vals_b2b = {
                        'product_id': rma_line.product_id and
                        rma_line.product_id.id or False,
                        'name': rma_line.product_id and
                        rma_line.product_id.name or False,
                        'origin': rma.name,
                        'product_uom_qty': rma_line.refund_qty or 0,
                        'location_id': rma_line.source_location_id.id or False,
                        'location_dest_id':
                        rma_line.destination_location_id.id or
                        False,
                        'product_uom': rma_line.product_id.uom_id and
                        rma_line.product_id.uom_id.id or False,
                        'rma_id': rma.id,
                        'price_unit': rma_line.price_subtotal or 0,
                    }
                    stock_moves_vals.append((0, 0, rma_move_vals_b2b))
                    inv_account_id = rma_line.product_id. \
                        property_account_income_id and \
                        rma_line.product_id. \
                        property_account_income_id.id or \
                        rma_line.product_id.categ_id. \
                        property_account_income_categ_id and \
                        rma_line.product_id.categ_id. \
                        property_account_income_categ_id.id or False
                    if not inv_account_id:
                        raise ValidationError((
                            'No account defined for product "%s".') %
                            rma_line.product_id.name)
                    prod_price = 0.0
                    if rma_line.refund_qty != 0:
                        prod_price = float(
                            (rma_line.refund_price) / float(
                                rma_line.refund_qty))
                    # Prepare invoice lines
                    inv_line_values = {
                        'product_id': rma_line.product_id and rma_line.
                        product_id.id or False,
                        'account_id': inv_account_id or False,
                        'name': rma_line.product_id and rma_line.
                        product_id.name or False,
                        'quantity': rma_line.refund_qty or 0,
                        'price_unit': prod_price or 0,
                        'currency_id': rma.currency_id.id or False,
                    }

                    if rma_line.tax_id and rma_line.tax_id.ids:
                        inv_line_values.update(
                            {'tax_ids': [(6, 0, rma_line.tax_id.ids)]})

                    invoice_line_vals.append((0, 0, inv_line_values))

                    if rma_line.type == 'exchange':
                        state = 'approve'
                        # If rma type is exchange then prepare exchange moves
                        rma_move_vals_b2c = {
                            'product_id': rma_line.exchange_product_id and
                            rma_line.exchange_product_id.id or False,
                            'name': rma_line.exchange_product_id and
                            rma_line.exchange_product_id.name or False,
                            'origin': rma.name,
                            'product_uom_qty': rma_line.refund_qty or 0,
                            'location_id':
                            rma_line.destination_location_id.id or
                            False,
                            'location_dest_id':
                            rma_line.source_location_id.id or
                            False,
                            'product_uom':
                            rma_line.exchange_product_id.uom_id and
                            rma_line.exchange_product_id.uom_id.id or False,
                            'rma_id': rma.id,
                            'price_unit': rma_line.price_subtotal or 0,
                        }
                        exchange_move_vals.append((0, 0, rma_move_vals_b2c))
                        inv_line_vals_exchange = {
                            'product_id': rma_line.exchange_product_id and
                            rma_line.exchange_product_id.id or False,
                            'account_id': inv_account_id or False,
                            'name': rma_line.exchange_product_id and rma_line.
                            exchange_product_id.name or False,
                            'quantity': rma_line.refund_qty or 0,
                            'price_unit':
                            rma_line.exchange_product_id.lst_price or 0,
                            'currency_id': rma.currency_id.id or False,
                        }
                        if rma_line.tax_id and rma_line.tax_id.ids:
                            inv_line_vals_exchange.update(
                                {'tax_ids': [(6, 0, rma_line.
                                              tax_id.ids)]})

                        exchange_inv_line_vals.append(
                            (0, 0, inv_line_vals_exchange))
                for move in stock_moves_vals:
                    picking = self.env['stock.picking'].search([
                        ('rma_id', '=', rma.id),
                        ('location_id', '=', move[2]['location_id']),
                        ('location_dest_id', '=',
                         move[2]['location_dest_id'])])
                    if not picking:
                        picking_type_id = self.env[
                            'stock.picking.type'].search([
                                ('code', '=', 'incoming'),
                                ('warehouse_id.company_id', 'in',
                                 [self.env.context.get(
                                     'company_id',
                                     self.env.user.company_id.id),
                                  False])],
                            limit=1).id
                        picking_vals = {
                            'move_type': 'one',
                            'picking_type_id': picking_type_id or False,
                            'partner_id': rma.picking_partner_id and
                            rma.picking_partner_id.id or
                            rma.picking_rma_id.partner_id.id or
                            False,
                            'origin': rma.name,
                            'move_lines': [move],
                            'location_id': move[2]['location_id'],
                            'location_dest_id': move[2]['location_dest_id'],
                            'rma_id': rma.id,
                        }
                        picking_rec = self.env[
                            'stock.picking'].create(picking_vals)
                        picking_rec.action_confirm()
                        picking_rec.action_assign()

                    else:
                        move[2]['picking_id'] = picking.id
                        self.env['stock.move'].create(move[2])
                for vals in exchange_move_vals:
                    ex_picking = self.env['stock.picking'].search([
                        ('rma_id', '=', rma.id),
                        ('location_id', '=', vals[2]['location_id']),
                        ('location_dest_id', '=', vals[2]['location_dest_id']),
                        ('picking_type_code', '=', 'outgoing')])
                    if not ex_picking:
                        picking_type = self.env['stock.picking.type'].search([
                            ('code', '=', 'outgoing'),
                            ('warehouse_id.company_id', 'in',
                             [self.env.context.get('company_id',
                                                   self.env.user.company_id.id
                                                   ),
                              False])],
                            limit=1).id
                        exchange_picking_vals = {
                            'move_type': 'one',
                            'picking_type_id': picking_type or False,
                            'partner_id': rma.picking_partner_id and
                            rma.picking_partner_id.id or
                            rma.picking_rma_id.partner_id.id or
                            False,
                            'origin': rma.name,
                            'move_lines': [vals],
                            'location_id': vals[2]['location_id'],
                            'location_dest_id': vals[2]['location_dest_id'],
                            'rma_id': rma.id,
                        }
                        picking_rec_ex = self.env[
                            'stock.picking'].create(exchange_picking_vals)
                        picking_rec_ex.action_confirm()
                        picking_rec_ex.action_assign()
                    else:
                        vals[2]['picking_id'] = ex_picking.id
                        self.env['stock.move'].create(vals[2])
                if invoice_line_vals:
                    inv_values = {
                        'type': 'out_refund',
                        'invoice_origin': rma.name or '',
                        'narration': rma.problem or '',
                        'partner_id': rma.picking_partner_id and
                        rma.picking_partner_id.id or
                        rma.picking_rma_id.partner_id.id or False,
                        'invoice_line_ids': invoice_line_vals,
                        'invoice_date': rma.rma_date or False,
                        'rma_id': rma.id,
                    }
                    self.env['account.move'].create(inv_values)

                if exchange_inv_line_vals:
                    ex_inv_vals = {
                        'type': 'out_invoice',
                        'narration': rma.problem or '',
                        'invoice_origin': rma.name or '',
                        'partner_id': rma.picking_partner_id and
                        rma.picking_partner_id.id or
                        rma.picking_rma_id.partner_id.id or False,
                        'invoice_line_ids': exchange_inv_line_vals,
                        'invoice_date': rma.rma_date or False,
                        'rma_id': rma.id,
                    }
                    self.env['account.move'].create(ex_inv_vals)
                rma.write({'state': state})
            return True

    def count_stock_picking(self):
        """ 
            Counting the numner of pickings.
            Redirect to Picking Views.
        """
        for rec in self:
            model_obj = self.env['ir.model.data']
            picview_id = model_obj.get_object_reference('stock',
                                                        'view_picking_form')[1]
            picking_ids = self.env["stock.picking"
                                   ].search([('rma_id', '=', rec.id)])
            if len(picking_ids.ids) > 1:
                return {
                    'name': ('Stock Pickings'),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'view_id': False,
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'domain': [('id', 'in', picking_ids.ids)],
                    'context': {'show_lots_m2o': True}
                }
            elif len(picking_ids.ids) == 1:
                return {
                    'name': ('Stock picking'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': picview_id,
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': picking_ids[0].id,
                    'context': {'show_lots_m2o': True}
                }

    def count_invoice_ids(self):
        """
            Counting the number of invoice created from RMA.
            Redirect to invoice form view and tree views based on count.
        """
        for rec in self:
            if rec.rma_type == 'customer':
                action = self.env.ref(
                    'account.action_move_out_invoice_type').read()[0]
            if rec.rma_type == 'supplier':
                action = self.env.ref(
                    'account.action_move_in_invoice_type').read()[0]
            if rec.rma_type == 'picking' or rec.rma_type == 'lot':
                action = self.env.ref(
                    'account.action_move_in_invoice_type').read()[0]
            invoice_ids = self.env["account.move"
                                   ].search([('rma_id', '=', rec.id)])
            if len(invoice_ids.ids) > 1:
                action['domain'] = [('id', 'in', invoice_ids.ids)]
            elif len(invoice_ids.ids) == 1:
                if rec.rma_type == 'customer':
                    action['views'] = [
                        (self.env.ref('account.view_move_form').id, 'form')]
                if rec.rma_type == 'supplier':
                    action['views'] = [
                        (self.env.ref('account.view_move_form').id,
                         'form')]
                if rec.picking_rma_id.picking_type_id.code == 'incoming':
                    action['views'] = [
                        (self.env.ref('account.view_move_form').id,
                         'form')]
                if rec.picking_rma_id.picking_type_id.code == 'outgoing':
                    action['views'] = [
                        (self.env.ref('account.view_move_form').id, 'form')]

                action['res_id'] = invoice_ids[0].id
            else:
                action = {'type': 'ir.actions.act_window_close'}
            return action

    def unlink(self):
        """
            Before delete rma check its status
        """
        for rma in self:
            if rma.state in ['close', 'approve']:
                raise ValidationError(_("You can not delete a Approved or \
Done RMA."))
        return super(RMARetMerAuth, self).unlink()

    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        """
            On selecting sale order auto populate data to lines from sale lines
        """
        order_line_lst = []
        for order_line in self.sale_order_id.order_line:
            rma_sale_line = (0, 0, {
                'product_id': order_line.product_id and
                order_line.product_id.id or False,
                'total_qty': order_line.product_uom_qty or 0,
                'delivered_quantity': order_line.qty_delivered,
                'order_quantity': order_line.product_uom_qty or 0,
                'refund_qty': order_line.qty_delivered,
                'refund_price': order_line.price_unit,
                'price_unit': order_line.price_unit or 0,
                'price_subtotal': order_line.price_subtotal or 0,
                'source_location_id':
                self.env.user.company_id.source_location_id.id or
                False,
                'destination_location_id': self.env.user.company_id.
                destination_location_id.id or False,
                'type': 'return',
                'tax_id': order_line.tax_id,
                'discount': order_line.discount
            })
            order_line_lst.append(rma_sale_line)
        self.rma_sale_lines_ids = [(5,)]
        self.rma_sale_lines_ids = order_line_lst

    @api.onchange('picking_rma_id')
    def onchange_picking_rma_id(self):
        """
            On selection of picking auto add lines from stock moves
        """
        order_line_lst = []
        for order_line in self.picking_rma_id.move_lines:
            move = self.env['stock.move'].search([
                ('picking_id', '=', self.picking_rma_id.id),
                ('product_id', '=', order_line.product_id.id)])
            so_line = self.env['rma.sale.lines'].search([
                ('product_id', '=', order_line.product_id.id),
                ('rma_id', '=', self.picking_rma_id.rma_id.id)])
            taxes = []
            if move.picking_id.rma_id.rma_type == 'customer':
                line = self.env['rma.sale.lines'].search([
                    ('exchange_product_id', '=', order_line.product_id.id),
                    ('rma_id', '=', move.rma_id.id)])
                taxes = line.tax_id
            if move.picking_id.rma_id.rma_type == 'supplier':
                line = self.env['rma.purchase.lines'].search([
                    ('exchange_product_id', '=', order_line.product_id.id),
                    ('rma_id', '=', move.rma_id.id)])
                taxes = line.tax_id
            rma_pick_line = {
                'product_id': order_line.product_id and
                order_line.product_id.id or False,
                'total_qty': order_line.quantity_done or 0,
                'delivered_quantity': order_line.quantity_done,
                'order_quantity': order_line.product_uom_qty or 0,
                'refund_qty': order_line.quantity_done,
                'refund_price': order_line.product_id.lst_price,
                'price_unit': order_line.product_id.lst_price or 0,
                'source_location_id':
                self.env.user.company_id.source_location_id.id or
                False,
                'destination_location_id': self.env.user.company_id.
                destination_location_id.id or False,
                'type': 'return',
                'tax_id': taxes or False
            }
            if self.picking_rma_id.picking_type_id.code == 'incoming' and \
                    so_line:
                rma_pick_line.update({'discount': so_line.discount or 0.0})
            order_line_lst.append((0, 0, rma_pick_line))
        self.rma_picking_lines_ids = [(5,)]
        self.rma_picking_lines_ids = order_line_lst

    @api.onchange('lot_picking_id')
    def onchange_lot_picking_id(self):
        """
            Based on lot find it's picking and from picking auto add lines
        """
        order_line_lst = []
        for order_line in self.lot_picking_id.move_lines:
            move = self.env['stock.move'].search([
                ('picking_id', '=', self.picking_rma_id.id),
                ('product_id', '=', order_line.product_id.id)])
            taxes = []
            if move.picking_id.rma_id.rma_type == 'customer':
                line = self.env['rma.sale.lines'].search(
                    [('product_id', '=', order_line.product_id.id),
                     ('rma_id', '=', move.rma_id.id)])
                taxes = line.tax_id
            if move.picking_id.rma_id.rma_type == 'supplier':
                line = self.env['rma.purchase.lines'].search(
                    [('product_id', '=', order_line.product_id.id),
                     ('rma_id', '=', move.rma_id.id)])
                taxes = line.tax_id
            quant = self.env['stock.quant'].search([
                ('lot_id.name', '=', self.rma_lot)])
            rma_pick_line = (0, 0, {
                'product_id': order_line.product_id and
                order_line.product_id.id or False,
                'total_qty': order_line.quantity_done or 0,
                'delivered_quantity': order_line.quantity_done,
                'order_quantity': order_line.product_uom_qty or 0,
                'refund_qty': order_line.quantity_done,
                'refund_price': order_line.product_id.lst_price,
                'price_unit': order_line.product_id.lst_price or 0,
                'source_location_id': quant.location_id.id or False,
                'destination_location_id': quant.owner_id.property_stock_supplier.id or
                self.env.user.company_id.destination_location_id.id or False,
                'type': 'return',
                'tax_id': taxes or False
            })
            order_line_lst.append(rma_pick_line)
        self.rma_picking_lines_ids = [(5,)]
        self.rma_picking_lines_ids = order_line_lst


class RmaSaleLines(models.Model):
    _name = "rma.sale.lines"
    _description = "Return Merchandise Authorization Sale Lines"

    @api.depends('refund_qty', 'price_unit', 'discount', 'tax_id')
    def _compute_amount(self):
        """Compute the amounts of the SO line."""
        for line in self:
            refund_qty = line.refund_qty
            if line.refund_qty == 0:
                refund_qty = 0
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.rma_id.currency_id,
                                            refund_qty,
                                            product=line.product_id,
                                            partner=line.rma_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'refund_price': refund_qty * price
            })

    @api.model
    def create(self, vals):
        """
        Check if souce location and destination location is configured or not
        """
        if not vals.get('source_location_id' and 'destination_location_id'):
            raise ValidationError(
                _('''Please Configure valid source and destination \
location in your company!'''))
        res = super(RmaSaleLines, self).create(vals)
        return res

    @api.constrains('refund_qty', 'delivered_quantity')
    def _check_refund_quantity(self):
        for line in self:
            if line.refund_qty <= 0:
                raise ValidationError(('Return Quantity should be greater than \
Zero'))
            if line.order_quantity < line.refund_qty:
                raise ValidationError(('Return Quantity should \
not be greater than order quantity'))
            if line.order_quantity < line.delivered_quantity:
                raise ValidationError(('Delivered quantity should \
not be greater than order quantity'))
            if line.refund_qty > line.delivered_quantity:
                raise ValidationError(('Return Quantity should not be greater \
than delivered quantity'))

    @api.model
    def _get_source_location(self):
        # Select Source location from current user company
        return self.env.user.company_id.source_location_id or\
            self.env['stock.location']

    @api.model
    def _get_destination_location(self):
        # Select Destination location from current user company
        return self.env.user.company_id.destination_location_id or\
            self.env['stock.location']

    rma_id = fields.Many2one('rma.ret.mer.auth', string='RMA')
    product_id = fields.Many2one('product.product', string='Product')
    reason_id = fields.Many2one("rma.reasons", string="Reason")
    reason = fields.Text(string="Reason")
    currency_id = fields.Many2one(
        "res.currency",
        related='rma_id.partner_id.property_product_pricelist.currency_id',
        string='Currency',
        readonly=True)
    total_qty = fields.Integer(
        string='Total Qty', readonly=False)
    order_quantity = fields.Integer('Ordered Qty')
    delivered_quantity = fields.Integer('Delivered Qty')
    price_unit = fields.Float('Unit Price')
    refund_qty = fields.Integer('Return Qty')
    refund_price = fields.Float(compute='_compute_amount',
                                string='Refund Price', compute_sudo=True)
    total_price = fields.Float(string='Total Price')
    type = fields.Selection([('return', 'Return'), ('exchange', 'Exchange')],
                            string='Action', default='return')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    price_subtotal = fields.Float(compute='_compute_amount',
                                  string='Subtotal', readonly=True,
                                  store=True, compute_sudo=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes',
                             readonly=True, store=True, compute_sudo=True)
    price_total = fields.Float(compute='_compute_amount', string='Total',
                               readonly=True, store=True, compute_sudo=True)
    source_location_id = fields.Many2one('stock.location',
                                         'Source Location',
                                         default=_get_source_location
                                         )
    destination_location_id = fields.Many2one(
        'stock.location',
        'Destination Location',
        default=_get_destination_location
    )
    exchange_product_id = fields.Many2one(
        'product.product', 'Exchange Product')

    @api.constrains('total_qty', 'refund_qty')
    def _check_rma_quantity(self):
        for line in self:
            if line.total_qty != 0.0 and line.refund_qty > line.total_qty:
                raise ValidationError(('Return Quantity should not greater \
                  than Total Quantity.'))

    @api.onchange('refund_qty', 'total_qty')
    def onchange_refund_price(self):
        for order in self:
            if order.total_qty != 0.0 and order.refund_qty > order.total_qty:
                raise ValidationError(('Return Quantity should not be greater \
than Total Quantity.'))
            total_qty_amt = 0.0
            if order.total_price and order.total_qty:
                total_qty_amt = (order.total_price /
                                 order.total_qty) * float(order.refund_qty)
                order.refund_price = total_qty_amt
            else:
                if order.product_id and order.product_id.id:
                    order.refund_price = order.product_id.lst_price * \
                        order.refund_qty


class RmaPurchaseLines(models.Model):
    _name = "rma.purchase.lines"
    _description = "Return Merchandise Authorization Purchase Lines"

    @api.depends('refund_qty', 'price_unit', 'tax_id', 'discount')
    def _compute_amount(self):
        """Compute the amounts of the SO line."""
        for line in self:
            refund_qty = line.refund_qty
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.rma_id.currency_id,
                                            refund_qty,
                                            product=line.product_id,
                                            partner=line.rma_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'refund_price': refund_qty * price,
            })

    @api.model
    def create(self, vals):
        if not vals.get('source_location_id' and 'destination_location_id'):
            raise ValidationError(
                _('''Please Configure valid source and\
                 destination location in your company!'''))
        res = super(RmaPurchaseLines, self).create(vals)
        return res

    # @api.model
    # def _get_source_location(self):
    #     return self.env.user.company_id.source_location_id or\
    #         self.env['stock.location']

    # @api.model
    # def _get_destination_location(self):
    #     return self.env.user.company_id.destination_location_id or\
    #         self.env['stock.location']

    rma_id = fields.Many2one('rma.ret.mer.auth', 'RMA')
    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    product_id = fields.Many2one('product.product', 'Product')
    reason_id = fields.Many2one("rma.reasons", string="Reason")
    reason = fields.Text(string="Reason")
    currency_id = fields.Many2one(
        "res.currency",
        related='rma_id.company_id.currency_id',
        string='Currency', readonly=True)
    total_qty = fields.Integer(
        string='Total Qty', readonly=False)
    order_quantity = fields.Integer('Ordered Qty')
    delivered_quantity = fields.Integer('Delivered Qty')
    price_unit = fields.Float('Unit Price')
    refund_qty = fields.Integer('Return Qty', default=1)
    refund_price = fields.Float(compute='_compute_amount',
                                string='Refund Price', compute_sudo=True)
    total_price = fields.Float(
        string='Total Price')
    type = fields.Selection([('return', 'Return'), ('exchange', 'Exchange')],
                            string='Action', default='return')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Float(compute='_compute_amount',
                                  string='Subtotal', readonly=True,
                                  store=True, compute_sudo=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes',
                             readonly=True, store=True, compute_sudo=True)
    price_total = fields.Float(compute='_compute_amount', string='Total',
                               readonly=True, store=True, compute_sudo=True)
    source_location_id = fields.Many2one('stock.location',
                                         'Source Location'
                                         )
    destination_location_id = fields.Many2one(
        'stock.location',
        'Destination Location'
    )
    exchange_product_id = fields.Many2one(
        'product.product', 'Exchange Product')

    @api.constrains('total_qty', 'refund_qty')
    def _check_rma_quantity(self):
        for line in self:
            if line.total_qty != 0.0 and line.refund_qty > line.total_qty:
                raise ValidationError(('Return Quantity should not greater \
                  than Total Quantity.'))

#     @api.constrains('refund_qty', 'delivered_quantity')
#     def _check_refund_quantity(self):
#         for line in self:
#             if line.refund_qty <= 0:
#                 raise ValidationError(('Return Quantity should be greater than \
# Zero'))
#             if line.order_quantity < line.refund_qty:
#                 raise ValidationError(('Return Quantity should \
# not be greater than order quantity'))
#             if line.order_quantity < line.delivered_quantity:
#                 raise ValidationError(('Delivered quantity should \
# not be greater than order quantity'))
#             if line.refund_qty > line.delivered_quantity:
#                 raise ValidationError(('Return Quantity should not be greater \
# than delivered quantity'))

    @api.onchange('refund_qty', 'total_qty')
    def onchange_refund_price(self):
        for order in self:
            if order.total_qty != 0.0 and order.refund_qty > order.total_qty:
                raise ValidationError(('Return Quantity should not greater \
                  than Total Quantity.'))
            total_qty_amt = 0.0
            if order.total_price and order.total_qty:
                total_qty_amt = (order.total_price /
                                 order.total_qty) * float(order.refund_qty)
                order.refund_price = total_qty_amt
            else:
                if order.product_id and order.product_id.id:
                    order.refund_price = order.product_id.lst_price * order.\
                        refund_qty

    @api.onchange('reason_id')
    def _onchange_reason(self):
        if self.reason_id:
            self.destination_location_id = self.reason_id.sup_destination_location_id
            self.source_location_id = self.reason_id.sup_source_location_id

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.price_unit = self.product_id.standard_price


class RmaPickingLines(models.Model):
    _name = "rma.picking.lines"
    _description = "Return Merchandise Authorization picking Lines"

    @api.depends('refund_qty', 'price_unit', 'discount', 'tax_id')
    def _compute_amount(self):
        """Compute the amounts of the SO line."""
        for line in self:
            refund_qty = line.refund_qty
            if line.refund_qty == 0:
                refund_qty = 0
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.rma_id.currency_id,
                                            refund_qty,
                                            product=line.product_id,
                                            partner=line.rma_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'refund_price': refund_qty * price
            })

    @api.model
    def create(self, vals):
        if not vals.get('source_location_id' and 'destination_location_id'):
            raise ValidationError(
                _('''Please Configure valid source and destination\
                 location in your company!'''))
        res = super(RmaPickingLines, self).create(vals)
        return res

    @api.constrains('refund_qty')
    def _check_refund_quantity(self):
        for line in self:
            if line.refund_qty <= 0:
                raise ValidationError(('Return Quantity should be greater than \
Zero'))

    @api.model
    def _get_source_location(self):
        return self.env.user.company_id.source_location_id or\
            self.env['stock.location']

    @api.model
    def _get_destination_location(self):
        return self.env.user.company_id.destination_location_id or\
            self.env['stock.location']

    rma_id = fields.Many2one('rma.ret.mer.auth', 'RMA')
    product_id = fields.Many2one('product.product', 'Product')
    reason_id = fields.Many2one("rma.reasons", string="Reason")
    reason = fields.Text(string="Reason")
    currency_id = fields.Many2one(
        "res.currency",
        related='rma_id.company_id.currency_id',
        string='Currency',
        readonly=True)
    total_qty = fields.Integer(
        string='Total Qty', readonly=False)
    order_quantity = fields.Integer('Ordered Qty')
    delivered_quantity = fields.Integer('Delivered Qty')
    price_unit = fields.Float('Unit Price')
    refund_qty = fields.Integer('Return Qty')
    refund_price = fields.Float(compute='_compute_amount',
                                string='Refund Price', compute_sudo=True)
    total_price = fields.Float(string='Total Price')
    type = fields.Selection([('return', 'Return'), ('exchange', 'Exchange')],
                            string='Action', default='return')
    tax_id = fields.Many2many('account.tax', string='Taxes')
    discount = fields.Float(string='Discount (%)', digits=(16, 2), default=0.0)
    price_subtotal = fields.Float(compute='_compute_amount',
                                  string='Subtotal', readonly=True,
                                  store=True, compute_sudo=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes',
                             readonly=True, store=True, compute_sudo=True)
    price_total = fields.Float(compute='_compute_amount', string='Total',
                               readonly=True, store=True, compute_sudo=True)
    source_location_id = fields.Many2one('stock.location',
                                         'Source Location',
                                         default=_get_source_location
                                         )
    destination_location_id = fields.Many2one(
        'stock.location',
        'Destination Location',
        default=_get_destination_location
    )
    exchange_product_id = fields.Many2one(
        'product.product', 'Exchange Product')

    @api.constrains('total_qty', 'refund_qty', 'delivered_quantity')
    def _check_rma_quantity(self):
        for line in self:
            if line.total_qty != 0.0 and line.refund_qty > line.total_qty:
                raise ValidationError(('Return Quantity should not be greater \
than Total Quantity.'))
            if line.order_quantity < line.refund_qty:
                raise ValidationError(('Return Quantity should \
not be greater than order quantity'))
            if line.order_quantity < line.delivered_quantity:
                raise ValidationError(('Delivered quantity should \
not be greater than order quantity'))

    @api.onchange('refund_qty', 'total_qty')
    def onchange_refund_price(self):
        for order in self:
            if order.total_qty != 0.0 and order.refund_qty > order.total_qty:
                raise ValidationError(('Return Quantity should not be greater \
than Total Quantity.'))
            total_qty_amt = 0.0
            if order.total_price and order.total_qty:
                total_qty_amt = (order.total_price /
                                 order.total_qty) * float(order.refund_qty)
                order.refund_price = total_qty_amt
            else:
                if order.product_id and order.product_id.id:
                    order.refund_price = order.product_id.lst_price * \
                        order.refund_qty


class RmaReasons(models.Model):
    _name = "rma.reasons"
    _description = "Reasons For Creating RMA Record"

    name = fields.Char("Reason", required=True)
    type = fields.Selection([('return', 'Return'), ('exchange', 'Exchange')],
                            string='Action', default='return')
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        domain=[('usage', '=', 'customer')]
        )
    destination_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        domain=[('usage', '=', 'internal')]
    )
    sup_source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        domain=[('usage', '=', 'internal')]
        )
    sup_destination_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        domain=[('usage', '=', 'supplier')]
    )
    is_customer = fields.Boolean(string="Customer")
    is_vendor = fields.Boolean(string="Vendor")


class StockLocation(models.Model):
    _inherit = "stock.location"
    _description = "Stock Location"

    # @api.model
    # def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
    #     args = args or []
    #     context = self._context or {}
    #     if context.get('return_reason'):
    #         args.append(('company_id', '=', self.env.company.id))
    #     return super(StockLocation, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
