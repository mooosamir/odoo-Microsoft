from odoo import api, fields, models, _


class SaleOrderLineHCPCS(models.Model):
    _name = 'sale.order.line.hcpcs'
    _description = 'sale.order.line.hcpcs'

    name = fields.Char('Name', default='HCPCS Details')
    order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_id = fields.Many2one('product.product', string='Product ID', force_save=True)
    hcpcs_code = fields.Many2many('spec.procedure.code',string='HCPCS Code')
    hcpcs_modifier = fields.Many2one('spec.lens.modifier',string='Modifier')
    currency_id = fields.Many2one('res.currency', string="currency", required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    retail_price = fields.Monetary('Retail Price')
    copay = fields.Monetary('Copay')
    pt_resp = fields.Monetary('PT Resp')
    qty = fields.Float('QTY', default=1)
    pt_total = fields.Monetary('PT Total', compute='pt_total_calculations')
    insurance = fields.Monetary('Insurance')
    insurance_id = fields.Integer('Insurance ID')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sale_order_line_wizard_id = fields.Many2one('multi.order.type')
    categ_id = fields.Many2one('product.category')
    spec_product_type = fields.Selection([('lens','Lens'),('frame','Frame'),('contact_lens_os','Contact Lens OS'), ('contact_lens_od','Contact Lens OD'), ('accessory', 'Miscellaneous'), ('lens_treatment', 'Lens Treatment'),('service','Services')])
    line_id = fields.Float('Line ID')

    @api.onchange('copay','pt_resp', 'insurance_id')
    def pt_total_calculations(self):
        for rec in self:
            rec.pt_total = rec.retail_price * rec.qty
            if rec.sale_order_line_wizard_id.insurance_id.id:
                rec.pt_total = rec.copay + rec.pt_resp if rec.copay > 0 or rec.pt_resp > 0 else rec.retail_price * rec.qty
                if rec.copay == 0.00 and rec.pt_resp == 0.00:
                    rec.insurance = rec.qty * rec.retail_price
                else:
                    rec.insurance = rec.qty * rec.retail_price - rec.pt_total
            else:
                rec.insurance = 0



            # rec.insurance = (0 if (rec.retail_price - rec.pt_total) < 0 else (
            #             rec.retail_price - rec.pt_total)) if rec.insurance_id else 0



