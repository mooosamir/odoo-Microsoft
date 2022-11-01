# -*- coding: utf-8 -*-
import json

import requests
from xml.etree import ElementTree
from odoo import models, fields, api, exceptions
from xml.etree import ElementTree as ET
import urllib.parse
from html import escape
import uuid


class VisionWeb(models.TransientModel):
    _name = 'vision.web'
    _description = 'vision_web.vision_web'

    name = fields.Char()

    def get_visionweb_config(self):
        catalog_link = 'http://services.visionwebqa.com/VWCatalog.asmx'
        username = self.env['ir.config_parameter'].sudo().search([('key', '=', 'vw_username')]).value
        password = self.env['ir.config_parameter'].sudo().search([('key', '=', 'vw_password')]).value
        refid = 'ROKANDOOIT'
        sloid = self.env['ir.config_parameter'].sudo().search([('key', '=', 'vw_sloid')]).value
        type = 'SUP1'

        return catalog_link, username, password, refid, sloid, type \
            if catalog_link and username and password and refid and sloid and type else None

    def get_vendors(self):
        data = []

        vendor_ids = self.env['res.partner'].search([('supplier_rank', '>=', 1),('is_lab', '=', True)])
        for vendor in vendor_ids:
            data.append({
                'id': vendor.id,
                'name': vendor.name,
            })
        return data

    def get_api_data(self):
        try:
            general_settings = self.get_visionweb_config()
            link = requests.get(str(general_settings[0]) + "/GetStandardCatalogByLoginSupplier?username=" + str(
                general_settings[1]) + "&password=" + str(general_settings[2]) + "&refid=" + str(
                general_settings[3]) + "&sloid=" + str(general_settings[4]) + "&type=" + str(general_settings[5]))
            if link.status_code == 200:
                tree = ET.fromstring(link.text)
                if tree.text and tree.text != '':
                    newData = ET.fromstring(tree.text)

                # Lens Treatment
                treatment_sub_category = {}
                spec_lens_categories = {record.short_code:(record.name if record.name else '') for record in self.env['spec.lens.category'].search([])}
                LensTreatemnts = {n.get("Code"): n.attrib for n in newData[1].findall(".//ADDED_VALUE/TREATMENT[@Code]")}
                for treatment in newData[5]:
                    if treatment.get('VwCode') in LensTreatemnts:
                        LensTreatemnts[treatment.get('VwCode')]['Incompatible'] = [n.attrib for n in treatment.findall(".//INCOMPATIBLE")]
                    # else:
                    #     LensTreatemnts[treatment.get('VwCode')] = {'code': treatment.get('VwCode'), 'Description': treatment.get('Description'), 'Incompatible': [n.attrib for n in newData[5][0].findall(".//INCOMPATIBLE")]}
                for key in LensTreatemnts:
                    if key.split('-',1)[0] in spec_lens_categories:
                        if spec_lens_categories[key.split('-',1)[0]] in treatment_sub_category:
                            treatment_sub_category[spec_lens_categories[key.split('-',1)[0]]]['selections'].append(LensTreatemnts[key])
                        else:
                            treatment_sub_category[spec_lens_categories[key.split('-',1)[0]]] = {'name': spec_lens_categories[key.split('-',1)[0]], 'selections':[]}
                    else:
                        print(LensTreatemnts[key])
                treatment_sub_category = [treatment_sub_category[data] for data in treatment_sub_category]

                # Lens
                spec_lens_material = {record.code:(record.name if record.name else '') for record in self.env['spec.lens.material'].search([('code', '!=', '')])}
                spec_lens_filter = {record.code:(record.name if record.name else '') for record in self.env['spec.lens.filter'].search([('code', '!=', '')])}
                spec_lens_colors = {record.code:(record.name if record.name else '') for record in self.env['spec.lens.colors'].search([('code', '!=', '')])}

                ADD_IDs = [{'ADD_ID':n.get('ADD_ID'), 'Description':n.get('Description'),'Treatments':{t.get("Code"): t.attrib for t in n.findall(".//TREATMENT[@Code]")}} for n in newData[1].findall(".//ADDED_VALUE[@ADD_ID]")]
                Designs = {n.get("VwCode"): {'VwCode':n.get('VwCode'),'ParameterID':n.get('ParameterID'), 'Description':n.get('Description'),'LensTypeCode':n.findall('.//LENSTYPE')[0].get('Code')} for n in newData[3].findall(".//DESIGN")}
                Materials = {n.get("VwCode"): n.attrib for n in newData[4].findall(".//MATERIAL")}
                LensTypes = {n.get("Code"): n.get('Description') for n in newData[7].findall(".//LENS_TYPE")}

                Lenses = []
                lens_sub_category = {}

                for treatment in newData[5]:
                    for ADD_ID in range(0,len(ADD_IDs),1):
                        if treatment.get('VwCode') in ADD_IDs[ADD_ID]['Treatments']:
                            ADD_IDs[ADD_ID]['Treatments'][treatment.get('VwCode')]['Incompatible'] = [n.attrib for n in treatment.findall(".//INCOMPATIBLE")]
                for ADD_ID in range(0,len(ADD_IDs),1):
                    treatment_list = []
                    for key in ADD_IDs[ADD_ID]['Treatments']:
                        treatment_list.append(ADD_IDs[ADD_ID]['Treatments'][key])
                    ADD_IDs[ADD_ID]['Treatments'] = treatment_list
                ADD_IDs = {n.get('ADD_ID'):n for n in ADD_IDs}

                for n in newData[2].findall(".//LENS"):
                    Lenses.append({
                        'ADD_ID': n.get('ADD_ID'),
                        'Description': n.get('Description'),
                        'DesignCode': n.get('DesignCode'),
                        'MaterialCode': n.get('MaterialCode'),
                    })
                    if n.get('ADD_ID') in ADD_IDs:
                        Lenses[len(Lenses) - 1]['AddDescription'] = ADD_IDs[n.get('ADD_ID')]['Description']
                        # Lenses[len(Lenses) - 1]['AddTreatments'] = ADD_IDs[n.get('ADD_ID')]['Treatments']
                    if n.get('DesignCode') in Designs:
                        Lenses[len(Lenses) - 1]['DesignParameterID'] = Designs[n.get('DesignCode')]['ParameterID']
                        Lenses[len(Lenses) - 1]['DesignDescription'] = Designs[n.get('DesignCode')]['Description']
                        Lenses[len(Lenses) - 1]['DesignLensTypeCode'] = Designs[n.get('DesignCode')]['LensTypeCode']
                        if Designs[n.get('DesignCode')]['LensTypeCode'] in LensTypes:
                            Lenses[len(Lenses) - 1]['DesignLensTypeDescription'] = LensTypes[Designs[n.get('DesignCode')]['LensTypeCode']]
                    if n.get('MaterialCode') in Materials:
                        Lenses[len(Lenses) - 1]['MaterialDescription'] = Materials[n.get('MaterialCode')]['Description']
                    material = n.get('MaterialCode').split('-')
                    material_custom_code_1 = ''
                    material_custom_code_2 = ' '
                    material_custom_code_3 = ' '
                    if (material[0] + '-' + material[1]) in spec_lens_material:
                        material_custom_code_1 = spec_lens_material[material[0] + '-' + material[1]]
                    else:
                        material_custom_code_1 = '---'
                    if material[2] == 'XTRA':
                        if 'XTRA' in Lenses[len(Lenses) - 1]['MaterialDescription']:
                            material_custom_code_2 += 'Transitions Xtractive'
                        else:
                            material_custom_code_2 += 'Photochormic Xtra'
                    elif (material[2]) in spec_lens_filter:
                        material_custom_code_2 += spec_lens_filter[material[2]]
                    else:
                        material_custom_code_2 += '---'
                    # if (material[3][0:3]) in spec_lens_colors:
                    #     material_custom_code_3 += spec_lens_colors[material[3][0:3]]
                    if material[3] in spec_lens_colors:
                        material_custom_code_3 += spec_lens_colors[material[3]]
                    else:
                        material_custom_code_3 += '---'
                    Lenses[len(Lenses) - 1]['name'] = material_custom_code_1 + material_custom_code_2 + material_custom_code_3

                for data in Lenses:
                    if data['DesignDescription'] in lens_sub_category:
                        DesignDescription = data['DesignDescription']
                        del data['DesignDescription']
                        lens_sub_category[DesignDescription]['selections'].append(data)
                    else:
                        lens_sub_category[data['DesignDescription']] = {'name': data['DesignDescription'], 'selections':[]}
                        DesignDescription = data['DesignDescription']
                        del data['DesignDescription']
                        lens_sub_category[DesignDescription]['selections'].append(data)
                # for data in Lenses:
                #     if data['DesignCode'] in lens_sub_category:
                #         DesignCode = data['DesignCode']
                #         del data['DesignCode']
                #         lens_sub_category[DesignCode]['selections'].append(data)
                #     else:
                #         lens_sub_category[data['DesignCode']] = {'name': data['DesignCode'], 'selections':[]}
                #         DesignCode = data['DesignCode']
                #         del data['DesignCode']
                #         lens_sub_category[DesignCode]['selections'].append(data)
                lens_sub_category = [lens_sub_category[data] for data in lens_sub_category]

                return lens_sub_category,treatment_sub_category, ADD_IDs
            else:
                return [],[],{}
        except:
            raise exceptions.Warning("Server error, try again in a few minutes.")

    def import_lens(self, lens, treatment, lens_add_ids):
        try:
            for data in treatment.values():
                spec_lens_category_id = self.env['spec.lens.category'].search([('name','=',data['sub_category'])],limit=1)
                product_template_id = self.env['product.template'].search([('vw_code','=',data['Code'])],limit=1)
                if not product_template_id.id:
                    product_category_id = self.env['product.category'].search([('name', '=', 'Lens Treatment')], limit=1)
                    if not product_category_id.id:
                        product_category_id = self.env['product.category'].create({
                            'name': 'Lens Treatment'
                        })
                    product_template_id = self.env['product.template'].create({
                        'name': data['Description'],
                        'vw_code': data['Code'],
                        'category_id': spec_lens_category_id.id,
                        'categ_id': product_category_id.id,
                        'spec_product_type': 'lens_treatment',
                    })
                for incompatible in data['Incompatible']:
                    incompatible_product_template_id = self.env['product.template'].search([('vw_code', '=', incompatible['VwCode'])], limit=1)
                    if not incompatible_product_template_id.id:
                        incompatible_product_template_id = self.env['product.template'].create({
                            'name': incompatible['Description'],
                            'vw_code': incompatible['VwCode'],
                            'category_id': spec_lens_category_id.id,
                            'categ_id': product_category_id.id,
                            'spec_product_type': 'lens_treatment',
                        })
                        product_template_id.update({
                            'incompatible_treatments_ids': (incompatible_product_template_id.id, product_template_id.id),
                        })
                        # self.env['procuct_template_template_rel'].create({
                        #     'parent_id': product_template_id.id,
                        #     'child_id': incompatible_product_template_id.id,
                        # })

            spec_lens_categories = {record.short_code:record.name for record in self.env['spec.lens.category'].search([])}
            for data in lens.values():
                spec_lens_type_id = self.env['spec.lens.type'].search([('code','=',data['DesignLensTypeCode'])],limit=1)
                if not spec_lens_type_id.id:
                    spec_lens_type_id = self.env['spec.lens.type'].create({
                        'code': data['DesignLensTypeCode'],
                        'name': data['DesignLensTypeDescription'],
                    })
                parent_category_id = self.env['product.category'].search([('name', '=', 'Lens')])
                if not parent_category_id.id:
                    parent_category_id = self.env['product.category'].create({
                        'name': 'Lens'
                    })
                product_category_id = self.env['product.category'].search([('name', '=', spec_lens_type_id.name),
                                                                           ('parent_id', '=', parent_category_id.id)])
                if not product_category_id.id:
                    product_category_id = self.env['product.category'].create({
                        'name': spec_lens_type_id.name,
                        'parent_id': parent_category_id.id
                    })
                spec_lens_style_id = self.env['spec.lens.style'].search([('code', '=', data['DesignCode'])],limit=1)
                if not spec_lens_style_id.id:
                    spec_lens_style_id = self.env['spec.lens.style'].create({
                        'name': data['sub_category'],
                        'code': data['DesignCode'],
                    })
                spec_lens_material_id = self.env['spec.lens.material'].search([('code','=','-'.join(data['MaterialCode'].split('-')[0:2]))],limit=1)
                if not spec_lens_material_id.id:
                    spec_lens_material_id = self.env['spec.lens.material'].create({
                        'code': '-'.join(data['MaterialCode'].split('-')[0:2]),
                        'name': 'N/A',
                    })
                material_name = ''
                if data['MaterialCode'].split('-')[2] == 'XTRA':
                    if 'XTRA' in data['MaterialDescription']:
                        material_name = 'Transitions Xtractive'
                    else:
                        material_name = 'Photochormic Xtra'
                if material_name == '':
                    spec_lens_filter_id = self.env['spec.lens.filter'].search([('code', '=', data['MaterialCode'].split('-')[2])])
                    if not spec_lens_filter_id.id:
                        spec_lens_filter_id = self.env['spec.lens.filter'].create({
                            'code': data['MaterialCode'].split('-')[2],
                            'name': 'N/A',
                        })
                else:
                    spec_lens_filter_id = self.env['spec.lens.filter'].search([('code', '=', data['MaterialCode'].split('-')[2]),
                                                                               ('name', '=', material_name)])
                spec_lens_colors_id = self.env['spec.lens.colors'].search([('code', '=', data['MaterialCode'].split('-')[3])])
                if not spec_lens_colors_id.id:
                    spec_lens_colors_id = self.env['spec.lens.colors'].create({
                        'code': data['MaterialCode'].split('-')[3],
                        'name': 'N/A',
                    })

                product_template_id = self.env['product.template'].search([('lens_type_id','=',spec_lens_type_id.id),
                                                                           ('style_id','=',spec_lens_style_id.id),
                                                                           ('material_id','=',spec_lens_material_id.id),
                                                                           ('filter_id','=',spec_lens_filter_id.id),
                                                                           ('color_id','=',spec_lens_colors_id.id)],limit=1)
                if not product_template_id.id:
                    product_template_id = self.env['product.template'].create({
                        'name': data['sub_category'] + " " + data['MaterialDescription'],
                        'lens_type_id': spec_lens_type_id.id,
                        'categ_id': product_category_id.id,
                        'style_id':spec_lens_style_id.id,
                        'material_id':spec_lens_material_id.id,
                        'filter_id':spec_lens_filter_id.id,
                        'color_id':spec_lens_colors_id.id,
                        'prd_categ_name':'lens',
                        'vw_code_material': data['MaterialCode'],
                        'vw_code_style': data['DesignCode'],
                        'vw_code_type': data['DesignLensTypeCode'],
                        'spec_product_type': 'lens',
                    })
                else:
                    product_template_id.update({
                        'vw_code_material': data['MaterialCode'],
                        'vw_code_style': data['DesignCode'],
                        'vw_code_type': data['DesignLensTypeCode'],
                        'spec_product_type': 'lens',
                    })

                if data['ADD_ID'] in lens_add_ids:
                    for treatments in lens_add_ids[data.get('ADD_ID')]['Treatments']:
                        spec_lens_category_id = self.env['spec.lens.category'].search([('short_code', '=', treatments['Code'].split('-',1)[0])],limit=1)
                        if not spec_lens_category_id.id:
                            spec_lens_category_id = self.env['spec.lens.category'].create({
                                'short_code': treatments['Code'].split('-',1)[0],
                                'name': 'N/A',
                            })
                        if treatments['Code'].split('-',1)[0] == 'AR' or treatments['Code'].split('-',1)[0] == 'MIRR':
                            child_product_template_id = self.env['treatment.for.lens'].search([('code', '=', treatments['Code'])], limit=1)
                            if not child_product_template_id.id:
                                child_product_template_id = self.env['treatment.for.lens'].create({
                                    'description': treatments['Description'],
                                    'code': treatments['Code'],
                                    'category_id': spec_lens_category_id.id,
                                })
                            # if 'Incompatible' in treatments:
                            #     for incompatible in treatments['Incompatible']:
                            #         incompatible_product_template_id = self.env['product.template'].search(
                            #             [('vw_code', '=', incompatible['VwCode'])], limit=1)
                            #         if incompatible_product_template_id.id:
                            #             child_product_template_id.update({
                            #                 'incompatible_treatments_ids': (incompatible_product_template_id.id, child_product_template_id.id),
                            #             })

                            self.env['spec.lens.treatment.child'].create({
                                'category_id': spec_lens_category_id.id,
                                'lens_id': product_template_id.id,
                                'lens_treatment_id': child_product_template_id.id,
                                'lnclude': False,
                            })

            return True
        except:
            return False

    def transmit_data(self, ids):
        # send data
        general_settings = self.get_visionweb_config()
        multi_order_type_ids = self.env['multi.order.type'].search([('id', 'in', [int(id) for id in ids])])
        # multi_order_type.vw_order_id = ''

        return_statements = ""
        for multi_order_type in multi_order_type_ids:
            return_statements += "<br/>"
            return_statements += "<br/><h3 style='text-decoration: underline;'>*) " + str(multi_order_type.display_name) + "</h3>"
            if multi_order_type.vw_order_id != '' and multi_order_type.vw_order_id:
                return_statements += "<br/><b style='text-decoration: underline;'> *) Order Tracking Info </b><br/> " + str(self.order_tracking(multi_order_type.id))
            else:
                try:
                    if multi_order_type.lens_products.id:
                        lens_material = multi_order_type.lens_products.vw_code_material if multi_order_type.lens_products.vw_code_material else ''
                        # if multi_order_type.lens_products.material_id.id and multi_order_type.lens_products.filter_id.id and\
                        #         multi_order_type.lens_products.color_id.id:
                        #     lens_material = multi_order_type.lens_products.material_id.code + "-" + multi_order_type.lens_products.filter_id.code + \
                        #                         "-" + multi_order_type.lens_products.color_id.code + "-00"
                        # else:
                        #     lens_material = ''
                    else:
                        lens_material = ''
                    if multi_order_type.rx == "glasses":
                        gls_h_base = multi_order_type.gls_h_base if multi_order_type.gls_h_base else ''
                        if gls_h_base == "bi":
                            gls_h_base = "In"
                        elif gls_h_base == "bo":
                            gls_h_base = "Out"
                        gls_v_base = multi_order_type.gls_v_base if multi_order_type.gls_v_base else ''
                        if gls_v_base == "bu":
                            gls_v_base = "Up"
                        elif gls_v_base == "bd":
                            gls_v_base = "Down"
                        gls_left_lens_h_prism = multi_order_type.gls_left_lens_h_prism if multi_order_type.gls_left_lens_h_prism else ''
                        gls_left_lens_v_prism = multi_order_type.gls_left_lens_v_prism if multi_order_type.gls_left_lens_v_prism else ''
                        os_cylinder = multi_order_type.gls_left_lens_cylinder if multi_order_type.gls_left_lens_cylinder else ''
                        od_cylinder = multi_order_type.gls_cylinder if multi_order_type.gls_cylinder else ''
                        od_axis = multi_order_type.gls_axis if multi_order_type.gls_axis else ''
                        os_axis = multi_order_type.gls_left_lens_axis if multi_order_type.gls_left_lens_axis else ''
                        od_add = multi_order_type.gls_add if multi_order_type.gls_add else ''
                        os_add = multi_order_type.gls_left_lens_add if multi_order_type.gls_left_lens_add else ''
                        od_sphere = multi_order_type.gls_sphere if multi_order_type.gls_sphere else ''
                        os_sphere = multi_order_type.gls_left_lens_sphere if multi_order_type.gls_left_lens_sphere else ''
                    elif multi_order_type.rx == "soft":
                        return_statements += "<br/> *)Can't transmit data for soft contact lens"
                        os_cylinder = multi_order_type.soft_left_cylinder if multi_order_type.soft_left_cylinder else ''
                        od_cylinder = multi_order_type.select_soft_cylinder if multi_order_type.select_soft_cylinder else ''
                        od_axis = multi_order_type.select_soft_axis if multi_order_type.select_soft_axis else ''
                        os_axis = multi_order_type.soft_left_axis if multi_order_type.soft_left_axis else ''
                        od_sphere = multi_order_type.select_soft_sphere if multi_order_type.select_soft_sphere else ''
                        os_sphere = multi_order_type.soft_left_sphere if multi_order_type.soft_left_sphere else ''
                        # od_add = multi_order_type.gls_add
                        # os_add = multi_order_type.gls_left_lens_add
                        od_add = ''
                        os_add = ''
                    elif multi_order_type.rx == "hard":
                        return_statements += "<br/> *) Can't transmit data for hard contact lens"
                        os_cylinder = multi_order_type.left_cylinder if multi_order_type.left_cylinder else ''
                        od_cylinder = multi_order_type.cylinder if multi_order_type.cylinder else ''
                        od_add = multi_order_type.add if multi_order_type.add else ''
                        os_add = multi_order_type.left_add if multi_order_type.left_add else ''
                        od_axis = multi_order_type.axis if multi_order_type.axis else ''
                        os_axis = multi_order_type.left_axis if multi_order_type.left_axis else ''
                        od_sphere = multi_order_type.sphere if multi_order_type.sphere else ''
                        os_sphere = multi_order_type.left_sphere if multi_order_type.left_sphere else ''
                    else:
                        gls_left_lens_v_prism = ''
                        gls_left_lens_h_prism = ''
                        gls_v_base = ''
                        gls_h_base = ''
                        os_cylinder = ''
                        od_cylinder = ''
                        od_axis = ''
                        os_axis = ''
                        od_add = ''
                        os_add = ''
                        od_sphere = ''
                        os_sphere = ''

                    if multi_order_type.eye_lab_details == "Both":
                        eye_lab_details = "B"
                    elif multi_order_type.eye_lab_details == "Right Only":
                        eye_lab_details = "R"
                    elif multi_order_type.eye_lab_details == "Left Only":
                        eye_lab_details = "L"
                    else:
                        eye_lab_details = ''

                    if len(multi_order_type.lenstreatment_products.ids):
                        lens_treatment_length = 3
                        lens_treatment = ''
                        if len(multi_order_type.lenstreatment_products.ids) < 3:
                            lens_treatment_length = len(multi_order_type.lenstreatment_products.ids)
                        for i in range(0,lens_treatment_length,1):
                            lens_treatment += '''<Item>
                                                   <FieldName>RETreatment''' + str(i) + '''</FieldName>
                                                   <FieldValue>''' + str(multi_order_type.lenstreatment_products[i].vw_code if  multi_order_type.lenstreatment_products[i].vw_code != '' and multi_order_type.lenstreatment_products[i].vw_code else '') + '''</FieldValue>
                                                 </Item>
                                                 <Item>
                                                   <FieldName>LETreatment''' + str(i) + '''</FieldName>
                                                   <FieldValue>''' + str(multi_order_type.lenstreatment_products[i].vw_code if  multi_order_type.lenstreatment_products[i].vw_code != '' and multi_order_type.lenstreatment_products[i].vw_code else '') + '''</FieldValue>
                                                 </Item>'''
                        if multi_order_type.gls_balance:
                            balance_right = self.env['product.template'].search([('name', '=', 'Balance Right'), ('prd_categ_name', '=', 'Lens Treatment')])
                            if balance_right.id:
                                lens_treatment += '''<Item>
                                                       <FieldName>RETreatment''' + str(i) + '''</FieldName>
                                                       <FieldValue>''' + str(balance_right.vw_code if balance_right.vw_code != '' and balance_right.vw_code else '') + '''</FieldValue>
                                                     </Item>
                                                     <Item>
                                                       <FieldName>LETreatment''' + str(i) + '''</FieldName>
                                                       <FieldValue>''' + str(balance_right.vw_code if balance_right.vw_code != '' and balance_right.vw_code else '') + '''</FieldValue>
                                                     </Item>'''
                        if multi_order_type.gls_left_balance:
                            balance_left = self.env['product.template'].search([('name', '=', 'Balance Left'), ('prd_categ_name', '=', 'Lens Treatment')])
                            if balance_right.id:
                                lens_treatment += '''<Item>
                                                       <FieldName>RETreatment''' + str(i) + '''</FieldName>
                                                       <FieldValue>''' + str(balance_left.vw_code if balance_left.vw_code != '' and balance_left.vw_code else '') + '''</FieldValue>
                                                     </Item>
                                                     <Item>
                                                       <FieldName>LETreatment''' + str(i) + '''</FieldName>
                                                       <FieldValue>''' + str(balance_left.vw_code if balance_left.vw_code != '' and balance_left.vw_code else '') + '''</FieldValue>
                                                     </Item>'''
                    else:
                        lens_treatment = ''

                    order_id = '%Complete Pair%' if multi_order_type.order_type_name == 'Complete Pair' else '%Lenses Only%'
                    order_id_replace = 'Complete Pair - ' if multi_order_type.order_type_name == 'Complete Pair' else 'Lenses Only - '
                    if multi_order_type.frame_type.id:
                        FrameType = str(multi_order_type.frame_type.vw_code if multi_order_type.frame_type.vw_code != '' and multi_order_type.frame_type.vw_code else '')
                    elif multi_order_type.frame_id.id:
                        FrameType = str(multi_order_type.frame_id.vw_code if multi_order_type.frame_id.vw_code != '' and multi_order_type.frame_id.vw_code else '')

                    headers = {'Content-Type': 'text/xml'}
                    raw_data = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://services.visionweb.com">
                                   <soapenv:Header/>
                                   <soapenv:Body>
                                      <ser:UploadFile>
                                         <ser:username>''' + general_settings[1] + '''</ser:username>
                                         <ser:pswd>''' + general_settings[2] + '''</ser:pswd>
                                         <ser:filestring><![CDATA[<?xml version="1.0" encoding="utf-8"?>
                                            <VWOrder>
                                              <Item>
                                                <FieldName>Username</FieldName>
                                                <FieldValue>''' + general_settings[1] + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>Password</FieldName>
                                                <FieldValue>''' + general_settings[2] + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>OrderId</FieldName>
                                                <FieldValue>''' + self.env['sale.order.line'].search([('lab_details_id', '=', multi_order_type.id), ('name', '=like', order_id)]).name.replace(order_id_replace, '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>SupplierName</FieldName>
                                                <FieldValue>''' + "9901" + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>BillAccount</FieldName>
                                                <FieldValue>''' + (self.env.user.company_id.vw_ship_account if self.env.user.company_id.vw_ship_account else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>ShipAccount</FieldName>
                                                <FieldValue>''' + (self.env.user.company_id.vw_ship_account if self.env.user.company_id.vw_ship_account else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>PONumber</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>PatLastName</FieldName>
                                                <FieldValue>''' + str(multi_order_type.partner_id.last_name) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>PatFirstName</FieldName>
                                                <FieldValue>''' + str(multi_order_type.partner_id.first_name if  multi_order_type.partner_id.first_name else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RESph</FieldName>
                                                <FieldValue>''' + str(od_sphere) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RECyl</FieldName>
                                                <FieldValue>''' + str(od_cylinder) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REAxis</FieldName>
                                                <FieldValue>''' + str(od_axis) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REAdd</FieldName>
                                                <FieldValue>''' + str(od_add) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REHorizPrismValue</FieldName>
                                                <FieldValue>''' + str(gls_h_base) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REHorizPrismDirection</FieldName>
                                                <FieldValue>''' + str((multi_order_type.gls_h_prism if multi_order_type.gls_h_prism else '') if multi_order_type.rx == "glasses" else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REVerticalPrismValue</FieldName>
                                                <FieldValue>''' + str((multi_order_type.gls_v_prism if multi_order_type.gls_v_prism else '') if multi_order_type.rx == "glasses" else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REVerticalPrismDirection</FieldName>
                                                <FieldValue>''' + str(gls_v_base) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REDistPD</FieldName>
                                                <FieldValue>''' + str(multi_order_type.dist_pd_lab_details if multi_order_type.dist_pd_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RENearPD</FieldName>
                                                <FieldValue>''' + str(multi_order_type.near_pd_lab_details if multi_order_type.near_pd_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RESegHeight</FieldName>
                                                <FieldValue>''' + str(multi_order_type.seg_ht_lab_details if multi_order_type.seg_ht_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REOpticalCenter</FieldName>
                                                <FieldValue>''' + str(multi_order_type.oc_hit_lab_details if multi_order_type.oc_hit_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>REBaseCurve</FieldName>
                                                <FieldValue>''' + str(multi_order_type.bc_lab_details if multi_order_type.bc_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LESph</FieldName>
                                                <FieldValue>''' + str(os_sphere) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LECyl</FieldName>
                                                <FieldValue>''' + str(os_cylinder) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEAxis</FieldName>
                                                <FieldValue>''' + str(os_axis) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEAdd</FieldName>
                                                <FieldValue>''' + str(os_add) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEHorizPrismValue</FieldName>
                                                <FieldValue>''' + str((multi_order_type.gls_left_h_base if multi_order_type.gls_left_h_base else '') if multi_order_type.rx == "glasses" else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEHorizPrismDirection</FieldName>
                                                <FieldValue>''' + str(gls_left_lens_h_prism) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEVerticalPrismValue</FieldName>
                                                <FieldValue>''' + str(gls_left_lens_v_prism) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEVerticalPrismDirection</FieldName>
                                                <FieldValue>''' + str((multi_order_type.gls_left_v_base if multi_order_type.gls_left_v_base else '') if multi_order_type.rx == "glasses" else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEDistPD</FieldName>
                                                <FieldValue>''' + str(multi_order_type.dist_pd_lab_details_os if multi_order_type.dist_pd_lab_details_os else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LENearPD</FieldName>
                                                <FieldValue>''' + str(multi_order_type.near_pd_lab_details_os if multi_order_type.near_pd_lab_details_os else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LESegHeight</FieldName>
                                                <FieldValue>''' + str(multi_order_type.seg_ht_lab_details_os if multi_order_type.seg_ht_lab_details_os else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEOpticalCenter</FieldName>
                                                <FieldValue>''' + str(multi_order_type.oc_hit_lab_details_os if multi_order_type.oc_hit_lab_details_os else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LEBaseCurve</FieldName>
                                                <FieldValue>''' + str(multi_order_type.bc_lab_details_os if multi_order_type.bc_lab_details_os else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>Eyes</FieldName>
                                                <FieldValue>''' + eye_lab_details + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>JobType</FieldName>
                                                <FieldValue>''' + (str(multi_order_type.finishing_status) if multi_order_type.finishing_status else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LensShape</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>SpecialInstructions1</FieldName>
                                                <FieldValue>''' + str(multi_order_type.lab_instructions if multi_order_type.lab_instructions else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RELensDesign</FieldName>
                                                <FieldValue>''' + str((multi_order_type.lens_products.style_id.code if multi_order_type.lens_products.style_id.id else '') if multi_order_type.lens_products.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RELensMaterial</FieldName>
                                                <FieldValue>''' + str(lens_material) + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LELensDesign</FieldName>
                                                <FieldValue>''' + str((multi_order_type.lens_products.style_id.code if multi_order_type.lens_products.style_id.id else '') if multi_order_type.lens_products.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LELensMaterial</FieldName>
                                                <FieldValue>''' + str(lens_material) + '''</FieldValue>
                                              </Item>
                                              ''' + lens_treatment + '''
                                              <Item>
                                                <FieldName>RETreatmentComments</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LETreatmentComments</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameType</FieldName>
                                                <FieldValue>''' + FrameType + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameManufacturer</FieldName>
                                                <FieldValue>''' + str((multi_order_type.frames_products_variants.frame_manufacturer_id.name if multi_order_type.frames_products_variants.frame_manufacturer_id.id else '') if multi_order_type.frames_products_variants.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameModel</FieldName>
                                                <FieldValue>''' + str(multi_order_type.frames_products_variants.model_number if multi_order_type.frames_products_variants.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameColor</FieldName>
                                                <FieldValue>''' + str((multi_order_type.frames_products_variants.color_id.name if multi_order_type.frames_products_variants.color_id.id else '') if multi_order_type.frames_products_variants.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameTempleLength</FieldName>
                                                <FieldValue>''' + str((multi_order_type.frames_products_variants.temple if multi_order_type.frames_products_variants.temple else '') if multi_order_type.frames_products_variants.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameEyeSize</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>FrameSKU</FieldName>
                                                <FieldValue>''' + str(multi_order_type.frames_products_variants.barcode if multi_order_type.frames_products_variants.id else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>ABox</FieldName>
                                                <FieldValue>''' + str(multi_order_type.a_lab_details if multi_order_type.a_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>BBox</FieldName>
                                                <FieldValue>''' + str(multi_order_type.b_lab_details if multi_order_type.b_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>Dbl</FieldName>
                                                <FieldValue>''' + str(multi_order_type.dbl_lab_details if multi_order_type.dbl_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>ED</FieldName>
                                                <FieldValue>''' + str(multi_order_type.ed_lab_details if multi_order_type.ed_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>Patient_initials</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>HE_coeff</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>ST_coeff</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>Progression_Length</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>VertexDistance</FieldName>
                                                <FieldValue>''' + str(multi_order_type.vertex_mlab_details if multi_order_type.vertex_mlab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>WrapAngle</FieldName>
                                                <FieldValue>''' + str(multi_order_type.wrap_lab_details if multi_order_type.wrap_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>PantoAngle</FieldName>
                                                <FieldValue>''' + str(multi_order_type.panto_lab_details if multi_order_type.panto_lab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>SeeProudRightInset</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>SeeProudLeftInset</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RightVertexDistance</FieldName>
                                                <FieldValue>''' + str(multi_order_type.vertex_mlab_details if multi_order_type.vertex_mlab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LeftVertexDistance</FieldName>
                                                <FieldValue>''' + str(multi_order_type.vertex_mlab_details if multi_order_type.vertex_mlab_details else '') + '''</FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>ReadingDistance</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>RightERCD</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>LeftERCD</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>CAPE</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                              <Item>
                                                <FieldName>DominantEye</FieldName>
                                                <FieldValue></FieldValue>
                                              </Item>
                                            </VWOrder>
                                         ]]></ser:filestring>
                                         <ser:subordid>''' + str(multi_order_type.id) + '''</ser:subordid>
                                         <ser:refid>''' + general_settings[3] + '''</ser:refid>
                                         <ser:guid></ser:guid>
                                         <ser:msgguid>''' + str(uuid.uuid1()) + '''</ser:msgguid>
                                         <ser:sloid>''' + "9901" + '''</ser:sloid>
                                         <ser:cbsid></ser:cbsid>
                                         <ser:ordtype></ser:ordtype>
                                         <ser:filename></ser:filename>
                                      </ser:UploadFile>
                                   </soapenv:Body>
                                </soapenv:Envelope>'''
                    link = requests.post('http://services.visionwebqa.com/FileUpload.asmx', data=raw_data, headers=headers)
                    return_statement = ''
                    if link.status_code == 200:
                        tree = ET.fromstring(link.text)
                        if len(tree.findall(".//{http://services.visionweb.com}UploadFileResult")) >= 1:
                            response = ET.fromstring(tree.findall(".//{http://services.visionweb.com}UploadFileResult")[0].text)
                            if response.tag == 'ERROR_MESSAGE':
                                return_statement = ("Error code: " + response.findall('.//ERROR')[0].attrib['Code'] if "Code" in response.findall('.//ERROR')[0].attrib else '')+ "<br/> Description: " + \
                                                   (response.findall('.//ERROR')[0].attrib['Desc'] if 'Desc' in response.findall('.//ERROR')[0].attrib else response.findall('.//ERROR')[0].text)
                            else:
                                if len(response.findall(".//VWebOrderId")):
                                    multi_order_type.vw_order_id = response.findall(".//VWebOrderId")[0].text
                                    return_statement += response.findall(".//VWebOrderId")[0].text + "<br/>"
                                if len(response.findall(".//SentDate")):
                                    return_statement += "Data sent at " + response.findall(".//SentDate")[0].text
                                if len(response.findall(".//Status")):
                                    return_statement += "<br/>with status of '" + response.findall(".//Status")[0].text + "'"
                                if len(response.findall(".//ErrorList")):
                                    return_statement += "<br/><b>Errors</b><br/>"
                                    if response.findall(".//ErrorList")[0].text.find('FrameType:FrameType is required') == 88 and multi_order_type.frame_type.id and not(multi_order_type.frame_type.vw_code != '' and multi_order_type.frame_type.vw_code):
                                        return_statement += "0. no vwcode available for this frame type.<br/>"
                                    return_statement += response.findall(".//ErrorList")[0].text.replace("\n", "<br/>")
                        return_statements += "<br/> *) Details: " + return_statement
                    else:
                        return_statements += "<br/> *) invalid response from visionweb, try again later."
                except Exception as e:
                    return_statements += '<br/> *) Odoo Internal Server Error or Api Connection Error'
                    return_statements += '<br/> *) No data Transmitted to "' + (multi_order_type.lab_details.name if multi_order_type.lab_details.id else '' ) + '"'
        return return_statements

    def order_tracking(self, id):
        general_settings = self.get_visionweb_config()
        multi_order_type = self.env['multi.order.type'].search([('id', '=', int(id))])
        try:
            headers = {'Content-Type': 'text/xml'}
            raw_data = '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://services.visionweb.com">
                        <soapenv:Header/>
                        <soapenv:Body>
                            <ser:GetTracking>
                                <ser:orderId>''' + multi_order_type.vw_order_id + '''</ser:orderId>
                                <ser:username>''' + general_settings[1] + '''</ser:username>
                                <ser:password>''' + general_settings[2] + '''</ser:password>
                                <ser:refid>''' + general_settings[3] + '''</ser:refid>
                            </ser:GetTracking>
                        </soapenv:Body>
                    </soapenv:Envelope>'''
            link = requests.post('https://services.visionwebqa.com/VWOrderTracking.asmx', data=raw_data, headers=headers)
            return_statement = ''
            if link.status_code == 200:
                tree = ET.fromstring(link.text)
                if len(tree.findall(".//{http://services.visionweb.com}GetTrackingResult")) >= 1:
                    response = ET.fromstring(tree.findall(".//{http://services.visionweb.com}GetTrackingResult")[0].text)
                    if response.tag == 'ERROR_MESSAGE':
                        return_statement = ("Error code: " + response[0].attrib['Code'])if 'Code' in response[0].attrib \
                                            else '' + "<br/> Description: " + response[0].text
                    else:
                        if len(response.findall(".//STATUS_DESCRIPTION")):
                            return_statement = "Order Status <br/>" + response.findall(".//STATUS_DESCRIPTION")[0].text
                        if len(response.findall(".//ITEM")):
                            if 'Visionweb_Tracking_Id' in response.findall(".//ITEM")[0].attrib:
                                return_statement += "Visionweb Tracking Id: " + response.findall(".//ITEM")[0].attrib['Visionweb_Tracking_Id'] + "<br/>"
                            if 'Type' in response.findall(".//ITEM")[0].attrib:
                                return_statement += "Type: " + response.findall(".//ITEM")[0].attrib['Type'] + "<br/>"
                            if 'Status' in response.findall(".//ITEM")[0].attrib:
                                multi_order_type.vw_order_status = response.findall(".//ITEM")[0].attrib['Status']
                                return_statement += "Status: " + response.findall(".//ITEM")[0].attrib['Status'] + "<br/>"
                            if 'Tracking_Id' in response.findall(".//ITEM")[0].attrib:
                                return_statement += "Tracking Id: " + response.findall(".//ITEM")[0].attrib['Tracking_Id'] + "<br/>"
                            if 'Received_at' in response.findall(".//ITEM")[0].attrib:
                                return_statement += "Received at: " + response.findall(".//ITEM")[0].attrib['Received_at'] + "<br/>"
                    return return_statement
                else:
                    return "Invalid response from visionweb"
        except:
            return "error finding status for this order."
