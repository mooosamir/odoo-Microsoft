# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime
from werkzeug.exceptions import Forbidden, NotFound

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError
from odoo.osv import expression


class website_sale(WebsiteSale):
    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/frames/<int:fr>''',
        '''/shop/contact_lens/<int:cn>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
        
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, fr=None, cn=None, search='', ppg=False, specs_id=None, collection_id=None, **post):
        
        res=super(website_sale, self).shop(page, category, search, **post)
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}
        domain = self._get_search_domain(search, category, attrib_values)
        dict_filter_data = self.make_filter_dict(post)
        size_measure = False
        if 'size_measure' in post and  post.get('size_measure') == 'size_measure_1':
            domain += [('size', '<', 50)]
            size_measure = 1
        if 'size_measure' in post and  post.get('size_measure') == 'size_measure_2':
            domain += [('size', '>', 50), ('size', '<', 54)]
            size_measure = 2
        if 'size_measure' in post and  post.get('size_measure') == 'size_measure_3':
            domain += [('size', '>', 55)]
            size_measure = 3
        if dict_filter_data:
            if 'gender' in dict_filter_data and dict_filter_data.get('gender'):
                domain += [('gender_ids', 'in', dict_filter_data.get('gender'))]
            if 'collection' in dict_filter_data and dict_filter_data.get('collection'):
                domain += [('collection_id', 'in', dict_filter_data.get('collection'))]
            if 'shape' in dict_filter_data and dict_filter_data.get('shape'):
                domain += [('shap_id', 'in', dict_filter_data.get('shape'))]
            if 'color' in dict_filter_data and dict_filter_data.get('color'):
                domain += [('color_family_id', 'in', dict_filter_data.get('color'))]
            if 'material' in dict_filter_data and dict_filter_data.get('material'):
                domain += [('frame_material_id', 'in', dict_filter_data.get('material'))]
            #Contact Lens
            if 'replacement' in dict_filter_data and dict_filter_data.get('replacement'):
                domain += [('replacement_schedule_id', 'in', dict_filter_data.get('replacement'))]
            if 'wear' in dict_filter_data and dict_filter_data.get('wear'):
                domain += [('wear_period_id', 'in', dict_filter_data.get('wear'))]
        keep = QueryURL('/shop', search=search, attrib=attrib_list, order=post.get('order'))
        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        frames = False
        contact_lens = False
        if fr ==1:
            domain += [('prd_categ_name', '=', 'Frames')]
            frames = True
        if cn == 1:
            contact_lens = True
            domain += [('prd_categ_name', '=', 'Contact Lens')]
        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list
        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain, order=self._get_search_order(post))
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)
        # if not post:
        #     frames = True
        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset: offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        gender_types = request.env['spec.gender.type'].sudo().search([])
        collections = request.env['spec.collection.collection'].sudo().search([])
        materials = request.env['spec.temple.material'].sudo().search([])
        shapes = request.env['spec.shape.shape'].sudo().search([])
        colors = request.env['spec.color.family'].sudo().search([])
        #contact Lens
        wear_period = request.env['spec.contact.lens.wear.period'].sudo().search([])
        replacement_schedule = request.env['spec.contact.lens.replacement.schedule'].sudo().search([])
        #gender_types = request.env['spec.gender.type'].sudo().search([])
        #print("contact_lens",contact_lens, frames)
        res.qcontext.update({
            'gender_types': gender_types,
            'products': products,
            'replacement_schedule':replacement_schedule,
            'wear_period':wear_period,
            'frames': frames,
            'contact_lens':contact_lens,
            'genders':dict_filter_data.get('gender') if dict_filter_data.get('gender') else [],
            'collections_types': collections,
            'collection_ids': dict_filter_data.get('collection') if dict_filter_data.get('collection') else [],
            'shapes': shapes,
            'size': post.get('size') if post.get('size') else 0,
            'materials': materials,
            'material_ids': dict_filter_data.get('material') if dict_filter_data.get('material') else [],
            'shapes_ids': dict_filter_data.get('shape') if dict_filter_data.get('shape') else [],
            'colors': colors,
            'size_measure': size_measure,
            'colors_ids': dict_filter_data.get('color') if dict_filter_data.get('color') else [],
            'wear_ids': dict_filter_data.get('wear') if dict_filter_data.get('wear') else [],
            'replacement_ids': dict_filter_data.get('replacement') if dict_filter_data.get('replacement') else [],
            'bins': TableCompute().process(products),

            })
        return res

    def make_filter_dict(self, data):
        vals = {}
        #gender_1=1-Male&collection_1=1-Sun&shape_1=1-Rectangle&color_1=1-RED&size_measure=size_measure_1&material_1=1-Metal
        #Remove underscore from key
        lst = ['gender', 'collection', 'shape', 'color', 'material','replacement','wear','manufacturer']
        for k in data:
            if k:
                d = k.split('_')
                if len(d) > 1:
                    if d[0] in lst:
                        if d[0] not in vals:
                            vals[d[0]] = [int(d[1])]
                        else:
                            vals[d[0]].append(int(d[1]))
        return vals