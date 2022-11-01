# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api, exceptions, http
import json
from odoo.http import request
from xml.etree import ElementTree as ET


class PatientEngagement(http.Controller):

    # @http.route(['/a/b'], type='http', auth="user", methods=['POST', 'GET'], csrf=False)
    # def fasf(self, **kw):
    #     delivery = request.env['sale.order.line'].search([])
    #     for a in delivery:
    #         a.sudo().unlink()
    #     return "OK", str(len(delivery))

    @http.route(['/contact_lens_import/xml_import'], type='http', auth="user", methods=['POST', 'GET'], csrf=False)
    def xml_import(self, series_id, product_family_id, products_id, **kw):
        series_id = int(series_id)
        product_family_id = int(product_family_id)
        products_id = int(products_id)
        if kw.get('datas', False) != 'undefined' and kw.get('datas', False):
            # try:
                try:
                    tree = ET.fromstring(kw['datas'].stream.read())
                except:
                    return json.dumps(['-1','','',''])
                UNT_NAME = {"1 Blister": "1 Blister", "Box of 2": "2 pack", 'Box of 3': '3 pack', 'Box of 5': '5 pack',
                            'Box of 6': '6 pack', 'Box of 30': '30 pack', 'Box of 90': '90 pack', 'Single': 'Single',
                            '10 Pack': '10 pack', 'Box of 12': '12 pack'}

                for records in tree:
                    units = {n.get('UNT_ID'): n.attrib for n in records.findall(".//UNITS")}
                    data = records.findall(".//SERIES")
                    for i in range(series_id, series_id + 1, 1):
                        # Reference
                        # series.append({
                        #     'SER_ID': data.attrib['SER_ID'],
                        #     'SER_NAME': data.attrib['SER_NAME'],
                        #     'STY_ID': data.attrib['STY_ID'],
                        #     'SER_DAY_PER_LENS': data.attrib['SER_DAY_PER_LENS'],
                        #     'PRODUCT_FAMILY': [{'PRF_CONVERT': m.attrib['PRF_CONVERT'],
                        #                         'PRF_BASECURVE': m.attrib['PRF_BASECURVE'],
                        #                         'PRF_DIAMETER': m.attrib['PRF_DIAMETER'],
                        #                         'PRF_ID': m.attrib['PRF_ID'],
                        #                         'PRF_REV_DIAG_IND': m.attrib['PRF_REV_DIAG_IND'],
                        #                         'PRODUCTS': [n.attrib for n in m.findall('.//PRODUCTS')],
                        #                         'UNITS_AVAILABILITY': m.findall('.//UNITS_AVAILABILITY')[0].attrib
                        #                         }
                        #                        for m in data.findall("./PRODUCT_FAMILY")]
                        # })
                        unit = data[i].findall("./PRODUCT_FAMILY/UNITS_AVAILABILITY")[0].get('UNT_ID')
                        spec_contact_lens_manufacturer = request.env['spec.contact.lens.manufacturer'].search([('code', '=', records.get('MAN_ID'))],limit=1)
                        if not spec_contact_lens_manufacturer.id:
                            spec_contact_lens_manufacturer = request.env['spec.contact.lens.manufacturer'].create({
                                'name': records.get('MAN_NAME'),
                                'code': records.get('MAN_ID')
                            })
                        uom_category_id = request.env['uom.category'].sudo().search([('name', '=', 'Contact Lens Units')])
                        if not uom_category_id.id:
                            uom_category_id = request.env['uom.category'].sudo().create({
                                'name': 'Contact Lens Units',
                            })
                        uom_id = request.env['uom.uom'].search([('name', '=ilike', UNT_NAME[units[unit]['UNT_NAME']] if units[unit]['UNT_NAME'] in UNT_NAME else units[unit]['UNT_NAME'])],limit=1)
                        if not uom_id.id:
                            uom_id = request.env['uom.uom'].create({
                                'name': UNT_NAME[units[unit]['UNT_NAME']] if units[unit]['UNT_NAME'] in UNT_NAME else units[unit]['UNT_NAME'],
                                'category_id': uom_category_id.id,
                                'uom_type': 'bigger',
                                'factor_inv': 1,
                            })
                        spec_contact_lens_replacement_schedule = request.env['spec.contact.lens.replacement.schedule'].search([('code', '=', data[i].get('SER_DAY_PER_LENS'))],limit=1)
                        if not spec_contact_lens_replacement_schedule:
                            spec_contact_lens_replacement_schedule = request.env['spec.contact.lens.replacement.schedule'].create({
                                'name': 'N/A',
                                'code': data[i].get('SER_DAY_PER_LENS'),
                            })
                        product_template = request.env['product.template'].search([('ser_id','=',data[i].get('SER_ID'))],limit=1)
                        if not product_template.id:
                            product_category_id = self.env['product.category'].search([('name', '=', 'Contact Lens')],limit=1)
                            if not product_category_id.id:
                                product_category_id = self.env['product.category'].create({
                                    'name': 'Contact Lens'
                                })
                            product_template = request.env['product.template'].with_context(disable_varients=True, create_product_product=False).create({
                                'categ_id': product_category_id.id,
                                'type': 'product',
                                'ser_id': data[i].get('SER_ID'),
                                'contact_lens_manufacturer_id': spec_contact_lens_manufacturer.id,
                                'name': data[i].get('SER_NAME'),
                                'uom_id': uom_id.id,
                                'sty_id': data[i].get('STY_ID'),
                                'replacement_schedule_id': spec_contact_lens_replacement_schedule.id,
                                'spec_product_type': 'contact_lens',
                            })

                        product_family = data[i].findall("./PRODUCT_FAMILY")
                        for j in range(product_family_id, product_family_id +1, 1):
                            product = product_family[j].findall("./PRODUCTS")
                            product_end_id = products_id + 50
                            if products_id + 50 > len(product):
                                product_end_id = len(product)
                            for k in range(products_id, product_end_id, 1):

                                product_product_id = request.env['product.product'].search([('barcode', '=', product[k].get('PRD_UPC_CODE'))])
                                if not product_product_id:
                                    cylinder = product[k].get('PRD_CYLINDER')[0:2] + '.' + product[k].get('PRD_CYLINDER')[2:] if len(product[k].get('PRD_CYLINDER')) == 4 else product[k].get('PRD_CYLINDER')[0] + '0.' + product[k].get('PRD_CYLINDER')[1:]
                                    if len(product[k].get('PRD_AXIS')) == 2 and product[k].get('PRD_AXIS') != "00":
                                        axis = "0" + product[k].get('PRD_AXIS')
                                    elif len(product[k].get('PRD_AXIS')) == 1 and product[k].get('PRD_AXIS') != "0":
                                        axis = "00" +product[k].get('PRD_AXIS')
                                    # elif product[k].get('PRD_AXIS') != "00" or product[k].get('PRD_AXIS') != "0":
                                    #     axis = None
                                    else:
                                        axis = product[k].get('PRD_AXIS')
                                    if product[k].get('PRD_POWER')[0] == '-':
                                        if len(product[k].get('PRD_POWER')) == 4 or len(product[k].get('PRD_POWER')) == 5:
                                            sphere = product[k].get('PRD_POWER')[0:len(product[k].get('PRD_POWER'))-2] + '.' + product[k].get('PRD_POWER')[len(product[k].get('PRD_POWER'))-2:]
                                        else:
                                            sphere = product[k].get('PRD_POWER')[0:len(product[k].get('PRD_POWER')) - 1] + '.' + product[k].get('PRD_POWER')[len(product[k].get('PRD_POWER')) - 1:] + '0'
                                    else:
                                        if product[k].get('PRD_POWER') == "0":
                                            sphere = "-0.00"
                                        else:
                                            if len(product[k].get('PRD_POWER')) == 3:
                                                sphere = "+" + product[k].get('PRD_POWER')[0:len(product[k].get('PRD_POWER'))-2] + "." + product[k].get('PRD_POWER')[len(product[k].get('PRD_POWER'))-2:]
                                            else:
                                                sphere = "+" + product[k].get('PRD_POWER')[0] + "." + product[k].get('PRD_POWER')[1:] + "0"

                                    product_product_id = request.env['product.product'].with_context(disable_varients=True, create_product_product=False).create({
                                        'type': 'product',
                                        'name': product_template.name,
                                        'product_tmpl_id': product_template.id,
                                        'trial': False if product_family[j].get('PRF_REV_DIAG_IND') == 'R' else True,
                                        'diam': product_family[j].get('PRF_DIAMETER')[0:2] + '.' + product_family[j].get('PRF_DIAMETER')[2],
                                        'bc': product_family[j].get('PRF_BASECURVE')[0:1] + '.' + product_family[j].get('PRF_BASECURVE')[1],
                                        'barcode': product[k].get('PRD_UPC_CODE'),
                                        'sphere': sphere,
                                        'cylinder': None if cylinder == "00." else cylinder,
                                        'axis': None if axis == "0" else axis,
                                    })
                                    if data[i].get('STY_ID') == 'SPH':
                                        if product[k].get('PRD_COLOR') != 'Clear':
                                            spec_contact_lens_color_type = request.env['spec.contact.lens.color.type'].search([('name', '=', product[k].get('PRD_COLOR'))])
                                            if not spec_contact_lens_color_type.id:
                                                spec_contact_lens_color_type = request.env['spec.contact.lens.color.type'].create({
                                                    'name': product[k].get('PRD_COLOR'),
                                                })
                                            product_product_id.update({
                                                'color_type_id': spec_contact_lens_color_type.id,
                                            })
                                    elif data[i].get('STY_ID') == 'BIF':
                                        product_product_id.update({
                                            'add': product[k].get('PRD_COLOR') if product[k].get('PRD_COLOR').rfind('(') == -1 else product[k].get('PRD_COLOR')[0:product[k].get('PRD_COLOR').rindex('(')-1],
                                        })
                                    elif product[k].get('PRD_ADDITION') != '0' and product[k].get('PRD_COLOR') != '':
                                        product_product_id.update({
                                            'add': product[k].get('PRD_ADDITION') if product[k].get('PRD_ADDITION').rfind('(') == -1 else product[k].get('PRD_ADDITION')[0:product[k].get('PRD_ADDITION').rindex('(')-1],
                                            'multi_focal': product[k].get('PRD_COLOR'),
                                        })
                                    elif product[k].get('PRD_ADDITION') != '0':
                                        product_product_id.update({
                                            'add': product[k].get('PRD_ADDITION') if product[k].get('PRD_ADDITION').rfind('(') == -1 else product[k].get('PRD_ADDITION')[0:product[k].get('PRD_ADDITION').rindex('(')-1],
                                        })

                    if product_end_id >= len(product):
                        products_id = 0
                        if product_family_id < len(product_family)-1:
                            product_family_id += 1
                        elif product_family_id >= len(product_family) -1:
                            product_family_id = 0
                            if series_id < len(data) - 1:
                                series_id += 1
                            elif series_id >= len(data) -1:
                                series_id = -1
                    else:
                        products_id = product_end_id

                return json.dumps(['1', str(series_id), str(product_family_id), str(products_id)])
            # except:
            #     return json.dumps(['0', str(series_id), str(product_family_id), str(products_id)])

    @http.route(['/contact_lens_import/xml_correction'], type='http', auth="user", methods=['POST', 'GET'], csrf=False)
    def xml_imports(self, **kw):
        product_template = request.env['product.template'].search([('categ_id.name', '=', 'Contact Lens'), ('type', '=', 'product')])
        for data in product_template:
            product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', data.id),
                                                                        ('axis', '=', '')])
            for data in product_product_id:
                data.update({
                    'axis': None,
                })


            # product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', data.id)])
            # for a in product_product_id:
            #     if (a.sphere[0] == '-' or a.sphere[0] == '+') and len(a.sphere) == 7:
            #         a.sphere = a.sphere.replace('.', '')[0:3] + '.00'

            # product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', data.id),
            #                                                             ('cylinder', '=', '00.'),
            #                                                             ('axis', '=', '0')])
            # for data in product_product_id:
            #     data.update({
            #         'cylinder': None,
            #         'axis': None,
            #     })
            # product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', data.id),
            #                                                             ('sphere', '=', '+0.'),
            #                                                             ])
            # for data in product_product_id:
            #     data.update({
            #         'sphere': "-0.00",
            #     })
            # product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', data.id),
            #                                                             ])
            # for data in product_product_id:
            #     if data.sphere:
            #         if len(data.sphere.split('.')) == 1:
            #             data.sphere = data.sphere + ".0"
            #         data.update({
            #             'sphere': data.sphere.split('.')[0] + data.sphere.split('.')[1][0] + '.' + data.sphere.split('.')[1][1:] if len(data.sphere.split('.')[1]) == 3 else (data.sphere + "0" if len(data.sphere.split('.')[1]) == 1 else data.sphere),
            #         })
            #     data.update({
            #         'axis': ("00" + data.axis if len(data.axis) == 1 else data.axis) if data.axis else data.axis,
            #     })
            # product_product_id = request.env['product.product'].search([('product_tmpl_id', '=', data.id),
            #                                                             ('add', 'like', '('),
            #                                                             ])
            # for data in product_product_id:
            #     if data.add:
            #         data.update({
            #             'add':  data.add if data.add.rfind('(') == -1 else data.add[0:data.add.rindex('(')-1],
            #         })
        # request.env['product.packaging'].search([('name', '=', 'Box of 12')], limit=1).update({'name': '12 pack'})
        return 'OK'

    @http.route(['/contact_lens_import/xml_corrections'], type='http', auth="user", methods=['POST', 'GET'], csrf=False)
    def xml_importss(self, **kw):
        product_template = request.env['product.template'].search([('categ_id.name', '=', 'Contact Lens'), ('type', '=', 'product')])
        a = []
        UNT_NAME = {"1 Blister": "1 Blister", "2 pack":"Box of 2", '3 pack':'Box of 3', '5 pack':'Box of 5',
                    '6 pack':'Box of 6', '30 pack':'Box of 30', '90 pack':'Box of 90', '12 pack': 'Box of 12'}
        for data in product_template:
            if data.uom_id.id:
                if data.uom_id.name not in UNT_NAME:
                    a.append(data.uom_id.name)
                    UNT_NAME[data.uom_id.name] = ''
        return json.dumps(a)

    @http.route(['/visionweb/frame_types/import'], type='http', auth="user", methods=['POST', 'GET'], csrf=False)
    def vw_ft_import(self, **kw):
        # try:
            general_settings = request.env['vision.web'].search([]).get_visionweb_config()
            link = requests.get(str(general_settings[0]) + "/GetStandardCatalogByLoginSupplier?username=" + str(
                general_settings[1]) + "&password=" + str(general_settings[2]) + "&refid=" + str(
                general_settings[3]) + "&sloid=" + str(general_settings[4]) + "&type=" + str(general_settings[5]))
            if link.status_code == 200:
                tree = ET.fromstring(link.text)
                if tree.text and tree.text != '':
                    newData = ET.fromstring(tree.text)

                FrameTypes = {n.get("VwCode"): n.get('Description') for n in newData[6].findall(".//FRAME")}
                for key in FrameTypes:
                    spec_frame_type_id = request.env['spec.frame.type'].search([('name', '=', FrameTypes[key])], limit=1)
                    if not spec_frame_type_id.id:
                        spec_frame_type_id = request.env['spec.frame.type'].create({
                            'name': FrameTypes[key],
                            'vw_code': key,
                        })
                    else:
                        spec_frame_type_id.update({
                            'vw_code': key,
                        })
                return "done"
            return "error"
        # except:
        #     return "error"