from odoo import api, fields, models, _, exceptions
import logging
_logger = logging.getLogger(__name__)


class MultiOrderTypes(models.Model):
    _inherit = "multi.order.type"

    # frame
    is_frame = fields.Boolean(default=False)
    frames_products_variants_return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    frames_products_variants_post_sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
    # lens
    is_lens = fields.Boolean(default=False)
    lens_products_return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    lens_products_post_sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
    # miscellaneous
        # added in 'miscellaneous.products'
    # contact_lens
    contact_lens_products_od_return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    contact_lens_products_od_post_sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
    contact_lens_products_os_return_location = fields.Many2one('stock.location', string="Post Sale Return Location")
    contact_lens_products_os_post_sale_order_line_id = fields.Many2one('sale.order.line', string="Post Sale Order Line")
    # service
        # added in service.products
    # lens_treatment
    lenstreatment_products_ids = fields.One2many('lens_treatment.products', 'multi_order_type_id')
    # lens_parameter
        #  not needed for now.
    # Post Sale
    is_post_sale = fields.Boolean(default=False)
    post_sale_type = fields.Selection([('Return', 'Return'), ('Remake', 'Remake'),
                                       ('Exchange', 'Exchange'), ('Warranty', 'Warranty'),
                                       ])
    # reading_rx = fields.Boolean(default=False, string='Reading RX')
    display_name = fields.Char(string='Display Name')

    def create_lines(self):
        sale_order_id = self.env['sale.order'].browse(int(self.name))
        vals = {'display_type': 'line_section', 'name': str(self.order_type_name) + " - " + str(self.insurance_id.name) + " - " + str(self.authorization_id.name),
                'lab_details_id': self.id,
                'order_id': sale_order_id.id,
                'insurance_id': self.insurance_id.id}

        if self.prescription_id.id and self.seg_ht_lab_details == '0.00' and self.gls_add and self.gls_left_lens_add:
            raise exceptions.UserError(_("A Seg Ht is required"))

        for hcpcs_id in self.hcpcs_id:
            sum = (hcpcs_id.retail_price * hcpcs_id.qty)
            if hcpcs_id.pt_total > sum:
                raise exceptions.ValidationError("in HCPCS Details \n Pt total must be less then (retail_price * qty)")

        if self in list(sale_order_id.order_line.mapped('lab_details_id')):
            for line in sale_order_id.order_line.filtered(lambda x: x.lab_details_id == self):
                line.unlink()

        section = sale_order_id.order_line.create(vals)
        letter = ''

        if self.order_type_name in ['Complete Pair', 'Lenses Only']:
            letter = 'G'
        elif self.order_type_name == 'Frame Only':
            letter = 'F'
        elif self.order_type_name == 'Contact Lens':
            letter = 'CL'
        elif self.order_type_name == 'Services':
            letter = 'S'
        elif self.order_type_name == 'Miscellaneous':
            letter = 'A'
        insurance_id = ""
        authorization_id = ""
        if self.insurance_id.id:
            insurance_id = " - " +str(self.insurance_id.display_name)
            if self.authorization_id.id:
                authorization_id = " - " +str(self.authorization_id.display_name)

        if self.post_sale_type == 'Remake':
            section.write({'name': "REMK " + str(self.order_type_name) + ' - ' + letter + str(section.id) + insurance_id + authorization_id})
        elif self.post_sale_type == 'Warranty':
            section.write({'name': "WTY " + str(self.order_type_name) + ' - ' + letter + str(section.id) + insurance_id + authorization_id})
        else:
            section.write({'name': str(self.order_type_name) + ' - ' + letter + str(section.id) + insurance_id + authorization_id})

        self.display_name = letter + str(section.id)
        self.patient_name = self.partner_id
        self.sale_order_id = int(self.name)
        vals.clear()
        if self.frames_products_variants:
            # prd = self.env['product.product'].search([('product_tmpl_id', '=', self.frames_products_variants.id)],
            #                                                      order='id asc')[0]
            copay = float()
            pt_resp = float()
            for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Frames'):
                copay += hcpcs.copay
                pt_resp += hcpcs.pt_resp

            product_uom_qty = 1
            if ((self.is_frame or self.env.context.get('frames_products_variants', False)) and self.post_sale_type != 'Warranty') or \
                (self.post_sale_type == 'Remake' and not self.frames_products_variants_return_location.id):
                product_uom_qty = -1

            vals = {
                'order_id': sale_order_id.id,
                'product_id': self.frames_products_variants.id,
                'product_uom_qty': product_uom_qty,
                'name': self.frames_products_variants.name,
                'prescription_id': self.prescription_id.id,
                'lab_details_id': self.id,
                'insurance_id': self.insurance_id.id,
                'authorization_id': self.authorization_id.id,
                'dest_address_id' : self.ship_to.id,
                'co_pay': 0 if self.post_sale_type == 'Warranty' else copay,
                'pt_resp': 0 if self.post_sale_type == 'Warranty' else pt_resp,
                'return_location': self.frames_products_variants_return_location.id,
                'post_sale_order_line_id': self.frames_products_variants_post_sale_order_line_id.id,
            }
            if self.is_frame or self.post_sale_type == "Warranty":
                vals['price_unit'] = 0
            if self.post_sale_type == "Remake":
                vals['price_unit'] = 0
                vals['pt_total'] = 0
            order_line = self.env['sale.order.line'].create(vals)
            for hcpcs_id in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Frames'):
                hcpcs_id.order_line_id = order_line.id
        vals.clear()
        if self.contact_lens_products_od:
            # prd = self.env['product.product'].search([('product_tmpl_id', '=', self.contact_lens_products_od.id)],
            #                                            order='id asc')[0]
            prd = self.contact_lens_products_od
            copay = float()
            pt_resp = float()
            for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Contact Lens'):
                copay += hcpcs.copay
                pt_resp += hcpcs.pt_resp

            product_uom_qty = self.od_qty
            if (self.env.context.get('contact_lens_products_od', False) and self.post_sale_type != 'Warranty') or \
                (self.post_sale_type == 'Remake' and not self.contact_lens_products_od_return_location.id):
                product_uom_qty = self.od_qty * -1

            vals = {
                'order_id': sale_order_id.id,
                'product_id': prd.id,
                'name': prd.name,
                'product_uom_qty': product_uom_qty,
                'prescription_id': self.prescription_id.id,
                'lab_details_id': self.id,
                'dest_address_id': self.ship_to.id,
                'insurance_id': self.insurance_id.id,
                'co_pay': 0 if self.post_sale_type == 'Warranty' else copay,
                'pt_resp': 0 if self.post_sale_type == 'Warranty' else pt_resp,
                'return_location': self.contact_lens_products_od_return_location.id,
                'post_sale_order_line_id': self.contact_lens_products_od_post_sale_order_line_id.id,
            }
            if self.post_sale_type == "Warranty":
                vals['price_unit'] = 0
            if self.post_sale_type == "Remake":
                vals['price_unit'] = 0
                vals['pt_total'] = 0
            order_line = self.env['sale.order.line'].create(vals)
            for hcpcs_id in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Contact Lens'):
                hcpcs_id.order_line_id = order_line.id
        vals.clear()
        if self.contact_lens_products_os:
            # prd = self.env['product.product'].search([('product_tmpl_id', '=', self.contact_lens_products_os.id)],
            #                                            order='id asc')[0]
            prd = self.contact_lens_products_os
            copay = float()
            pt_resp = float()
            for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Contact Lens'):
                copay += hcpcs.copay
                pt_resp += hcpcs.pt_resp

            product_uom_qty = self.os_qty
            if (self.env.context.get('contact_lens_products_os', False) and self.post_sale_type != 'Warranty') or \
                (self.post_sale_type == 'Remake' and not self.contact_lens_products_os_return_location.id):
                product_uom_qty = self.os_qty * -1

            vals = {
                'order_id': sale_order_id.id,
                'product_id': prd.id,
                'name': prd.name,
                'product_uom_qty': product_uom_qty,
                'prescription_id': self.prescription_id.id,
                'lab_details_id': self.id,
                'dest_address_id': self.ship_to.id,
                'insurance_id': self.insurance_id.id,
                'co_pay': 0 if self.post_sale_type == "Warranty" else copay,
                'pt_resp': 0 if self.post_sale_type == "Warranty" else pt_resp,
                'return_location': self.contact_lens_products_os_return_location.id,
                'post_sale_order_line_id': self.contact_lens_products_os_post_sale_order_line_id.id,
            }
            if self.post_sale_type == "Warranty":
                vals['price_unit'] = 0
            if self.post_sale_type == "Remake":
                vals['price_unit'] = 0
                vals['pt_total'] = 0
            order_line = self.env['sale.order.line'].create(vals)
            for hcpcs_id in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Contact Lens'):
                hcpcs_id.order_line_id = order_line.id
        vals.clear()
        lens_product_uom_qty = 0
        if self.lens_products:
            # prd = self.env['product.product'].search([('product_tmpl_id', '=', self.lens_products.id)],
            #                                                      order='id asc')[0]
            prd = self.lens_products
            # product_uom_qty = 1 if prd.pair_each == 'pair' else 2
            product_uom_qty = 2 if self.eye_lab_details == 'Both' else 1
            lens_product_uom_qty = product_uom_qty
            pof_product_uom_qty = 1
            copay = float()
            pt_resp = float()

            for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Lens'):
                copay += hcpcs.copay
                pt_resp += hcpcs.pt_resp

            if ((self.is_lens or self.env.context.get('lens_products', False)) and self.post_sale_type != 'Warranty') or \
                (self.post_sale_type == 'Remake' and not self.lens_products_return_location.id):
                product_uom_qty = product_uom_qty * -1
                pof_product_uom_qty = product_uom_qty * -1
            if self.order_type_name == 'Lenses Only':
                lens_product = self.env['product.product'].search([('name','=','POF')])
                if not lens_product.id:
                    lens_product = self.env['product.product'].create({
                        'name': 'POF',
                        'type': 'service',
                        'spec_product_type': None,
                    })
                vals = {
                    'order_id': sale_order_id.id,
                    'product_id': lens_product.id,
                    'name': 'POF',
                    'product_uom_qty': pof_product_uom_qty,
                    # 'product_uom_qty': 2 if self.uom_lab_details == 'Both' else 1,
                    # 'product_uom': self.env['uom.uom'].search(
                    #     [('name', '=', ('Pair' if prd.pair_each == 'pair' else 'Each'))], limit=1).id,
                    'price_unit': 0,
                    'prescription_id': self.prescription_id.id if self.order_type_name == "Lenses Only" else None,
                    'lab_details_id': self.id,
                    'insurance_id': self.insurance_id.id,
                    'authorization_id': self.authorization_id.id if self.order_type_name != "Complete Pair" else None,
                    'dest_address_id': self.ship_to.id,
                    'co_pay': 0 if self.post_sale_type == "Warranty" else copay,
                    'pt_resp': 0 if self.post_sale_type == "Warranty" else pt_resp,
                    'return_location': self.lens_products_return_location.id,
                    'post_sale_order_line_id': self.lens_products_post_sale_order_line_id.id,
                }
                if self.model_number:
                    vals['name'] = self.model_number
                if self.is_lens or self.post_sale_type == "Warranty":
                    vals['price_unit'] = 0
                if self.post_sale_type == "Remake":
                    vals['price_unit'] = 0
                    vals['pt_total'] = 0
                order_line = self.env['sale.order.line'].create(vals)
                for hcpcs_id in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Lens'):
                    hcpcs_id.order_line_id = order_line.id
                vals.clear()
            vals = {
                'order_id': sale_order_id.id,
                'product_id': prd.id,
                'name': prd.name,
                'product_uom_qty': product_uom_qty,
                # 'product_uom_qty': 2 if self.uom_lab_details == 'Both' else 1,
                # 'product_uom': self.env['uom.uom'].search(
                #     [('name', '=', ('Pair' if prd.pair_each == 'pair' else 'Each'))], limit=1).id,
                # 'price_unit': prd.list_price * 2 if self.uom_lab_details == 'Pair' else prd.list_price,
                'prescription_id': self.prescription_id.id if self.order_type_name == "Lenses Only" else None,
                'lab_details_id': self.id,
                'insurance_id': self.insurance_id.id,
                'authorization_id': self.authorization_id.id if self.order_type_name != "Complete Pair" else None,
                'dest_address_id': self.ship_to.id,
                'co_pay': 0 if self.post_sale_type == "Warranty" else copay,
                'pt_resp': 0 if self.post_sale_type == "Warranty" else pt_resp,
                'return_location': self.lens_products_return_location.id,
                'post_sale_order_line_id': self.lens_products_post_sale_order_line_id.id,
            }
            if self.is_lens or self.post_sale_type == "Warranty":
                vals['price_unit'] = 0
            if self.post_sale_type == "Remake":
                vals['price_unit'] = 0
                vals['pt_total'] = 0
            order_line = self.env['sale.order.line'].create(vals)
            for hcpcs_id in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Lens'):
                hcpcs_id.order_line_id = order_line.id
        vals.clear()
        if self.lenstreatment_products:
            for rec in self.lenstreatment_products:
                # prd = self.env['product.product'].search([('product_tmpl_id', '=', rec.id)], order='id asc')[0]
                prd = rec
                copay = float()
                pt_resp = float()

                for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Lens Treatment'):
                    if hcpcs.product_id.id == prd.id:
                        copay = hcpcs.copay
                        pt_resp = hcpcs.pt_resp

                        lenstreatment_products_id = self.lenstreatment_products_ids.filtered(lambda x: x.lenstreatment_products_id.id == rec.id)
                        product_uom_qty = lens_product_uom_qty
                        if (lenstreatment_products_id.id and self.post_sale_type != 'Warranty') or \
                                (self.post_sale_type == 'Remake' and not lenstreatment_products_id.return_location.id):
                            product_uom_qty = -1

                        vals = {
                            'order_id': sale_order_id.id,
                            'product_id': prd.id,
                            'name': prd.name,
                            'lab_details_id': self.id,
                            'product_uom_qty': product_uom_qty,
                            'dest_address_id': self.ship_to.id,
                            'insurance_id': self.insurance_id.id,
                            'co_pay': copay,
                            'pt_resp': pt_resp,
                            'return_location': lenstreatment_products_id.return_location.id,
                            'post_sale_order_line_id': lenstreatment_products_id.sale_order_line_id.id,
                            'price_unit': prd.list_price / 2,
                        }
                        if lenstreatment_products_id.id or self.post_sale_type == "Warranty":
                            vals['price_unit'] = 0
                        if self.post_sale_type == "Remake":
                            vals['price_unit'] = 0
                            vals['pt_total'] = 0
                        # if self.env.context.get('lenstreatment_products_return_location', False):
                        #     if str(rec.id) in self.env.context.get('lenstreatment_products_return_location'):
                        #         vals['return_location'] = self.env.context.get('lenstreatment_products_return_location')[str(rec.id)][0]
                        #         vals['post_sale_order_line_id'] = self.env.context.get('lenstreatment_products_return_location')[str(rec.id)][1]
                        order_line = self.env['sale.order.line'].create(vals)
                        for hcpcs_id in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Lens Treatment'):
                            if hcpcs.product_id.id == prd.id:
                                hcpcs_id.order_line_id = order_line.id
                        vals.clear()
        if self.miscellaneous_products:
            flag = True
            miscellaneous_products_ids = []
            for rec in self.miscellaneous_products:
                # prd = self.env['product.product'].search([('product_tmpl_id', '=', rec.miscellaneous_products.id)], order='id asc')[0]
                copay = float()
                pt_resp = float()

                for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Accessory' and x.id not in miscellaneous_products_ids):
                    if hcpcs.product_id.id == rec.miscellaneous_products.id:
                        miscellaneous_products_ids.append(hcpcs.id)
                        copay = hcpcs.copay
                        pt_resp = hcpcs.pt_resp
                        vals = {
                            'order_id': sale_order_id.id,
                            'product_id': rec.miscellaneous_products.id,
                            'name': rec.miscellaneous_products.name,
                            'product_uom_qty': rec.qty,
                            'lab_details_id': self.id,
                            'insurance_id': self.insurance_id.id,
                            'authorization_id': self.authorization_id.id if self.order_type_name == "Miscellaneous" and flag == True else None,
                            'dest_address_id': self.ship_to.id,
                            'co_pay': 0 if self.post_sale_type == "Warranty" else copay,
                            'pt_resp': 0 if self.post_sale_type == "Warranty" else pt_resp,
                            'return_location': rec.return_location.id,
                            'post_sale_order_line_id': rec.sale_order_line_id.id,
                        }
                        if self.post_sale_type == "Warranty":
                            vals['price_unit'] = 0
                        if self.post_sale_type == "Remake":
                            vals['price_unit'] = 0
                            vals['pt_total'] = 0
                        order_line = self.env['sale.order.line'].create(vals)
                        hcpcs.order_line_id = order_line.id
                flag = False
                vals.clear()
        if self.service_products:
            service_products_ids = []
            for rec in self.service_products:
                # prd = self.env['product.product'].search([('product_tmpl_id', '=', rec.service_products.id)], order='id asc')[0]
                prd = rec.service_products
                flag = True
                copay = float()
                pt_resp = float()

                for hcpcs in self.hcpcs_id.filtered(lambda x: x.categ_id.name == 'Services' and x.id not in service_products_ids):
                    if hcpcs.product_id.id == prd.id:
                        service_products_ids.append(hcpcs.id)
                        copay = hcpcs.copay
                        pt_resp = hcpcs.pt_resp

                        vals = {
                            'order_id': sale_order_id.id,
                            'product_id': prd.id,
                            'name': prd.name,
                            'product_uom_qty': rec.qty,
                            'lab_details_id': self.id,
                            'insurance_id': self.insurance_id.id,
                            'authorization_id': self.authorization_id.id if self.order_type_name == "Services" and flag == True else None,
                            'dest_address_id': self.ship_to.id,
                            'return_location': rec.return_location.id,
                            'post_sale_order_line_id': rec.sale_order_line_id.id,
                            'co_pay': copay,
                            'pt_resp': pt_resp,

                        }
                        if self.post_sale_type == "Warranty":
                            vals['price_unit'] = 0
                        if self.post_sale_type == "Remake":
                            vals['price_unit'] = 0
                            vals['pt_total'] = 0

                        order_line = self.env['sale.order.line'].create(vals)
                        hcpcs.order_line_id = order_line.id
                flag = False
        if self.env['multi.order.type.historical'].search_count([('multi_order_type_id', '=', self.id)]) == 0:
            self._onchange_order_status()
        # if self.is_post_sale:
        return {
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_id': False,
            'res_id': sale_order_id.id,
            'type': 'ir.actions.act_window',
        }

