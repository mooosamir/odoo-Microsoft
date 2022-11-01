from odoo import api, fields, models, _
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _has_promotion_lines(self):
        for res in self:
            if len(res.order_line.filtered(lambda x: x.product_id.name == 'Promotion')):
                self.has_promotion_lines = 1
            else:
                self.has_promotion_lines = 0

    has_promotion_lines = fields.Boolean(compute='_has_promotion_lines')

    def recompute_coupon_lines(self):
        for rec in self:
            return {
                'type': 'ir.actions.client',
                'target': 'new',
                'tag': 'apply_promotion',
                'context': {'id': self.id}

            }

    def apply_promotion(self, id):
        # send data

        promotions = self.env['promotion.form'].search(
            ['|', ('end_date', '>=', fields.Datetime.now()), ('end_date', '=', False)])
        so = self.env['sale.order'].browse(int(id))
        promos = {}
        order_type = {}
        list_of_order_types = {}
        counter = 0

        for a in so.order_line:
            if a.lab_details_id.id not in list_of_order_types:
                list_of_order_types[a.lab_details_id.id] = so.order_line.filtered(
                    lambda x: x.lab_details_id.id == a.lab_details_id.id and x.product_id.name == "Promotion")

        for order_line in so.order_line:
            order_line.sequence = counter
            counter += 1
            if order_line.lab_details_id.id not in order_type:
                order_type[order_line.lab_details_id.id] = {}
                order_type[order_line.lab_details_id.id]['name'] = order_line.name
                order_type[order_line.lab_details_id.id]['id'] = order_line.lab_details_id.id
                order_type[order_line.lab_details_id.id]['category'] = {}
            else:
                if order_line.product_id.product_tmpl_id.categ_id.name in order_type[order_line.lab_details_id.id]['category']:
                    order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                        'quantity'] += order_line.product_uom_qty
                    order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                        'total_category_amount'] += order_line.price_subtotal

                    if order_line.product_id.product_tmpl_id.categ_id.name == 'Accessory':
                        if order_line.product_id.acc_category_id.name not in \
                                order_type[order_line.lab_details_id.id]['category'][
                                    order_line.product_id.product_tmpl_id.categ_id.name]['selection']['acc_category_id']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['acc_category_id'][
                                order_line.product_id.acc_category_id.name] = {'qty': order_line.product_uom_qty,
                                                                               'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['acc_category_id'][
                                order_line.product_id.acc_category_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['acc_category_id'][
                                order_line.product_id.acc_category_id.name][
                                'total_sub_category_amount'] += order_line.price_subtotal
                        if order_line.product_id.accessory_brand_id.name not in \
                                order_type[order_line.lab_details_id.id]['category'][
                                    order_line.product_id.product_tmpl_id.categ_id.name]['selection']['accessory_brand_id']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['accessory_brand_id'][
                                order_line.product_id.accessory_brand_id.name] = {'qty': order_line.product_uom_qty,
                                                                                  'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['accessory_brand_id'][
                                order_line.product_id.accessory_brand_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['accessory_brand_id'][
                                order_line.product_id.accessory_brand_id.name][
                                'total_sub_category_amount'] += order_line.price_subtotal
                        if order_line.product_id.name not in order_type[order_line.lab_details_id.id]['category'][
                            order_line.product_id.product_tmpl_id.categ_id.name]['selection']['accessory_header_name']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['accessory_header_name'][
                                order_line.product_id.name] = {'qty': order_line.product_uom_qty,
                                                               'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['accessory_header_name'][
                                order_line.product_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['accessory_header_name'][
                                order_line.product_id.name]['total_sub_category_amount'] += order_line.price_subtotal
                    elif order_line.product_id.product_tmpl_id.categ_id.name == 'services':
                        if order_line.product_id.name not in order_type[order_line.lab_details_id.id]['category'][
                            order_line.product_id.product_tmpl_id.categ_id.name]['selection']['name']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['name'][order_line.product_id.name] = {'qty': order_line.product_uom_qty,
                                                                                    'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['name'][order_line.product_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['name'][order_line.product_id.name][
                                'total_sub_category_amount'] += order_line.price_subtotal
                        if order_line.product_id.ser_pro_code_id.name not in \
                                order_type[order_line.lab_details_id.id]['category'][
                                    order_line.product_id.product_tmpl_id.categ_id.name]['selection']['ser_pro_code_id']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['ser_pro_code_id'][
                                order_line.product_id.ser_pro_code_id.name] = {'qty': order_line.product_uom_qty,
                                                                               'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['ser_pro_code_id'][
                                order_line.product_id.ser_pro_code_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['ser_pro_code_id'][
                                order_line.product_id.ser_pro_code_id.name][
                                'total_sub_category_amount'] += order_line.price_subtotal
                    elif order_line.product_id.product_tmpl_id.categ_id.name == 'contact_lens':
                        if order_line.product_id.replacement_schedule_id.name not in \
                                order_type[order_line.lab_details_id.id]['category'][
                                    order_line.product_id.product_tmpl_id.categ_id.name]['selection']['replacement_schedule_id']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['replacement_schedule_id'][
                                order_line.product_id.replacement_schedule_id.name] = {
                                'qty': order_line.product_uom_qty,
                                'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['replacement_schedule_id'][
                                order_line.product_id.replacement_schedule_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['replacement_schedule_id'][
                                order_line.product_id.replacement_schedule_id.name][
                                'total_sub_category_amount'] += order_line.price_subtotal
                        if order_line.product_id.name not in order_type[order_line.lab_details_id.id]['category'][
                            order_line.product_id.product_tmpl_id.categ_id.name]['selection']['name']:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['name'][order_line.product_id.name] = {'qty': order_line.product_uom_qty,
                                                                                    'total_sub_category_amount': order_line.price_subtotal}
                        else:
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['name'][order_line.product_id.name]['qty'] += order_line.product_uom_qty
                            order_type[order_line.lab_details_id.id]['category'][
                                order_line.product_id.product_tmpl_id.categ_id.name][
                                'selection']['name'][order_line.product_id.name][
                                'total_sub_category_amount'] += order_line.price_subtotal
                    else:
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'order_lines'].append(order_line)

                else:
                    order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name] = {}
                    order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                        'quantity'] = order_line.product_uom_qty
                    order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                        'total_category_amount'] = order_line.price_subtotal
                    if order_line.product_id.product_tmpl_id.categ_id.name == 'Accessory':
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection'] = {'acc_category_id': {}, 'accessory_brand_id': {},
                                            'accessory_header_name': {}}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['acc_category_id'][order_line.product_id.acc_category_id.name] = {
                            'qty': order_line.product_uom_qty, 'total_sub_category_amount': order_line.price_subtotal}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['accessory_brand_id'][
                            order_line.product_id.accessory_brand_id.name] = {'qty': order_line.product_uom_qty,
                                                                              'total_sub_category_amount': order_line.price_subtotal}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['accessory_header_name'][
                            order_line.product_id.name] = {'qty': order_line.product_uom_qty,
                                                           'total_sub_category_amount': order_line.price_subtotal}
                    elif order_line.product_id.product_tmpl_id.categ_id.name == 'services':
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection'] = {'name': {}, 'ser_pro_code_id': {}}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['name'][order_line.product_id.name] = {'qty': order_line.product_uom_qty,
                                                                                'total_sub_category_amount': order_line.price_subtotal}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['ser_pro_code_id'][order_line.product_id.ser_pro_code_id.name] = {
                            'qty': order_line.product_uom_qty, 'total_sub_category_amount': order_line.price_subtotal}
                    elif order_line.product_id.product_tmpl_id.categ_id.name == 'contact_lens':
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection'] = {'replacement_schedule_id': {}, 'name': {}}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['replacement_schedule_id'][
                            order_line.product_id.replacement_schedule_id.name] = {'qty': order_line.product_uom_qty,
                                                                                   'total_sub_category_amount': order_line.price_subtotal}
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'selection']['name'][order_line.product_id.name] = {'qty': order_line.product_uom_qty,
                                                                                'total_sub_category_amount': order_line.price_subtotal}
                    else:
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'order_lines'] = []
                        order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                            'order_lines'].append(order_line)
                    # order_type[order_line.lab_details_id.id]['category'][order_line.product_id.product_tmpl_id.categ_id.name][
                    #     'selection']['1'].append({})

            # if a.lab_details_id.id not in b:
            #     b[a.lab_details_id.id] = so.order_line.filtered(
            #         lambda x: x.lab_details_id.id == a.lab_details_id.id
            #                   and x.product_id.name != "Promotion")

        for promo in promotions:
            if promo.promotion_type == 'order_amount_discount':
                for ot in order_type:
                    amount_total = float()
                    discounted_amount = float()

                    if order_type[ot]['name'] not in promos:
                        promos[order_type[ot]['name']] = {'promotions': [], 'id': order_type[ot]['id'], }

                    for category in order_type[ot]['category'].values():
                        amount_total += category['total_category_amount']

                    for j in promo.order_amount_discount_id:
                        if not j.max_amount and not j.min_amount:
                            if amount_total >= 0:
                                if j.type == 'amount':
                                    discounted_amount += j.discount
                                elif j.type == 'percent':
                                    percent_amount = amount_total * j.discount / 100
                                    discounted_amount += percent_amount

                                promos[order_type[ot]['name']]['promotions'].append(
                                    {'promo_name': promo.promotion_name,
                                     'discounted_amount': discounted_amount,
                                     'promo_id': promo.id})
                        elif not j.max_amount:
                            if amount_total >= float(j.min_amount):
                                if j.type == 'amount':
                                    discounted_amount += j.discount
                                elif j.type == 'percent':
                                    percent_amount = amount_total * j.discount / 100
                                    discounted_amount += percent_amount

                                promos[order_type[ot]['name']]['promotions'].append(
                                    {'promo_name': promo.promotion_name,
                                     'discounted_amount': discounted_amount,
                                     'promo_id': promo.id})
                        elif not j.min_amount:
                            if amount_total >= 0 and amount_total <= float(j.max_amount):

                                if j.type == 'amount':
                                    discounted_amount += j.discount
                                elif j.type == 'percent':
                                    percent_amount = amount_total * j.discount / 100
                                    discounted_amount += percent_amount

                                promos[order_type[ot]['name']]['promotions'].append(
                                    {'promo_name': promo.promotion_name,
                                     'discounted_amount': discounted_amount,
                                     'promo_id': promo.id})
                        else:
                            if amount_total >= float(j.min_amount) and amount_total <= float(j.max_amount):

                                if j.type == 'amount':
                                    discounted_amount += j.discount
                                elif j.type == 'percent':
                                    percent_amount = amount_total * j.discount / 100
                                    discounted_amount += percent_amount

                                promos[order_type[ot]['name']]['promotions'].append(
                                    {'promo_name': promo.promotion_name,
                                     'discounted_amount': discounted_amount,
                                     'promo_id': promo.id})
            elif promo.promotion_type == 'category_discount':
                for ot in order_type:
                    discounted_amount_cd = float()
                    sale_order_match_cd = []
                    if order_type[ot]['name'] not in promos:
                        promos[order_type[ot]['name']] = {'promotions': [], 'id': order_type[ot]['id'], }

                    for j in promo.category_discount_id:
                        total_qty = int()
                        total_amount = int()
                        if not j.max_retail and not j.min_retail:
                            for category in order_type[ot]['category']:
                                if int(order_type[ot]['category'][category]['quantity']) == int(
                                        j.quantity) and category == j.inventory_category and \
                                        order_type[ot]['category'][category]['total_category_amount'] >= 0:
                                    sale_order_match_cd.append(True)
                                    if j.discount != 0:
                                        if j.discount_type == 'amount':
                                            discounted_amount_cd += j.discount
                                        elif j.discount_type == 'percent':
                                            percent_amount = order_type[ot]['category'][category][
                                                                 'total_category_amount'] * j.discount / 100
                                            discounted_amount_cd += percent_amount
                                        break
                        elif not j.max_retail:
                            for category in order_type[ot]['category']:
                                if int(order_type[ot]['category'][category]['quantity']) == int(
                                        j.quantity) and category == j.inventory_category and \
                                        order_type[ot]['category'][category]['total_category_amount'] >= float(
                                    j.min_retail):
                                    sale_order_match_cd.append(True)
                                    if j.discount != 0:
                                        if j.discount_type == 'amount':
                                            discounted_amount_cd += j.discount
                                        elif j.discount_type == 'percent':
                                            percent_amount = order_type[ot]['category'][category][
                                                                 'total_category_amount'] * j.discount / 100
                                            discounted_amount_cd += percent_amount
                                        break
                        elif not j.min_retail:
                            for category in order_type[ot]['category']:
                                if int(order_type[ot]['category'][category]['quantity']) == int(
                                        j.quantity) and category == j.inventory_category and \
                                        order_type[ot]['category'][category]['total_category_amount'] >= 0 and category[
                                    'total_category_amount'] <= float(
                                    j.max_retail):
                                    sale_order_match_cd.append(True)
                                    if j.discount != 0:
                                        if j.discount_type == 'amount':
                                            discounted_amount_cd += j.discount
                                        elif j.discount_type == 'percent':
                                            percent_amount = order_type[ot]['category'][category][
                                                                 'total_category_amount'] * j.discount / 100
                                            discounted_amount_cd += percent_amount
                                        break
                        else:
                            for category in order_type[ot]['category']:
                                if int(order_type[ot]['category'][category]['quantity']) == int(
                                        j.quantity) and category == j.inventory_category and \
                                        order_type[ot]['category'][category]['total_category_amount'] >= float(
                                    j.min_retail) and order_type[ot]['category'][category][
                                    'total_category_amount'] <= float(
                                    j.max_retail):
                                    sale_order_match_cd.append(True)
                                    if j.discount != 0:
                                        if j.discount_type == 'amount':
                                            discounted_amount_cd += j.discount
                                        elif j.discount_type == 'percent':
                                            percent_amount = order_type[ot]['category'][category][
                                                                 'total_category_amount'] * j.discount / 100
                                            discounted_amount_cd += percent_amount
                                        break

                        if len(sale_order_match_cd) == len(promo.category_discount_id):
                            promos[order_type[ot]['name']]['promotions'].append(
                                {'promo_name': promo.promotion_name,
                                 'discounted_amount': discounted_amount_cd,
                                 'promo_id': promo.id}
                            )
            elif promo.promotion_type == 'item_discount':
                for ot in order_type:
                    discounted_amount_id = float()
                    sale_order_match_id = []
                    if order_type[ot]['name'] not in promos:
                        promos[order_type[ot]['name']] = {'promotions': [], 'id': order_type[ot]['id'], }

                    item_discount_ids = {}
                    for item_discount in promo.item_discount_id:
                        key = item_discount.inventory_category.split("__")[0]
                        if key not in item_discount_ids:
                            item_discount_ids[key] = {}
                            item_discount_ids[key]["category"] = key
                            item_discount_ids[key]["max_retail"] = float(item_discount.max_retail)
                            item_discount_ids[key]["min_retail"] = float(item_discount.min_retail)
                            item_discount_ids[key]["quantity"] = int(item_discount.quantity)
                            item_discount_ids[key]["selection"] = []
                            item_discount_ids[key]["selection"].append(
                                {"compute_selection": item_discount.compute_selection.split(", "),
                                 "sub_category": item_discount.inventory_category.split("__")[1],
                                 "discount": float(item_discount.discount),
                                 "discount_type": item_discount.discount_type,
                                 })
                        else:
                            # item_discount_id[key]["selection"].append(buyx_gety)
                            item_discount_ids[key]["selection"].append(
                                {"compute_selection": item_discount.compute_selection.split(", "),
                                 "sub_category": item_discount.inventory_category.split("__")[1],
                                 "discount": float(item_discount.discount),
                                 "discount_type": item_discount.discount_type,
                                 })
                            item_discount_ids[key]["max_retail"] += float(item_discount.max_retail)
                            item_discount_ids[key]["min_retail"] += float(item_discount.min_retail)

                    for item_discount in item_discount_ids.values():
                        for item_discount_line in item_discount['selection']:
                            check = False
                            total_qty = int()
                            total_amount = int()
                            if not item_discount['max_retail'] and not item_discount['min_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0:
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[
                                                                item_discount_line['sub_category']].name in \
                                                            item_discount_line['compute_selection'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0:
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break

                                            except:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0:
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[
                                                                item_discount_line['sub_category']] in \
                                                            item_discount_line[
                                                                'compute_selection'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0:
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if item_discount_line['sub_category'] in order_type[ot]['category'][category]['selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                item_discount_line['sub_category']]:
                                                sub_cat = sub_category

                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:

                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and order_type[ot]['category'][category]['total_category_amount'] >= 0:
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['qty']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            sub_cat in \
                                                            item_discount_line['compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] >= 0:
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                            elif not item_discount['max_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= float(
                                                        item_discount['min_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[item_discount_line[
                                                                'sub_category']].name in item_discount_line[
                                                        'compute_selection'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= float(
                                                        item_discount['min_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                            except:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= float(
                                                        item_discount['min_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[
                                                                item_discount_line['sub_category']] in item_discount_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= float(
                                                        item_discount['min_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if item_discount_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                item_discount_line['sub_category']]:
                                                sub_cat = sub_category
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category]['total_category_amount'] >= float(
                                                        item_discount['min_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['qty']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            sub_cat in item_discount_line[
                                                        'compute_selection'] and order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] >= float(
                                                        item_discount['min_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                            elif not item_discount['min_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[item_discount_line[
                                                                'sub_category']].name in item_discount_line[
                                                        'compute_selection'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                            except:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[
                                                                item_discount_line['sub_category']] in item_discount_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if item_discount_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                item_discount_line['sub_category']]:
                                                sub_cat = sub_category
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category]['total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category]['total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['qty']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            sub_cat in item_discount_line[
                                                        'compute_selection'] and order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                            else:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= float(
                                                        item_discount['min_retail']) and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_line.product_id[item_discount_line[
                                                                'sub_category']].name in item_discount_line[
                                                        'compute_selection'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= float(
                                                        item_discount['min_retail']) and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                            except:
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] >= float(
                                                        item_discount['min_retail']) and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                item_discount[
                                                                    'quantity']) and category == \
                                                                item_discount['category'] and order_line.product_id[
                                                            item_discount_line[
                                                                'sub_category']] in item_discount_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            item_discount['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            item_discount['max_retail']):
                                                            sale_order_match_id.append(True)
                                                            if item_discount_line['discount'] != 0:
                                                                if item_discount_line['discount_type'] == 'amount':
                                                                    discounted_amount_id += item_discount_line[
                                                                        'discount']
                                                                elif item_discount_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                        order_type[ot]['category'][category][
                                                                            'total_category_amount'] * \
                                                                        item_discount[
                                                                            'discount'] / 100
                                                                    discounted_amount_id += percent_amount
                                                                break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if item_discount_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                item_discount_line['sub_category']]:
                                                sub_cat = sub_category
                                                if item_discount_line['compute_selection'] == [''] or not \
                                                        item_discount_line[
                                                            'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            order_type[ot]['category'][category]['total_category_amount'] >= float(
                                                        item_discount['min_retail']) and \
                                                            order_type[ot]['category'][category]['total_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['total_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['qty']) == int(
                                                            item_discount[
                                                                'quantity']) and category == \
                                                            item_discount['category'] and \
                                                            sub_cat in item_discount_line[
                                                        'compute_selection'] and float(
                                                        item_discount['min_retail']) <= \
                                                            order_type[ot]['category'][category]['selection'][
                                                                item_discount_line['sub_category']][sub_cat][
                                                                'total_sub_category_amount'] <= float(
                                                        item_discount['max_retail']):
                                                        sale_order_match_id.append(True)
                                                        if item_discount_line['discount'] != 0:
                                                            if item_discount_line['discount_type'] == 'amount':
                                                                discounted_amount_id += item_discount_line['discount']
                                                            elif item_discount_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category]['selection'][item_discount_line['sub_category']][sub_cat]['total_sub_category_amount'] * \
                                                                                 item_discount_line[
                                                                                     'discount'] / 100
                                                                discounted_amount_id += percent_amount
                                                            break


                            if len(sale_order_match_id) == len(promo.item_discount_id):
                                promos[order_type[ot]['name']]['promotions'].append(
                                    {'promo_name': promo.promotion_name,
                                     'discounted_amount': discounted_amount_id,
                                     'promo_id': promo.id}
                                )
            elif promo.promotion_type == 'contact_lens_annual_supply':
                for ot in order_type:
                    discounted_amount_cl = float()
                    check = []
                    if order_type[ot]['name'] not in promos:
                        promos[order_type[ot]['name']] = {'promotions': [], 'id': order_type[ot]['id'], }

                    contact_lens_annual_supply_ids = {}
                    for contact_lens in promo.contact_lens_id:
                        key = contact_lens.inventory_category.split("__")[0]
                        if key not in contact_lens_annual_supply_ids:
                            contact_lens_annual_supply_ids[key] = {}
                            contact_lens_annual_supply_ids[key]["category"] = key
                            contact_lens_annual_supply_ids[key]["min_quantity"] = int(contact_lens.min_quantity)
                            contact_lens_annual_supply_ids[key]["selection"] = []
                            contact_lens_annual_supply_ids[key]["selection"].append(
                                {"compute_selection": contact_lens.compute_selection.split(", "),
                                 "sub_category": contact_lens.inventory_category.split("__")[1],
                                 "discount": float(contact_lens.discount),
                                 "discount_type": contact_lens.discount_type,
                                 })
                        else:
                            # item_discount_id[key]["selection"].append(buyx_gety)
                            contact_lens_annual_supply_ids[key]["selection"].append(
                                {"compute_selection": contact_lens.compute_selection.split(", "),
                                 "sub_category": contact_lens.inventory_category.split("__")[1],
                                 "discount": float(contact_lens.discount),
                                 "discount_type": contact_lens.discount_type,
                                 })

                    for contact_lens in contact_lens_annual_supply_ids.values():
                        for contact_lens_line in contact_lens['selection']:
                            for category in order_type[ot]['category']:
                                if 'selection' in order_type[ot]['category'][category]:
                                    if contact_lens_line['sub_category'] in order_type[ot]['category'][category][
                                        'selection']:
                                        for sub_category in order_type[ot]['category'][category]['selection'][
                                            contact_lens_line['sub_category']]:
                                            sub_cat = sub_category
                                            if contact_lens_line['compute_selection'] == [''] or not \
                                                    contact_lens_line[
                                                        'compute_selection']:
                                                if int(order_type[ot]['category'][category]['quantity']) >= int(
                                                        contact_lens['min_quantity']) and category == \
                                                                contact_lens['category']:
                                                    check.append(True)
                                                    if contact_lens_line['discount'] != 0:
                                                        if contact_lens_line['discount_type'] == 'amount':
                                                            discounted_amount_cl = contact_lens_line['discount']
                                                        elif contact_lens_line['discount_type'] == 'percent':
                                                            percent_amount = order_type[ot]['category'][category]['total_category_amount'] * contact_lens_line[
                                                                'discount'] / 100
                                                            discounted_amount_cl = percent_amount
                                                        break
                                            else:
                                                if int(order_type[ot]['category'][category]['selection'][contact_lens_line['sub_category']][sub_cat]['qty']) >= int(
                                                        contact_lens['min_quantity']) and category == \
                                                                contact_lens['category'] and \
                                                                sub_cat in \
                                                                contact_lens_line['compute_selection']:
                                                    check.append(True)
                                                    if contact_lens_line['discount'] != 0:
                                                        if contact_lens_line['discount_type'] == 'amount':
                                                            discounted_amount_cl = contact_lens_line['discount']
                                                        elif contact_lens_line['discount_type'] == 'percent':
                                                            percent_amount = order_type[ot]['category'][category]['selection'][contact_lens_line['sub_category']][sub_cat]['total_sub_category_amount'] * contact_lens_line[
                                                                'discount'] / 100
                                                            discounted_amount_cl = percent_amount
                                                        break

                            if len(check) == len(promo.contact_lens_id):
                                promos[order_type[ot]['name']]['promotions'].append(
                                    {'promo_name': promo.promotion_name,
                                     'discounted_amount': discounted_amount_cl,
                                     'promo_id': promo.id}
                                )
            elif promo.promotion_type == 'buy_x_get_y':
                buy_x_final = []
                get_y_final = []

                buy_x_final = []
                get_y_final = []

                for ot in order_type:
                    sale_order_match = []
                    sale_order_match2 = []
                    discounted_amount_xy = float()

                    if order_type[ot]['name'] not in promos:
                        promos[order_type[ot]['name']] = {'promotions': [], 'id': order_type[ot]['id'], }

                    buyx_ids = {}
                    for buy_x in promo.buyx_gety_id:
                        key = buy_x.inventory_category.split("__")[0]
                        if key not in buyx_ids:
                            buyx_ids[key] = {}
                            buyx_ids[key]["category"] = key
                            buyx_ids[key]["max_retail"] = float(buy_x.max_retail)
                            buyx_ids[key]["min_retail"] = float(buy_x.min_retail)
                            buyx_ids[key]["quantity"] = int(buy_x.quantity)
                            buyx_ids[key]["selection"] = []
                            buyx_ids[key]["selection"].append(
                                {"compute_selection": buy_x.compute_selection.split(", "),
                                 "sub_category": buy_x.inventory_category.split("__")[1],
                                 })
                        else:
                            # item_discount_id[key]["selection"].append(buyx_gety)
                            buyx_ids[key]["selection"].append(
                                {"compute_selection": buy_x.compute_selection.split(", "),
                                 "sub_category": buy_x.inventory_category.split("__")[1],
                                 })
                            buyx_ids[key]["max_retail"] += float(buy_x.max_retail)
                            buyx_ids[key]["min_retail"] += float(buy_x.min_retail)

                    for buy_x in buyx_ids.values():
                        for buy_x_line in buy_x['selection']:
                            total_qty = int()

                            if not buy_x['max_retail'] and not buy_x['min_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']].name in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                            except:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']] in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if buy_x_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                buy_x_line['sub_category']]:
                                                sub_cat = sub_category
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            buy_x[
                                                                'quantity']) and category == \
                                                            buy_x['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= 0:
                                                        sale_order_match.append(True)
                                                        break
                                                        # if j.discount != 0:
                                                        #     demo_promos.append(
                                                        #         {'promo_name': promo.promotion_name,
                                                        #          'order_lines_ids': [xAndY[i][v]],
                                                        #          'promo_id': promo.id})
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                        buy_x_line['sub_category']][
                                                        sub_cat]['qty']) == int(buy_x[
                                                    'quantity']) and category == \
                                                            buy_x['category'] and \
                                                            sub_cat in buy_x_line[
                                                    'compute_selection'] and order_type[ot]['category'][category]['selection'][
                                                        buy_x_line['sub_category']][
                                                    sub_cat]['total_sub_category_amount'] >= 0: \
                                                        sale_order_match.append(True)
                                                break
                                                # if j.discount != 0:
                                                #     demo_promos.append(
                                                #         {'promo_name': promo.promotion_name,
                                                #          'order_lines_ids': [xAndY[i][v]],
                                                #          'promo_id': promo.id})
                            elif not buy_x['max_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x[
                                                                'min_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x[
                                                                'min_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']].name in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                            except:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x[
                                                                'min_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x[
                                                                'min_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']] in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if buy_x_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                buy_x_line['sub_category']]:
                                                sub_cat = sub_category
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            buy_x[
                                                                'quantity']) and category == \
                                                            buy_x['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= float(
                                                        buy_x['min_retail']):
                                                        sale_order_match.append(True)
                                                        break
                                                        # if j.discount != 0:
                                                        #     demo_promos.append(
                                                        #         {'promo_name': promo.promotion_name,
                                                        #          'order_lines_ids': [xAndY[i][v]],
                                                        #          'promo_id': promo.id})
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               buy_x_line['sub_category']][
                                                               sub_cat]['qty']) == int(buy_x[
                                                                                           'quantity']) and category == \
                                                            buy_x['category'] and \
                                                            sub_cat in buy_x_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                buy_x_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] >= float(
                                                        buy_x['min_retail']):
                                                        sale_order_match.append(True)
                                                        break
                                                        # if j.discount != 0:
                                                        #     demo_promos.append(
                                                        #         {'promo_name': promo.promotion_name,
                                                        #          'order_lines_ids': [xAndY[i][v]],
                                                        #          'promo_id': promo.id})
                            elif not buy_x['min_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':

                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x[
                                                                'max_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':

                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x[
                                                                'max_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']].name in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                            except:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x[
                                                                'max_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x[
                                                                'max_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']] in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if buy_x_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                buy_x_line['sub_category']]:
                                                sub_cat = sub_category
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            buy_x[
                                                                'quantity']) and category == \
                                                            buy_x['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        buy_x['max_retail']):
                                                        sale_order_match.append(True)
                                                        break
                                                        # if j.discount != 0:
                                                        #     demo_promos.append(
                                                        #         {'promo_name': promo.promotion_name,
                                                        #          'order_lines_ids': [xAndY[i][v]],
                                                        #          'promo_id': promo.id})
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                        buy_x_line['sub_category']][sub_cat][
                                                        'qty']) == int(buy_x[
                                                                           'quantity']) and category == \
                                                           buy_x['category'] and \
                                                           sub_cat in buy_x_line[
                                                               'compute_selection'] and order_type[ot]['category'][category]['selection'][
                                                               buy_x_line['sub_category']][sub_cat][
                                                               'total_sub_category_amount'] >= 0 and \
                                                           order_type[ot]['category'][category]['selection'][
                                                               buy_x_line['sub_category']][sub_cat][
                                                               'total_sub_category_amount'] <= float(
                                                        buy_x['max_retail']):
                                                        sale_order_match.append(True)
                                                    break
                                                    # if j.discount != 0:
                                                    #     demo_promos.append(
                                                    #         {'promo_name': promo.promotion_name,
                                                    #          'order_lines_ids': [xAndY[i][v]],
                                                    #          'promo_id': promo.id})
                            else:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']].name in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                            except:
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x[
                                                                'max_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                else:
                                                    if buy_x_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x[
                                                                'max_retail']) and order_line.product_id.is_sunclass == True:
                                                            sale_order_match.append(True)
                                                            break
                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                buy_x[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                buy_x['category'] and \
                                                                order_line.product_id[
                                                                    buy_x_line['sub_category']] in buy_x_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            buy_x['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            buy_x['max_retail']):
                                                            sale_order_match.append(True)
                                                            break

                                                            # if j.discount != 0:
                                                            #     demo_promos.append(
                                                            #         {'promo_name': promo.promotion_name,
                                                            #          'order_lines_ids': [xAndY[i][v]],
                                                            #          'promo_id': promo.id})
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if buy_x_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                buy_x_line['sub_category']]:
                                                sub_cat = sub_category
                                                if buy_x_line['compute_selection'] == [''] or not buy_x_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            buy_x[
                                                                'quantity']) and category == \
                                                            buy_x['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= float(
                                                        buy_x['min_retail']) and order_type[ot]['category'][category][
                                                        'total_category_amount'] <= float(
                                                        buy_x['max_retail']):
                                                        sale_order_match.append(True)
                                                        break
                                                        # if j.discount != 0:
                                                        #     demo_promos.append(
                                                        #         {'promo_name': promo.promotion_name,
                                                        #          'order_lines_ids': [xAndY[i][v]],
                                                        #          'promo_id': promo.id})
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               buy_x_line['sub_category']][sub_cat][
                                                               'qty']) == int(buy_x[
                                                                                  'quantity']) and category == \
                                                            buy_x['category'] and \
                                                            sub_cat in buy_x_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                buy_x_line['sub_category']][sub_cat][
                                                                'total_sub_category_amount'] >= float(
                                                        buy_x['min_retail']) and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                buy_x_line['sub_category']][sub_cat][
                                                                'total_sub_category_amount'] <= float(
                                                        buy_x['max_retail']):
                                                        sale_order_match.append(True)
                                                        break
                                                        # if j.discount != 0:
                                                        #     demo_promos.append(
                                                        #         {'promo_name': promo.promotion_name,
                                                        #          'order_lines_ids': [xAndY[i][v]],
                                                        #          'promo_id': promo.id})

                    if len(sale_order_match) == len(promo.buyx_gety_id):
                        buy_x_final.append(order_type[ot]['id'])
                    else:
                        sale_order_match = []
                        # if not check:
                        #     demo_promos = []
                        #     break

                    gety_ids = {}
                    for get_y in promo.buyx_gety2_id:
                        key = get_y.inventory_category.split("__")[0]
                        if key not in gety_ids:
                            gety_ids[key] = {}
                            gety_ids[key]["category"] = key
                            gety_ids[key]["max_retail"] = float(get_y.max_retail)
                            gety_ids[key]["min_retail"] = float(get_y.min_retail)
                            gety_ids[key]["quantity"] = int(get_y.quantity)
                            gety_ids[key]["selection"] = []
                            gety_ids[key]["selection"].append(
                                {"compute_selection": get_y.compute_selection.split(", "),
                                 "sub_category": get_y.inventory_category.split("__")[1],
                                 "discount": float(get_y.discount),
                                 "discount_type": get_y.discount_type,
                                 })
                        else:
                            # item_discount_id[key]["selection"].append(buyx_gety)
                            gety_ids[key]["selection"].append(
                                {"compute_selection": get_y.compute_selection.split(", "),
                                 "sub_category": get_y.inventory_category.split("__")[1],
                                 "discount": float(get_y.discount),
                                 "discount_type": get_y.discount_type,
                                 })
                            gety_ids[key]["max_retail"] += float(get_y.max_retail)
                            gety_ids[key]["min_retail"] += float(get_y.max_retail)

                    for get_y in gety_ids.values():
                        for get_y_line in get_y['selection']:
                            total_qty = int()
                            if not get_y['max_retail'] and not get_y['min_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']].name in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                            except:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']] in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if get_y_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                get_y_line['sub_category']]:
                                                sub_cat = sub_category
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            get_y[
                                                                'quantity']) and category == \
                                                            get_y['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= 0:
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               get_y_line['sub_category']][
                                                               sub_cat]['qty']) == int(get_y[
                                                                                           'quantity']) and category == \
                                                            get_y['category'] and \
                                                            sub_cat in get_y_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                get_y_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] >= 0:
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    get_y_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] * \
                                                                get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                            elif not get_y['max_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']].name in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                            except:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']] in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if get_y_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                get_y_line['sub_category']]:
                                                sub_cat = sub_category
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            get_y[
                                                                'quantity']) and category == \
                                                            get_y['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= float(
                                                        get_y['min_retail']):
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               get_y_line['sub_category']][
                                                               sub_cat]['qty']) == int(get_y[
                                                                                           'quantity']) and category == \
                                                            get_y['category'] and \
                                                            sub_cat in get_y_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                get_y_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] >= float(
                                                        get_y['min_retail']):
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    get_y_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] * \
                                                                get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                            elif not get_y['min_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']].name in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                            except:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y[
                                                                    'category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']] in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= 0 and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if get_y_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                get_y_line['sub_category']]:
                                                sub_cat = sub_category
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            get_y[
                                                                'quantity']) and category == \
                                                            get_y['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category][
                                                                'total_category_amount'] <= float(
                                                        get_y['max_retail']):
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               get_y_line['sub_category']][
                                                               sub_cat]['qty']) == int(get_y[
                                                                                           'quantity']) and category == \
                                                            get_y['category'] and \
                                                            sub_cat in get_y_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                get_y_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] >= 0 and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                get_y_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] <= float(
                                                        get_y['max_retail']):
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    get_y_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] * \
                                                                get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                            else:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']].name in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                            except:
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                else:
                                                    if get_y_line['sub_category'] == 'is_sunclass':
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']) and order_line.product_id.is_sunclass:
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                get_y[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                get_y['category'] and \
                                                                order_line.product_id[
                                                                    get_y_line['sub_category']] in get_y_line[
                                                            'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            get_y['min_retail']) and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            get_y['max_retail']):
                                                            sale_order_match2.append(True)
                                                            if get_y_line['discount'] != 0:
                                                                if get_y_line['discount_type'] == 'amount':
                                                                    discounted_amount_xy += get_y_line['discount']
                                                                elif get_y_line['discount_type'] == 'percent':
                                                                    percent_amount = \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount'] * \
                                                                    get_y_line['discount'] / 100
                                                                    discounted_amount_xy += percent_amount
                                                                break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if get_y_line['sub_category'] in order_type[ot]['category'][category][
                                            'selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                get_y_line['sub_category']]:
                                                sub_cat = sub_category
                                                if get_y_line['compute_selection'] == [''] or not get_y_line[
                                                    'compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            get_y[
                                                                'quantity']) and category == \
                                                            get_y['category'] and order_type[ot]['category'][category][
                                                        'total_category_amount'] >= float(
                                                        get_y['min_retail']) and order_type[ot]['category'][category][
                                                        'total_category_amount'] <= float(
                                                        get_y['max_retail']):
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = order_type[ot]['category'][category][
                                                                                     'total_category_amount'] * \
                                                                                 get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               get_y_line['sub_category']][
                                                               sub_cat]['qty']) == int(get_y[
                                                                                           'quantity']) and category == \
                                                            get_y['category'] and \
                                                            sub_cat in get_y_line[
                                                        'compute_selection'] and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                get_y_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] >= float(
                                                        get_y['min_retail']) and \
                                                            order_type[ot]['category'][category]['selection'][
                                                                get_y_line['sub_category']][
                                                                sub_cat]['total_sub_category_amount'] <= float(
                                                        get_y['max_retail']):
                                                        sale_order_match2.append(True)
                                                        if get_y_line['discount'] != 0:
                                                            if get_y_line['discount_type'] == 'amount':
                                                                discounted_amount_xy += get_y_line['discount']
                                                            elif get_y_line['discount_type'] == 'percent':
                                                                percent_amount = \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    get_y_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] * \
                                                                get_y_line['discount'] / 100
                                                                discounted_amount_xy += percent_amount
                                                            break

                    if len(sale_order_match2) == len(promo.buyx_gety2_id):
                        get_y_final.append(order_type[ot]['id'])
                    else:
                        sale_order_match2 = []

                        # if not check:
                        #     demo_promos = []
                        #     break
                if len(buy_x_final) >= 1 and len(get_y_final) >= 1:
                    for get in get_y_final:
                        if len(buy_x_final) == len(get_y_final):
                            promos[order_type[get]['name']]['promotions'].append(
                                {'promo_name': promo.promotion_name,
                                 'discounted_amount': discounted_amount_xy,
                                 'promo_id': promo.id})

                # promos[contactLens[i][0].name]['promotions'].append(
            elif promo.promotion_type == 'package_discount':

                for ot in order_type:
                    amount_total = float()
                    discounted_amount_pd = float()
                    sale_order_match = []
                    seq = int()
                    if order_type[ot]['name'] not in promos:
                        promos[order_type[ot]['name']] = {'promotions': [], 'id': order_type[ot]['id'], }

                    package_discount_ids = {}
                    for package_discount in promo.package_discount_id:
                        key = package_discount.inventory_category.split("__")[0]
                        if key not in package_discount_ids:
                            package_discount_ids[key] = {}
                            package_discount_ids[key]["category"] = key
                            package_discount_ids[key]["max_retail"] = float(package_discount.max_retail)
                            package_discount_ids[key]["quantity"] = int(package_discount.quantity)
                            package_discount_ids[key]["selection"] = []
                            package_discount_ids[key]["selection"].append(
                                {"compute_selection": package_discount.compute_selection.split(", "),
                                 "sub_category": package_discount.inventory_category.split("__")[1],
                                 })
                        else:
                            # item_discount_id[key]["selection"].append(buyx_gety)
                            package_discount_ids[key]["selection"].append(
                                {"compute_selection": package_discount.compute_selection.split(", "),
                                 "sub_category": package_discount.inventory_category.split("__")[1],
                                 })
                            package_discount_ids[key]["max_retail"] += float(package_discount.max_retail)

                    for package_discount in package_discount_ids.values():
                        for package_discount_line in package_discount['selection']:
                            check = False
                            total_qty = int()
                            new_amount_total = int()
                            if not package_discount['max_retail']:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if package_discount_line['compute_selection'] == [''] or not \
                                                        package_discount_line['compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            package_discount[
                                                                'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                            package_discount['category']:
                                                        if seq != order_line.sequence:
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                        sale_order_match.append(True)
                                                        seq = order_line.sequence
                                                        break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            package_discount[
                                                                'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                            package_discount['category'] and \
                                                            order_line.product_id[
                                                                package_discount_line['sub_category']].name in \
                                                            package_discount_line['compute_selection']:
                                                        if seq != order_line.sequence:
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                        sale_order_match.append(True)
                                                        seq = order_line.sequence
                                                        break
                                            except:
                                                if package_discount_line['compute_selection'] == [''] or not \
                                                        package_discount_line['compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            package_discount[
                                                                'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                            package_discount['category']:
                                                        if seq != order_line.sequence:
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                        sale_order_match.append(True)
                                                        seq = order_line.sequence
                                                        break
                                                else:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            package_discount[
                                                                'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                            package_discount['category'] and \
                                                            order_line.product_id[
                                                                package_discount_line['sub_category']] in \
                                                            package_discount_line['compute_selection']:
                                                        if seq != order_line.sequence:
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                        sale_order_match.append(True)
                                                        seq = order_line.sequence
                                                        break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if package_discount_line['sub_category'] in \
                                                order_type[ot]['category'][category]['selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                package_discount_line['sub_category']]:
                                                sub_cat = sub_category
                                                if package_discount_line['compute_selection'] == [''] or not \
                                                        package_discount_line['compute_selection']:
                                                    if int(order_type[ot]['category'][category]['quantity']) == int(
                                                            package_discount[
                                                                'quantity']) and category == \
                                                            package_discount['category']:
                                                        if seq != order_line.sequence:
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                        sale_order_match.append(True)
                                                        seq = order_line.sequence
                                                        break
                                                else:
                                                    if int(order_type[ot]['category'][category]['selection'][
                                                               package_discount_line['sub_category']][sub_cat][
                                                               'qty']) == int(
                                                            package_discount[
                                                                'quantity']) and category == \
                                                            package_discount['category'] and \
                                                            sub_cat in \
                                                            package_discount_line['compute_selection']:
                                                        if seq != order_line.sequence:
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    package_discount_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount']
                                                        sale_order_match.append(True)
                                                        seq = order_line.sequence
                                                        break
                            else:
                                for category in order_type[ot]['category']:
                                    if 'order_lines' in order_type[ot]['category'][category]:
                                        for order_line in order_type[ot]['category'][category]['order_lines']:
                                            try:
                                                if package_discount_line['compute_selection'] == [''] or not \
                                                        package_discount_line['compute_selection']:
                                                    if promo.allow_upgrade:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and (
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']) or
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            package_discount['max_retail'])):
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                            sale_order_match.append(True)
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']):
                                                            if seq != order_line.sequence:
                                                                if promo.allow_upgrade:
                                                                    amount_total += float(
                                                                        package_discount['max_retail'])
                                                                else:
                                                                    amount_total += \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount']
                                                            sale_order_match.append(True)
                                                            seq = order_line.sequence
                                                            break
                                                else:
                                                    if promo.allow_upgrade:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and order_line.product_id[
                                                            package_discount_line['sub_category']].name in \
                                                                package_discount_line['compute_selection'] and (
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']) or
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            package_discount['max_retail'])):
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                            sale_order_match.append(True)
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and order_line.product_id[
                                                            package_discount_line['sub_category']].name in \
                                                                package_discount_line['compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']):
                                                            if seq != order_line.sequence:
                                                                if promo.allow_upgrade:
                                                                    amount_total += float(
                                                                        package_discount['max_retail'])
                                                                else:
                                                                    amount_total += \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount']
                                                            sale_order_match.append(True)
                                                            seq = order_line.sequence
                                                            break
                                            except:
                                                if package_discount_line['compute_selection'] == [''] or not \
                                                        package_discount_line['compute_selection']:
                                                    if promo.allow_upgrade:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and (
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']) or
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            package_discount['max_retail'])):
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                            sale_order_match.append(True)
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']):
                                                            if seq != order_line.sequence:
                                                                if promo.allow_upgrade:
                                                                    amount_total += float(
                                                                        package_discount['max_retail'])
                                                                else:
                                                                    amount_total += \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount']
                                                            sale_order_match.append(True)
                                                            seq = order_line.sequence
                                                            break
                                                else:
                                                    if promo.allow_upgrade:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and order_line.product_id[
                                                            package_discount_line['sub_category']] in \
                                                                package_discount_line[
                                                                    'compute_selection'] and (
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']) or
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            package_discount['max_retail'])):
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                            sale_order_match.append(True)
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and order_line.product_id.product_tmpl_id.categ_id.name == \
                                                                package_discount['category'] and order_line.product_id[
                                                            package_discount_line['sub_category']] in \
                                                                package_discount_line[
                                                                    'compute_selection'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']):
                                                            if seq != order_line.sequence:
                                                                if promo.allow_upgrade:
                                                                    amount_total += float(
                                                                        package_discount['max_retail'])
                                                                else:
                                                                    amount_total += \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount']
                                                            sale_order_match.append(True)
                                                            seq = order_line.sequence
                                                            break
                                    elif 'selection' in order_type[ot]['category'][category]:
                                        if package_discount_line['sub_category'] in \
                                                order_type[ot]['category'][category]['selection']:
                                            for sub_category in order_type[ot]['category'][category]['selection'][
                                                package_discount_line['sub_category']]:
                                                sub_cat = sub_category
                                                if package_discount_line['compute_selection'] == [''] or not \
                                                        package_discount_line['compute_selection']:
                                                    if promo.allow_upgrade:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and category == \
                                                                package_discount['category'] and (
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']) or
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] >= float(
                                                            package_discount['max_retail'])):
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += order_type[ot]['category'][category][
                                                                    'total_category_amount']
                                                            sale_order_match.append(True)
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['quantity']) == int(
                                                                package_discount[
                                                                    'quantity']) and category == \
                                                                package_discount['category'] and \
                                                                order_type[ot]['category'][category][
                                                                    'total_category_amount'] <= float(
                                                            package_discount['max_retail']):
                                                            if seq != order_line.sequence:
                                                                if promo.allow_upgrade:
                                                                    amount_total += float(
                                                                        package_discount['max_retail'])
                                                                else:
                                                                    amount_total += \
                                                                    order_type[ot]['category'][category][
                                                                        'total_category_amount']
                                                            sale_order_match.append(True)
                                                            seq = order_line.sequence
                                                            break
                                                else:
                                                    if promo.allow_upgrade:
                                                        if int(order_type[ot]['category'][category]['selection'][
                                                                   package_discount_line['sub_category']][sub_cat][
                                                                   'qty']) == int(
                                                                package_discount[
                                                                    'quantity']) and category == \
                                                                package_discount['category'] and sub_cat in \
                                                                package_discount_line['compute_selection'] and (
                                                                order_type[ot]['category'][category]['selection'][
                                                                    package_discount_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] <= float(
                                                            package_discount['max_retail']) or
                                                                order_type[ot]['category'][category]['selection'][
                                                                    package_discount_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] >= float(
                                                            package_discount['max_retail'])):
                                                            if promo.allow_upgrade:
                                                                amount_total += float(package_discount['max_retail'])
                                                            else:
                                                                amount_total += \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    package_discount_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount']
                                                            sale_order_match.append(True)
                                                            break
                                                    else:
                                                        if int(order_type[ot]['category'][category]['selection'][
                                                                   package_discount_line['sub_category']][sub_cat][
                                                                   'qty']) == int(
                                                                package_discount[
                                                                    'quantity']) and category == \
                                                                package_discount['category'] and sub_cat in \
                                                                package_discount_line['compute_selection'] and \
                                                                order_type[ot]['category'][category]['selection'][
                                                                    package_discount_line['sub_category']][sub_cat][
                                                                    'total_sub_category_amount'] <= float(
                                                            package_discount['max_retail']):
                                                            if seq != order_line.sequence:
                                                                if promo.allow_upgrade:
                                                                    amount_total += float(
                                                                        package_discount['max_retail'])
                                                                else:
                                                                    amount_total += \
                                                                    order_type[ot]['category'][category]['selection'][
                                                                        package_discount_line['sub_category']][sub_cat][
                                                                        'total_sub_category_amount']
                                                            sale_order_match.append(True)
                                                            seq = order_line.sequence
                                                            break

                    if len(promo.package_discount_id) >= 1:
                        if len(sale_order_match) == len(promo.package_discount_id):
                            discounted_amount_pd = amount_total - promo.package_amount

                            promos[order_type[ot]['name']]['promotions'].append(
                                {'promo_name': promo.promotion_name,
                                 'discounted_amount': discounted_amount_pd,
                                 'promo_id': promo.id},
                            )

        for promo in promos:
            for i, pr in enumerate(promos[promo]['promotions']):
                for ot in list_of_order_types:
                    for ol in list_of_order_types[ot]:
                        if ol.promotion_id.id == pr['promo_id']:
                            if 'ot_id' not in promos[promo]['promotions'][i]:
                                promos[promo]['promotions'][i]['ot_id'] = []
                            promos[promo]['promotions'][i]['is_applied'] = True
                            promos[promo]['promotions'][i]['ot_id'].append(ol.lab_details_id.id)

        return promos

    def apply_code(self, id, data, amount, soid, create=0):
        promotion = self.env['promotion.form'].browse(int(id))
        sol = self.env['sale.order.line'].search([('lab_details_id.id', '=', data), ('order_id', '=', int(soid))],
                                                 order='sequence desc', limit=1)
        sol_for_promo = self.env['sale.order.line'].search(
            [('lab_details_id.id', '=', int(data)), ('product_id', '=', 'Promotion'), ('order_id', '=', int(soid))], limit=1)
        if float(amount) < 0:
            amount = abs(float(amount))
        if create or not promotion.code_entry:
            product = self.env['product.product'].sudo().search([('name', '=', 'Promotion')], limit=1)
            if not product:
                product = self.env['product.template'].create({
                    'name': 'Promotion',
                })

            if sol_for_promo.id:
                return 0
            else:
                res = self.env['sale.order.line'].create({
                    'order_id': int(soid),
                    'sequence': sol.sequence,
                    'lab_details_id': int(data),
                    'product_id': product.id,
                    'name': promotion.promotion_name,
                    'pt_resp': float(amount),
                    'price_unit': float(amount),
                    'promotion_id': int(id),
                    'discount': 100,
                    'discount_amount': 100,
                })
        promo_code = {'promo_code': promotion.code_entry, 'id': id, 'soid': soid, 'data': data, 'amount': amount}

        return promo_code

    def code_applied(self, input, id, soid, data, amount):
        promotion = self.env['promotion.form'].browse(int(id))
        if promotion.code_entry_box == input:
            self.apply_code(int(id), int(data), float(amount), int(soid), 1)
            return "1"
        else:
            return "0"
