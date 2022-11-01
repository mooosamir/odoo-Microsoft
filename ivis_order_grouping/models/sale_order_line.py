from odoo import models, fields, api, _, exceptions


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('co_pay', 'pt_resp', 'price_unit')
    def sum_pay_pt(self):
        for rec in self:
            rec.pt_total = rec.price_unit * rec.product_uom_qty
            if rec.insurance_id.id:
                rec.pt_total = rec.co_pay + rec.pt_resp if rec.co_pay > 0 or rec.pt_resp > 0 else rec.price_unit * rec.product_uom_qty
                rec.insur = rec.product_uom_qty * rec.price_unit - rec.pt_total if rec.product_uom_qty * rec.price_unit - rec.pt_total > 0 else 0
            else:
                rec.insur = 0

    # discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    discount = fields.Monetary('Discount')
    discount_amount = fields.Monetary('Discount')
    discount_compute = fields.Monetary('Discount')
    discount_reason = fields.Many2one('discount.reason', string="Discount Reason")
    discount_type = fields.Selection([('Flat', 'Flat'), ('Percentage', 'Percentage')],
                                     string="Discount Type", default="Percentage")

    # @api.onchange('discount_compute', 'discount_type')
    def _compute_discount(self):
        for res in self:
            if res.discount_type in ['Flat', 'Percentage']:
                if res.display_type == 'line_section':
                    order_lines = res.order_id.order_line.filtered(
                        lambda x: x.lab_details_id == res.lab_details_id and x.display_type != 'line_section')
                    for order_line in order_lines:
                        discount = res.discount_compute if res.discount_type == 'Percentage' else (1 - (
                                order_line.price_unit - res.discount_compute) / order_line.price_unit) * 100
                        order_line.update({
                            'discount_type': res.discount_type,
                            'discount_reason': res.discount_reason,
                            'discount': discount,
                            'discount_amount': (res.price_unit - res.price_unit * (
                                        1 - (discount or 0.0) / 100.0)) * res.product_uom_qty if discount != 0 else 0
                        })
                        if not res.discount_reason:
                            res.update({
                                'discount': 0,
                                'discount_amount': 0
                            })
                else:
                    discount = res.discount_compute if res.discount_type == 'Percentage' else (1 - (
                            res.price_unit - res.discount_compute) / res.price_unit) * 100
                    res.update({
                        'discount': discount,
                        'discount_amount': (res.price_unit - res.price_unit * (
                                    1 - (discount or 0.0) / 100.0)) * res.product_uom_qty if discount != 0 else 0
                    })
                    if not res.discount_reason:
                        res.update({
                            'discount': 0,
                            'discount_amount': 0
                        })

    # def _compute_discount_amount(self):
    #     for res in self:
    #         res.discount_amount = res.price_unit * (1 - (res.discount or 0.0) / 100.0)

    price_unit = fields.Monetary('Retail')
    prescription_id = fields.Many2one('spec.contact.lenses', string="Prescription")
    lab_details_id = fields.Many2one('multi.order.type', string='Lab Details', copy=False)
    insurance_id = fields.Many2one('spec.insurance')
    authorization_id = fields.Many2one('spec.insurance.authorizations')
    co_pay = fields.Float(string='CO-PAY')
    pt_resp = fields.Float(string='PT RESP')
    pt_total = fields.Float(string='PT TOTAL', compute='sum_pay_pt')
    insur = fields.Integer(string='INSUR', compute='sum_pay_pt')
    DX = fields.Many2many('sale.line.diagnosis.setup', 'sale_line_id', domain="[('sale_id','=',order_id)]")
    actual_retail = fields.Float(string='Retails', String='Product Price')
    spec_product_type = fields.Selection([('frame', 'Frames'),
                                          ('lens', 'lens'),
                                          ('contact_lens', 'Contact Lens'),
                                          ('accessory', 'Accessory'),
                                          ('service', 'Service'),
                                          ('lens_treatment', 'Lens Treatments'),
                                          ('lens_parameter', 'Lens Parameter')], related='product_id.spec_product_type')
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id')
    categ_id = fields.Many2one('product.category', related='product_tmpl_id.categ_id')

    @api.onchange('product_uom_qty')
    def _restrict_qty(self):
        for rec in self:
            if rec.product_id.product_tmpl_id.categ_id.name in ['Frames', 'Lens', 'Lens Treatment', 'Services',
                                                                    'Contact Lens', 'Accessory']:
                raise exceptions.ValidationError(_("You cannot change Quantity"))

    def _prepare_invoice_line(self):
        res = super(SaleOrderLineInherit, self)._prepare_invoice_line()
        vals = {
            'prescription_id': self.prescription_id.id,
            'lab_details_id': self.lab_details_id.id,
            'insurance_id': self.insurance_id.id,
            'authorization_id': self.authorization_id.id,
            'co_pay': self.co_pay,
            'pt_resp': self.pt_resp,
            'pt_total': self.pt_total,
            'insur': self.insur,
            'actual_retail': self.actual_retail,
            'DX': [(6, 0, self.DX.ids)],
        }
        res.update(vals)
        return res

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.lab_details_id.insurance_id.carrier_id.apply_tax == 'yes':
                price = 0
                if line.lab_details_id.insurance_id.carrier_id.patient_tax_responsibility == 'pt_total':
                    price = line.pt_total * (1 - (line.discount or 0.0) / 100.0)
                elif line.lab_details_id.insurance_id.carrier_id.patient_tax_responsibility == 'copay':
                    price = line.co_pay * (1 - (line.discount or 0.0) / 100.0)
                elif line.lab_details_id.insurance_id.carrier_id.patient_tax_responsibility == 'retail':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                actual_price = line.price_unit * line.product_uom_qty
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)
                if line.product_id.product_tmpl_id.categ_id.name == 'Frames' and line.product_id.taxes_id and line.lab_details_id.prescription_id.id:
                    line.update({
                        'price_subtotal': actual_price,
                        'tax_id': False,
                    })
                else:
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': actual_price,
                    })
                    if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                            'account.group_account_manager'):
                        line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
            else:
                super(SaleOrderLineInherit, self)._compute_amount()

    def apply_discount(self):
        if self.order_id.state in ['done', 'locked']:
            raise exceptions.ValidationError("Can't change data in this state.")
        return {
            'name': 'Discount',
            'view_mode': 'form',
            'view_id': self.env.ref('ivis_order_grouping.discount_form').id,
            'res_model': 'sale.order.line',
            'res_id': self.id,
            'views': [[self.env.ref('ivis_order_grouping.discount_form').id, 'form']],
            'type': 'ir.actions.act_window',
            'target': 'new',
            # 'domain': ([('multi_order_type_id', '=', self.id)])
        }

    def compute_discount_and_close_window(self):
        self._compute_discount()
        return {
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': self.order_id.id,
            'views': [[False, 'form']],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
