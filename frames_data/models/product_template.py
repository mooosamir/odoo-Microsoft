# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class FramesData(models.Model):
    _inherit = 'product.template'

    frames_data_link = fields.Char(string='frames data image', compute='_compute_frames_data_link')

    def _compute_frames_data_link(self):
        general_settings = self.env['frames.data'].get_token()
        for record in self:
            record.frames_data_link = ''
            if record.categ_id.name == 'Frames':
                if record.sfmid:
                    record.frames_data_link = str(general_settings[0]) + "api/images?auth=" + str(general_settings[1]) + '&size=small&id=' + str(record.sfmid)

    def fd_synchronize(self, records, record):
        if record.categ_id.name == 'Frames':
            error_response = ""
            for data in records:
                if data.sfmid and data.sfmid != '':
                    style = self.env['frames.data'].get_styles_by_sfmid(data.sfmid)
                    if style:
                        style = style[0]
                        spec_collection_collection_id = self.env['spec.collection.collection'].search(
                            [('cfmid', '=', int(style['CollectionFramesMasterID']))], limit=1)
                        spec_frame_material_id = self.env['spec.frame.material'].search(
                            [('name', '=', style['Material'])], limit=1)
                        if not spec_frame_material_id.id:
                            spec_frame_material_id = self.env['spec.frame.material'].create({
                                'name': style['Material'],
                            })
                        spec_shape_shape_id = self.env['spec.shape.shape'].search([('name', '=', style['Shape'])],
                                                                                  limit=1)
                        if not spec_shape_shape_id.id:
                            spec_shape_shape_id = self.env['spec.shape.shape'].create({
                                'name': style['Shape'],
                            })
                        spec_gender_type_id = self.env['spec.gender.type'].search([('name', '=', style['GenderType'])],
                                                                                  limit=1)
                        if not spec_gender_type_id.id:
                            spec_gender_type_id = self.env['spec.gender.type'].create({
                                'name': style['GenderType'],
                            })
                        age = ''
                        if style['Age'] == 'Adult':
                            age = 'adult'
                        elif style['Age'] == 'Child':
                            age = 'child'
                        elif style['Age'] == 'Youth/Teen':
                            age = 'youth_teen'
                        elif style['Age'] == 'Infant':
                            age = 'infant'
                        elif style['Age'] == 'Child & Adult':
                            age = 'child_adult'
                        spec_frame_type_id = self.env['spec.frame.type'].search([('name', '=', style['FrameType'])],
                                                                                limit=1)
                        if not spec_frame_type_id.id:
                            spec_frame_type_id = self.env['spec.frame.type'].create({
                                'name': style['FrameType'],
                            })
                        rim = ''
                        if style['Rim'] == '3-Piece Compression':
                            rim = 'piece_compression'
                        elif style['Rim'] == '3-Piece Screw':
                            rim = 'piece_screw'
                        elif style['Rim'] == 'Full Rim':
                            rim = 'full_rim'
                        elif style['Rim'] == 'Half Rim':
                            rim = 'half_Rim'
                        elif style['Rim'] == 'Inverted Half Rim':
                            rim = 'inverted_half_Rim'
                        elif style['Rim'] == 'None':
                            rim = 'none'
                        elif style['Rim'] == 'Other':
                            rim = 'other'
                        elif style['Rim'] == 'Semi-Rimless':
                            rim = 'semi_rimless'
                        elif style['Rim'] == 'Shield':
                            rim = 'shield'
                        edge = ''
                        if style['EdgeType'] == 'drill-mount':
                            edge = 'drill_mount'
                        else:
                            edge = style['EdgeType']
                        bridge = ''
                        if style['Bridge'] == 'Adjustable nose pads':
                            bridge = 'adjustable_nose_pads'
                        elif style['Bridge'] == 'Double':
                            bridge = 'double'
                        elif style['Bridge'] == 'Keyhole':
                            bridge = 'keyhole'
                        elif style['Bridge'] == 'Other':
                            bridge = 'other'
                        elif style['Bridge'] == 'Saddle':
                            bridge = 'saddle'
                        elif style['Bridge'] == 'Single bridge':
                            bridge = 'single_Bridge'
                        elif style['Bridge'] == 'Unifit':
                            bridge = 'unifit'
                        elif style['Bridge'] == 'Universal':
                            bridge = 'universal'
                        hinge = ''
                        if style['Hinge'] == 'Hingeless':
                            hinge = 'hingeless'
                        elif style['Hinge'] == 'Micro spring Hinge':
                            hinge = 'micro_spring_hinge'
                        elif style['Hinge'] == 'Regular Hinge':
                            hinge = 'regular_hinge'
                        elif style['Hinge'] == 'Screwless Hinge':
                            hinge = 'screwless_hinge'
                        elif style['Hinge'] == 'Spring Hinge':
                            hinge = 'spring_hinge'
                        spec_lenses_type_id = self.env['spec.lenses.type'].search([('name', '=', style['LensType'])],
                                                                                  limit=1)
                        if not spec_lenses_type_id.id:
                            spec_lenses_type_id = self.env['spec.lenses.type'].create({
                                'name': style['LensType'],
                            })
                        rx = ''
                        if style['RX'] == 'Other':
                            rx = 'other'
                        elif style['RX'] == 'Prescription available & Rx adaptable.':
                            rx = 'prescription_available_adaptable'
                        elif style['RX'] == 'Prescription available.':
                            rx = 'prescription_adaptable'
                        elif style['RX'] == 'Rx adaptable.':
                            rx = 'rx_daptable.'
                        clip = ''
                        if style['ClipOnOption'] == 'Available as a Sunglass.':
                            clip = 'available_sunglass.'
                        elif style['ClipOnOption'] == 'Clip-on Available':
                            clip = 'clip_available'
                        elif style['ClipOnOption'] == 'Clip-on included.':
                            clip = 'clip_included'
                        elif style['ClipOnOption'] == 'Magnetic clip-on available':
                            clip = 'magnetic_clip_available'
                        elif style['ClipOnOption'] == 'Magnetic clip-on included.':
                            clip = 'magnetic_clip_included'
                        elif style['ClipOnOption'] == 'Other':
                            clip = 'other'
                        side = ''
                        if style['Sideshields'] == 'Detachable':
                            side = 'detachable'
                        elif style['Sideshields'] == 'Flat fold':
                            side = 'flat_fold'
                        elif style['Sideshields'] == 'Other':
                            side = 'other'
                        elif style['Sideshields'] == 'Permanent':
                            side = 'permanent'
                        warranty = ''
                        if style['Warranty'] == '1-year warranty.':
                            warranty = '1_year_arranty'
                        elif style['Warranty'] == '2-year warranty.':
                            warranty = '2_year_arranty'
                        elif style['Warranty'] == '3-year warranty.':
                            warranty = '3_year_arranty'
                        elif style['Warranty'] == 'Lifetime warranty on manufacturer’s defects':
                            warranty = 'lifetime_year_arranty'
                        elif style['Warranty'] == 'Material defects or workmanship: 12 month warranty.':
                            warranty = '12_year_arranty'
                        elif style['Warranty'] == 'Material defects or workmanship: 24 month warranty.':
                            warranty = '24_year_arranty'
                        elif style['Warranty'] == 'Other':
                            warranty = 'other'
                        elif style['Warranty'] == 'Unconditional lifetime warranty.':
                            warranty = 'unconditional_year_arranty'
                        self.browse(data.id).update({
                            'material_frame_id': spec_frame_material_id.id,
                            'shap_id': spec_shape_shape_id.id,
                            'gender_ids': spec_gender_type_id.id,
                            'age': age if age != '' else None,
                            'frame_type_id': spec_frame_type_id.id,
                            'rim': rim if rim != '' else None,
                            'edge_type': edge if edge != '' else None,
                            'bridge_fix': bridge if bridge != '' else None,
                            'hinge': hinge if hinge != '' else None,
                            'lenses': spec_lenses_type_id.id,
                            'rx': rx if rx != '' else None,
                            'clip_on_option': clip if clip != '' else None,
                            'side_shields': side if side != '' else None,
                            'warranty': warranty if warranty != '' else None,
                            'is_sunclass': True if style['Sunglasses'] == 'Sunglasses' else False,
                            'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                            'discontinue': True if style['StyleStatus'] == 'D' else False,
                            'discont_date': fields.datetime.strptime(style['StyleDiscontinuedOn'],'%m/%d/%Y') if style['StyleStatus'] == 'D' else None,
                            'frames_data_last_sync': fields.datetime.now().date(),
                        })

                    configurations = self.env['frames.data'].get_configurations_by_sfmid(data.sfmid)
                    if configurations:
                        for configuration in configurations[0]:
                            spec_color_family_id = self.env['spec.color.family'].search(
                                [('name', '=', configuration['Color'])], limit=1)
                            if not spec_color_family_id.id:
                                spec_color_family_id = self.env['spec.color.family'].create({
                                    'name': configuration['Color'],
                                })
                            spec_color_code_family_id = self.env['spec.color.code.family'].search(
                                [('name', '=', configuration['ColorCode'])], limit=1)
                            if not spec_color_code_family_id.id:
                                spec_color_code_family_id = self.env['spec.color.code.family'].create({
                                    'name': configuration['ColorCode'],
                                })
                            spec_lens_colors_id = self.env['spec.lens.colors'].search(
                                [('name', '=', configuration['LensColor'])], limit=1)
                            if not spec_lens_colors_id.id:
                                spec_lens_colors_id = self.env['spec.lens.colors'].create({
                                    'name': configuration['LensColor'],
                                })
                            product_product_id = self.env['product.product'].search(
                                [('barcode', '=', configuration['UPC']), ('product_tmpl_id', '=', data.id)], limit=1)
                            if product_product_id:
                                product_product_id.update({
                                    'eye': configuration['Eye'],
                                    'bridge': configuration['Bridge'],
                                    'temple': configuration['Temple'],
                                    'color_id': spec_color_family_id.id,
                                    'color_code_id': spec_color_code_family_id.id,
                                    'lens_color_id': spec_lens_colors_id.id,
                                    'a': float(configuration['A']) if configuration['A'] else 0,
                                    'b': float(configuration['B']) if configuration['B'] else 0,
                                    'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                                    'ed': float(configuration['ED']) if configuration['ED'] else 0,
                                    'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                                    'barcode': configuration['UPC'],
                                    'default_code': configuration['SKU'],
                                    'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                                    'list_price': float(configuration['SalePrice']) if configuration['SalePrice'] else 0,
                                    'configurations_last_modified_on': fields.datetime.now().date(),
                                })
                            else:
                                product_product_id = self.env['product.product'].with_context(disable_varients=True, create_product_product=False).create({
                                    # 'name': spec_collection_collection_id.name + " " + style['StyleName'] + "(" + configuration['UPC'] + ")",
                                    'eye': configuration['Eye'],
                                    'bridge': configuration['Bridge'],
                                    'temple': configuration['Temple'],
                                    'color_id': spec_color_family_id.id,
                                    'color_code_id': spec_color_code_family_id.id,
                                    'lens_color_id': spec_lens_colors_id.id,
                                    'a': float(configuration['A']) if configuration['A'] else 0,
                                    'b': float(configuration['B']) if configuration['B'] else 0,
                                    'dbl': float(configuration['DBL']) if configuration['DBL'] else 0,
                                    'ed': float(configuration['ED']) if configuration['ED'] else 0,
                                    'ed_angle': float(configuration['EDAngle']) if configuration['EDAngle'] else 0,
                                    'barcode': configuration['UPC'],
                                    'default_code': configuration['SKU'],
                                    # 'list_price': float(configuration['Retail']) if configuration['Retail'] else 0,
                                    'product_tmpl_id': data.id,
                                    'lens_discontinue': True if configuration['Discontinued'] == 'D' else False,
                                    'list_price': float(configuration['SalePrice']) if configuration['SalePrice'] else 0,
                                    'configurations_last_modified_on': fields.datetime.now().date(),
                                })
                else:
                    error_response +="StyleFramesMasterId not available for " + data.name + "\n"
            if error_response != "":
                raise exceptions.Warning(error_response)
        else:
            raise exceptions.Warning("Only frame data synchronize available.")
