# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import date
# from duplicity.tempdir import default
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, exceptions

_logger = logging.getLogger(__name__)

created = False

sphere_list = [('-30.00', '-30.00'), ('-29.75', '-29.75'), ('-29.50', '-29.50'), ('-29.25', '-29.25'), ('-29.00', '-29.00'), ('-28.75', '-28.75'), ('-28.50', '-28.50'), ('-28.25', '-28.25'), ('-28.00', '-28.00'),
('-27.75', '-27.75'), ('-27.50', '-27.50'), ('-27.25', '-27.25'), ('-27.00', '-27.00'), ('-26.75', '-26.75'), ('-26.50', '-26.50'), ('-26.25', '-26.25'), ('-26.00', '-26.00'), ('-25.75', '-25.75'),
('-25.50', '-25.50'), ('-25.25', '-25.25'), ('-25.00', '-25.00'), ('-24.75', '-24.75'), ('-24.50', '-24.50'), ('-24.25', '-24.25'), ('-24.00', '-24.00'), ('-23.75', '-23.75'), ('-23.50', '-23.50'),
('-23.25', '-23.25'), ('-23.00', '-23.00'), ('-22.75', '-22.75'), ('-22.50', '-22.50'), ('-22.25', '-22.25'), ('-22.00', '-22.00'), ('-21.75', '-21.75'), ('-21.50', '-21.50'), ('-21.25', '-21.25'),
('-21.00', '-21.00'), ('-20.75', '-20.75'), ('-20.50', '-20.50'), ('-20.25', '-20.25'), ('-20.00', '-20.00'), ('-19.75', '-19.75'), ('-19.50', '-19.50'), ('-19.25', '-19.25'), ('-19.00', '-19.00'),
('-18.75', '-18.75'), ('-18.50', '-18.50'), ('-18.25', '-18.25'), ('-18.00', '-18.00'), ('-17.75', '-17.75'), ('-17.50', '-17.50'), ('-17.25', '-17.25'), ('-17.00', '-17.00'), ('-16.75', '-16.75'),
('-16.50', '-16.50'), ('-16.25', '-16.25'), ('-16.00', '-16.00'), ('-15.75', '-15.75'), ('-15.50', '-15.50'), ('-15.25', '-15.25'), ('-15.00', '-15.00'), ('-14.75', '-14.75'), ('-14.50', '-14.50'),
('-14.25', '-14.25'), ('-14.00', '-14.00'), ('-13.75', '-13.75'), ('-13.50', '-13.50'), ('-13.25', '-13.25'), ('-13.00', '-13.00'), ('-12.75', '-12.75'), ('-12.50', '-12.50'), ('-12.25', '-12.25'),
('-12.00', '-12.00'), ('-11.75', '-11.75'), ('-11.50', '-11.50'), ('-11.25', '-11.25'), ('-11.00', '-11.00'), ('-10.75', '-10.75'), ('-10.50', '-10.50'), ('-10.25', '-10.25'), ('-10.00', '-10.00'),
('-9.75', '-9.75'), ('-9.50', '-9.50'), ('-9.25', '-9.25'), ('-9.00', '-9.00'), ('-8.75', '-8.75'), ('-8.50', '-8.50'), ('-8.25', '-8.25'), ('-8.00', '-8.00'), ('-7.75', '-7.75'), ('-7.50', '-7.50'),
('-7.25', '-7.25'), ('-7.00', '-7.00'), ('-6.75', '-6.75'), ('-6.50', '-6.50'), ('-6.25', '-6.25'), ('-6.00', '-6.00'), ('-5.75', '-5.75'), ('-5.50', '-5.50'), ('-5.25', '-5.25'), ('-5.00', '-5.00'),
('-4.75', '-4.75'), ('-4.50', '-4.50'), ('-4.25', '-4.25'), ('-4.00', '-4.00'), ('-3.75', '-3.75'), ('-3.50', '-3.50'), ('-3.25', '-3.25'), ('-3.00', '-3.00'), ('-2.75', '-2.75'), ('-2.50', '-2.50'),
('-2.25', '-2.25'), ('-2.00', '-2.00'), ('-1.75', '-1.75'), ('-1.50', '-1.50'), ('-1.25', '-1.25'), ('-1.00', '-1.00'), ('-0.75', '-0.75'), ('-0.50', '-0.50'), ('-0.25', '-0.25'), ('0.00', '+0.00'),
('0.25', '+0.25'), ('0.50', '+0.50'), ('0.75', '+0.75'), ('1.00', '+1.00'), ('1.25', '+1.25'), ('1.50', '+1.50'), ('1.75', '+1.75'), ('2.00', '+2.00'), ('2.25', '+2.25'), ('2.50', '+2.50'),
('2.75', '+2.75'), ('3.00', '+3.00'), ('3.25', '+3.25'), ('3.50', '+3.50'), ('3.75', '+3.75'), ('4.00', '+4.00'), ('4.25', '+4.25'), ('4.50', '+4.50'), ('4.75', '+4.75'), ('5.00', '+5.00'),
('5.25', '+5.25'), ('5.50', '+5.50'), ('5.75', '+5.75'), ('6.00', '+6.00'), ('6.25', '+6.25'), ('6.50', '+6.50'), ('6.75', '+6.75'), ('7.00', '+7.00'), ('7.25', '+7.25'), ('7.50', '+7.50'),
('7.75', '+7.75'), ('8.00', '+8.00'), ('8.25', '+8.25'), ('8.50', '+8.50'), ('8.75', '+8.75'), ('9.00', '+9.00'), ('9.25', '+9.25'), ('9.50', '+9.50'), ('9.75', '+9.75'), ('10.00', '+10.00'),
('10.25', '+10.25'), ('10.50', '+10.50'), ('10.75', '+10.75'), ('11.00', '+11.00'), ('11.25', '+11.25'), ('11.50', '+11.50'), ('11.75', '+11.75'), ('12.00', '+12.00'), ('12.25', '+12.25'),
('12.50', '+12.50'), ('12.75', '+12.75'), ('13.00', '+13.00'), ('13.25', '+13.25'), ('13.50', '+13.50'), ('13.75', '+13.75'), ('14.00', '+14.00'), ('14.25', '+14.25'), ('14.50', '+14.50'),
('14.75', '+14.75'), ('15.00', '+15.00'), ('15.25', '+15.25'), ('15.50', '+15.50'), ('15.75', '+15.75'), ('16.00', '+16.00'), ('16.25', '+16.25'), ('16.50', '+16.50'), ('16.75', '+16.75'),
('17.00', '+17.00'), ('17.25', '+17.25'), ('17.50', '+17.50'), ('17.75', '+17.75'), ('18.00', '+18.00'), ('18.25', '+18.25'), ('18.50', '+18.50'), ('18.75', '+18.75'), ('19.00', '+19.00'),
('19.25', '+19.25'), ('19.50', '+19.50'), ('19.75', '+19.75'), ('20.00', '+20.00'), ('20.25', '+20.25'), ('20.50', '+20.50'), ('20.75', '+20.75'), ('21.00', '+21.00'), ('21.25', '+21.25'),
('21.50', '+21.50'), ('21.75', '+21.75'), ('22.00', '+22.00'), ('22.25', '+22.25'), ('22.50', '+22.50'), ('22.75', '+22.75'), ('23.00', '+23.00'), ('23.25', '+23.25'), ('23.50', '+23.50'),
('23.75', '+23.75'), ('24.00', '+24.00'), ('24.25', '+24.25'), ('24.50', '+24.50'), ('24.75', '+24.75'), ('25.00', '+25.00'), ('25.25', '+25.25'), ('25.50', '+25.50'), ('25.75', '+25.75'),
('26.00', '+26.00'), ('26.25', '+26.25'), ('26.50', '+26.50'), ('26.75', '+26.75'), ('27.00', '+27.00'), ('27.25', '+27.25'), ('27.50', '+27.50'), ('27.75', '+27.75'), ('28.00', '+28.00'),
('28.25', '+28.25'), ('28.50', '+28.50'), ('28.75', '+28.75'), ('29.00', '+29.00'), ('29.25', '+29.25'), ('29.50', '+29.50'), ('29.75', '+29.75'), ('30.00', '+30.00')]
cylinder_list = [('-20.00', '-20.00'), ('-19.75', '-19.75'), ('-19.50', '-19.50'), ('-19.25', '-19.25'), ('-19.00', '-19.00'),
('-18.75', '-18.75'), ('-18.50', '-18.50'), ('-18.25', '-18.25'), ('-18.00', '-18.00'), ('-17.75', '-17.75'), ('-17.50', '-17.50'), ('-17.25', '-17.25'), ('-17.00', '-17.00'), ('-16.75', '-16.75'),
('-16.50', '-16.50'), ('-16.25', '-16.25'), ('-16.00', '-16.00'), ('-15.75', '-15.75'), ('-15.50', '-15.50'), ('-15.25', '-15.25'), ('-15.00', '-15.00'), ('-14.75', '-14.75'), ('-14.50', '-14.50'),
('-14.25', '-14.25'), ('-14.00', '-14.00'), ('-13.75', '-13.75'), ('-13.50', '-13.50'), ('-13.25', '-13.25'), ('-13.00', '-13.00'), ('-12.75', '-12.75'), ('-12.50', '-12.50'), ('-12.25', '-12.25'),
('-12.00', '-12.00'), ('-11.75', '-11.75'), ('-11.50', '-11.50'), ('-11.25', '-11.25'), ('-11.00', '-11.00'), ('-10.75', '-10.75'), ('-10.50', '-10.50'), ('-10.25', '-10.25'), ('-10.00', '-10.00'),
('-9.75', '-9.75'), ('-9.50', '-9.50'), ('-9.25', '-9.25'), ('-9.00', '-9.00'), ('-8.75', '-8.75'), ('-8.50', '-8.50'), ('-8.25', '-8.25'), ('-8.00', '-8.00'), ('-7.75', '-7.75'), ('-7.50', '-7.50'),
('-7.25', '-7.25'), ('-7.00', '-7.00'), ('-6.75', '-6.75'), ('-6.50', '-6.50'), ('-6.25', '-6.25'), ('-6.00', '-6.00'), ('-5.75', '-5.75'), ('-5.50', '-5.50'), ('-5.25', '-5.25'), ('-5.00', '-5.00'),
('-4.75', '-4.75'), ('-4.50', '-4.50'), ('-4.25', '-4.25'), ('-4.00', '-4.00'), ('-3.75', '-3.75'), ('-3.50', '-3.50'), ('-3.25', '-3.25'), ('-3.00', '-3.00'), ('-2.75', '-2.75'), ('-2.50', '-2.50'),
('-2.25', '-2.25'), ('-2.00', '-2.00'), ('-1.75', '-1.75'), ('-1.50', '-1.50'), ('-1.25', '-1.25'), ('-1.00', '-1.00'), ('-0.75', '-0.75'), ('-0.50', '-0.50'), ('-0.25', '-0.25'), ('0.00', '+0.00'),
('0.25', '+0.25'), ('0.50', '+0.50'), ('0.75', '+0.75'), ('1.00', '+1.00'), ('1.25', '+1.25'), ('1.50', '+1.50'), ('1.75', '+1.75'), ('2.00', '+2.00'), ('2.25', '+2.25'), ('2.50', '+2.50'),
('2.75', '+2.75'), ('3.00', '+3.00'), ('3.25', '+3.25'), ('3.50', '+3.50'), ('3.75', '+3.75'), ('4.00', '+4.00'), ('4.25', '+4.25'), ('4.50', '+4.50'), ('4.75', '+4.75'), ('5.00', '+5.00'),
('5.25', '+5.25'), ('5.50', '+5.50'), ('5.75', '+5.75'), ('6.00', '+6.00'), ('6.25', '+6.25'), ('6.50', '+6.50'), ('6.75', '+6.75'), ('7.00', '+7.00'), ('7.25', '+7.25'), ('7.50', '+7.50'),
('7.75', '+7.75'), ('8.00', '+8.00'), ('8.25', '+8.25'), ('8.50', '+8.50'), ('8.75', '+8.75'), ('9.00', '+9.00'), ('9.25', '+9.25'), ('9.50', '+9.50'), ('9.75', '+9.75'), ('10.00', '+10.00'),
('10.25', '+10.25'), ('10.50', '+10.50'), ('10.75', '+10.75'), ('11.00', '+11.00'), ('11.25', '+11.25'), ('11.50', '+11.50'), ('11.75', '+11.75'), ('12.00', '+12.00'), ('12.25', '+12.25'),
('12.50', '+12.50'), ('12.75', '+12.75'), ('13.00', '+13.00'), ('13.25', '+13.25'), ('13.50', '+13.50'), ('13.75', '+13.75'), ('14.00', '+14.00'), ('14.25', '+14.25'), ('14.50', '+14.50'),
('14.75', '+14.75'), ('15.00', '+15.00'), ('15.25', '+15.25'), ('15.50', '+15.50'), ('15.75', '+15.75'), ('16.00', '+16.00'), ('16.25', '+16.25'), ('16.50', '+16.50'), ('16.75', '+16.75'),
('17.00', '+17.00'), ('17.25', '+17.25'), ('17.50', '+17.50'), ('17.75', '+17.75'), ('18.00', '+18.00'), ('18.25', '+18.25'), ('18.50', '+18.50'), ('18.75', '+18.75'), ('19.00', '+19.00'),
('19.25', '+19.25'), ('19.50', '+19.50'), ('19.75', '+19.75'), ('20.00', '+20.00')]
axis_list = [('1', '001'), ('2', '002'), ('3', '003'), ('4', '004'), ('5', '005'), ('6', '006'), ('7', '007'), ('08', '008'), ('09', '009'), ('10', '010'), ('11', '011'), ('12', '012'),
('13', '013'), ('14', '014'), ('15', '015'), ('16', '016'), ('17', '017'), ('18', '018'), ('19', '019'), ('20', '020'), ('21', '021'), ('22', '022'), ('23', '023'), ('24', '024'),
('25', '025'), ('26', '026'), ('27', '027'), ('28', '028'), ('29', '029'), ('30', '030'), ('31', '031'), ('32', '032'), ('33', '033'), ('34', '034'), ('35', '035'), ('36', '036'),
('37', '037'), ('38', '038'), ('39', '039'), ('40', '040'), ('41', '041'), ('42', '042'), ('43', '043'), ('44', '044'), ('45', '045'), ('46', '046'), ('47', '047'), ('48', '048'),
('49', '049'), ('050', '050'), ('51', '051'), ('52', '052'), ('53', '053'), ('54', '054'), ('55', '055'), ('56', '056'), ('57', '057'), ('58', '058'), ('59', '059'), ('60', '060'),
('61', '061'), ('62', '062'), ('63', '063'), ('64', '064'), ('65', '065'), ('66', '066'), ('67', '067'), ('68', '068'), ('69', '069'), ('70', '070'), ('71', '071'), ('72', '072'),
('73', '073'), ('74', '074'), ('75', '075'), ('76', '076'), ('77', '077'), ('78', '078'), ('79', '079'), ('80', '080'), ('81', '081'), ('82', '082'), ('83', '083'), ('84', '084'),
('85', '085'), ('86', '086'), ('87', '087'), ('88', '088'), ('89', '089'), ('90', '090'), ('91', '091'), ('92', '092'), ('93', '093'), ('094', '094'), ('95', '095'), ('096', '096'),
('97', '097'), ('98', '098'), ('99', '099'), ('100', '100'), ('101', '101'), ('102', '102'), ('103', '103'), ('104', '104'), ('105', '105'), ('106', '106'), ('107', '107'), ('108', '108'),
('109', '109'), ('110', '110'), ('111', '111'), ('112', '112'), ('113', '113'), ('114', '114'), ('115', '115'), ('116', '116'), ('117', '117'), ('118', '118'), ('119', '119'), ('120', '120'),
('121', '121'), ('122', '122'), ('123', '123'), ('124', '124'), ('125', '125'), ('126', '126'), ('127', '127'), ('128', '128'), ('129', '129'), ('130', '130'), ('131', '131'), ('132', '132'),
('133', '133'), ('134', '134'), ('135', '135'), ('136', '136'), ('137', '137'), ('138', '138'), ('139', '139'), ('140', '140'), ('141', '141'), ('142', '142'), ('143', '143'), ('144', '144'),
('145', '145'), ('146', '146'), ('147', '147'), ('148', '148'), ('149', '149'), ('150', '150'), ('151', '151'), ('152', '152'), ('153', '153'), ('154', '154'), ('155', '155'), ('156', '156'),
('157', '157'), ('158', '158'), ('159', '159'), ('160', '160'), ('161', '161'), ('162', '162'), ('163', '163'), ('164', '164'), ('165', '165'), ('166', '166'), ('167', '167'), ('168', '168'),
('169', '169'), ('170', '170'), ('171', '171'), ('172', '172'), ('173', '173'), ('174', '174'), ('175', '175'), ('176', '176'), ('177', '177'), ('178', '178'), ('179', '179'), ('180', '180')]
add_list = [('0.00', '+0.00'),('0.25', '+0.25'), ('0.50', '+0.50'), ('0.75', '+0.75'), ('1.00', '+1.00'), ('1.25', '+1.25'), ('1.50', '+1.50'), ('1.75', '+1.75'), ('2.00', '+2.00'), ('2.25', '+2.25'),
('2.50', '+2.50'), ('2.75', '+2.75'), ('3.00', '+3.00'), ('3.25', '+3.25'), ('3.50', '+3.50'), ('3.75', '+3.75'), ('4.00', '+4.00'), ('4.25', '+4.25'), ('4.50', '+4.50'), ('4.75', '+4.75'), ('5.00', '+5.00'),
('5.25', '+5.25'), ('5.50', '+5.50'), ('5.75', '+5.75'), ('6.00', '+6.00')]


class MultiOrderTypes(models.Model):
    _name = "multi.order.type"
    _description = "multi.order.type"
    _rec_name = 'order_type_name'
    _order = 'create_date desc'

    def _contact_lens_reorder(self):
        for res in self:
            contact_lens_products = None
            qty = 0
            if res.contact_lens_products_os.replacement_schedule_id.id or res.contact_lens_products_od.replacement_schedule_id.id:
                if res.contact_lens_products_os.replacement_schedule_id.code <= res.contact_lens_products_od.replacement_schedule_id.code:
                    contact_lens_products = res.contact_lens_products_os
                elif res.contact_lens_products_os.replacement_schedule_id.code > res.contact_lens_products_od.replacement_schedule_id.code:
                    contact_lens_products = res.contact_lens_products_od
                qty = (res.od_qty + res.os_qty) / 2
                package = 0

                if res.sale_order_id.id:
                    if contact_lens_products.uom_id.name in ['1 Blister', 'Single']:
                        package = 1
                    elif contact_lens_products.uom_id.name == '2 pack':
                        package = 2
                    elif contact_lens_products.uom_id.name == '3 pack':
                        package = 3
                    elif contact_lens_products.uom_id.name == '4 pack':
                        package = 4
                    elif contact_lens_products.uom_id.name == '5 pack':
                        package = 5
                    elif contact_lens_products.uom_id.name == '6 pack':
                        package = 6
                    elif contact_lens_products.uom_id.name == '10 pack':
                        package = 10
                    elif contact_lens_products.uom_id.name == '12 pack':
                        package = 12
                    elif contact_lens_products.uom_id.name == '24 pack':
                        package = 24
                    elif contact_lens_products.uom_id.name == '30 pack':
                        package = 30
                    elif contact_lens_products.uom_id.name == '90 pack':
                        package = 90

                    multiply = package * qty
                    if contact_lens_products.replacement_schedule_id.name == 'Daily':
                        res.contact_lens_reorder = res.sale_order_date_order + relativedelta(days=1 * multiply)
                    elif contact_lens_products.replacement_schedule_id.name == '2 Week':
                        res.contact_lens_reorder = res.sale_order_date_order + relativedelta(days=14 * multiply)
                    elif contact_lens_products.replacement_schedule_id.name == '1 Month':
                        res.contact_lens_reorder = res.sale_order_date_order + relativedelta(months=1 * multiply)
                    elif contact_lens_products.replacement_schedule_id.name == '3 Month':
                        res.contact_lens_reorder = res.sale_order_date_order + relativedelta(months=3 * multiply)
                    elif contact_lens_products.replacement_schedule_id.name == '6 Month':
                        res.contact_lens_reorder = res.sale_order_date_order + relativedelta(months=6 * multiply)
                    elif contact_lens_products.replacement_schedule_id.name == 'Yearly':
                        res.contact_lens_reorder = res.sale_order_date_order + relativedelta(years=1 * multiply)
            else:
                res.contact_lens_reorder = None

    def _promised_date_range(self):
        for res in self:
            res.promised_date_1 = fields.date.today() + relativedelta(days=1)
            res.promised_date_2 = fields.date.today() + relativedelta(days=2)
            res.promised_date_3 = fields.date.today() + relativedelta(days=3)

    def partner_id_name(self):
        for res in self:
            if res.partner_id.id and len(res.partner_id.name_get()[0]) > 0:
                res.partner_name = res.partner_id.with_context(name_dob=1).name_get()[0][1]
            else:
                res.partner_name = ''
    # Text Decoration in Tree View
    promised_date_1 = fields.Date(compute="_promised_date_range")
    promised_date_2 = fields.Date(compute="_promised_date_range")
    promised_date_3 = fields.Date(compute="_promised_date_range")
    contact_lens_reorder = fields.Date(compute="_contact_lens_reorder")

    def get_default_lines(self):
        so_id = self.env['sale.order'].browse(self._context.get('so_id'))
        return so_id.partner_id.id

    def get_rx_domain(self):
        domain_rx = self._context.get('domain_rx')
        if domain_rx == 'glasses':
            return "('rx', '=', 'glasses')"
        elif domain_rx == 'soft,hard':
            return "('rx', 'in', ['soft','hard'])"
        else:
            return None

    @api.onchange('prescription_id')
    def check_visibility(self):
        # self.od_contact_lens_visibility = False
        # self.os_contact_lens_visibility = False
        # if self.prescription_id:
        #     if self.prescription_id.rx == 'soft':
        #         if self.select_soft_base_curve and \
        #                 self.select_soft_diameter and \
        #                 self.select_soft_sphere and \
        #                 self.select_soft_cylinder and \
        #                 self.select_soft_axis and \
        #                 self.select_soft_add_power and \
        #                 self.select_soft_multifocal:
        #             self.od_contact_lens_visibility = True
        #         if self.soft_left_base_curve and \
        #                 self.soft_left_diameter and \
        #                 self.soft_left_sphere and \
        #                 self.soft_left_cylinder and \
        #                 self.soft_left_axis and \
        #                 self.soft_left_add_power and \
        #                 self.soft_left_multifocal:
        #             self.os_contact_lens_visibility = True
        #     elif self.prescription_id.rx == 'hard':
        #         if self.base_curve and \
        #                 self.sphere and \
        #                 self.cylinder and \
        #                 self.axis and \
        #                 self.add:
        #             self.od_contact_lens_visibility = True
        #         if self.left_base_curve and \
        #                 self.left_sphere and \
        #                 self.left_cylinder and \
        #                 self.left_axis and \
        #                 self.left_add:
        #             self.os_contact_lens_visibility = True
        #     elif self.prescription_id.rx == 'glasses':
        #         if self.gls_sphere and \
        #                 self.gls_cylinder and \
        #                 self.gls_axis and \
        #                 self.gls_add:
        #             self.od_contact_lens_visibility = True
        #         if self.gls_left_lens_sphere and \
        #                 self.gls_left_lens_cylinder and \
        #                 self.gls_left_lens_axis and \
        #                 self.gls_left_lens_add:
        #             self.os_contact_lens_visibility = True

        self.od_contact_lens_visibility = True
        self.os_contact_lens_visibility = True

    @api.onchange('prescription_id')
    def get_od_lenses(self):
        prod_list_od = list()
        colors = list()
        for rec in self:
            if rec.order_type_name == "Contact Lens" and rec.prescription_id:
                if rec.prescription_id.rx == 'soft':
                    contact_lens_search = self.env['product.template'].search(
                        [('categ_id.name', '=', 'Contact Lens'),
                         ('contact_lens_manufacturer_id', '=', rec.soft_manufacturer_id.contact_lens_manufacturer_id.id)])
                         # ('name', '=', rec.soft_manufacturer_id.name)])
                if rec.prescription_id.rx == 'hard':
                    contact_lens_search = self.env['product.template'].search(
                        [('categ_id.name', '=', 'Contact Lens'),
                         ('contact_lens_manufacturer_id', '=', rec.manufacturer_id.contact_lens_manufacturer_id.id)])
                         # ('name', '=', rec.manufacturer_id.name)])
                for con in contact_lens_search:
                    if rec.prescription_id.rx == 'soft':
                        for ps in con.product_variant_ids.filtered(lambda x:
                                                                   x.bc == rec.select_soft_base_curve and
                                                                   x.diam == rec.select_soft_diameter and
                                                                   x.sphere == rec.select_soft_sphere and
                                                                   x.cylinder == rec.select_soft_cylinder and
                                                                   x.axis == rec.select_soft_axis and
                                                                   x.add == rec.select_soft_add_power and
                                                                   x.multi_focal == rec.select_soft_multifocal  # and
                                                                   #    con.contact_lens_manufacturer_id == rec.soft_manufacturer_id.contact_lens_manufacturer_id and
                                                                   ):
                            colors.append(ps.color_type_id.id)
                            prod_list_od.append(ps.id)
                    elif rec.prescription_id.rx == 'hard':
                        for ps in con.product_variant_ids.filtered(lambda x:
                                                                   x.bc == rec.base_curve and
                                                                   x.sphere == rec.sphere and
                                                                   x.cylinder == rec.cylinder and
                                                                   x.axis == rec.axis and
                                                                   x.add == rec.add
                                                                   ):
                            colors.append(ps.color_type_id.id)
                            prod_list_od.append(ps.id)
                    elif rec.prescription_id.rx == 'glasses':
                        for ps in con.product_variant_ids.filtered(lambda x:
                                                                   x.sphere == rec.gls_sphere and
                                                                   x.cylinder == rec.gls_cylinder and
                                                                   x.axis == rec.gls_axis and
                                                                   x.add == rec.gls_add
                                                                   ):
                            colors.append(ps.color_type_id.id)
                            prod_list_od.append(ps.id)
        domain = {
            'contact_lens_products_od': [('id', 'in', prod_list_od)],
            'od_color': [('id', 'in', colors)]
        }
        if len(colors) == 1:
            try:
                self.od_color = colors[0].id
            except:
                pass
        return {'domain': domain}

    @api.onchange('prescription_id')
    def get_os_lenses(self):
        colors = list()
        prod_list_os = list()
        for rec in self:
            if rec.order_type_name == "Contact Lens" and rec.prescription_id:
                if rec.prescription_id.rx == 'soft':
                    contact_lens_search = self.env['product.template'].search(
                        [('categ_id.name', '=', 'Contact Lens'),
                         ('contact_lens_manufacturer_id', '=', rec.soft_left_manufacturer_id.contact_lens_manufacturer_id.id)])
                         # ('name', '=', rec.soft_left_manufacturer_id.name)])
                if rec.prescription_id.rx == 'hard':
                    contact_lens_search = self.env['product.template'].search(
                        [('categ_id.name', '=', 'Contact Lens'),
                         ('contact_lens_manufacturer_id', '=', rec.left_manufacturer_id.contact_lens_manufacturer_id.id)])
                         # ('name', '=',rec.left_manufacturer_id.name)])
                for con in contact_lens_search:
                    if rec.prescription_id.rx == 'soft':
                        for ps in con.product_variant_ids.filtered(lambda x:
                                                                   x.bc == rec.soft_left_base_curve and
                                                                   x.diam == rec.soft_left_diameter and
                                                                   x.sphere == rec.soft_left_sphere and
                                                                   x.cylinder == rec.soft_left_cylinder and
                                                                   x.axis == rec.soft_left_axis and
                                                                   x.add == rec.soft_left_add_power and
                                                                   x.multi_focal == rec.soft_left_multifocal  # and
                                                                   #    x.product_tmpl_id.contact_lens_manufacturer_id == rec.soft_left_manufacturer_id.contact_lens_manufacturer_id
                                                                   ):
                            colors.append(ps.color_type_id.id)
                            prod_list_os.append(ps.id)
                    elif rec.prescription_id.rx == 'hard':
                        for ps in con.product_variant_ids.filtered(lambda x:
                                                                   x.bc == rec.left_base_curve and
                                                                   x.sphere == rec.left_sphere and
                                                                   x.cylinder == rec.left_cylinder and
                                                                   x.axis == rec.left_axis and
                                                                   x.add == rec.left_add
                                                                   ):
                            colors.append(ps.color_type_id.id)
                            prod_list_os.append(ps.id)
                    elif rec.prescription_id.rx == 'glasses':
                        for ps in con.product_variant_ids.filtered(lambda x:
                                                                   x.sphere == rec.gls_left_lens_sphere and
                                                                   x.cylinder == rec.gls_left_lens_cylinder and
                                                                   x.axis == rec.gls_left_lens_axis and
                                                                   x.add == rec.gls_add
                                                                   ):
                            colors.append(ps.color_type_id.id)
                            prod_list_os.append(ps.id)
        domain = {
            'contact_lens_products_os': [('id', 'in', prod_list_os)],
            'os_color': [('id', 'in', colors)]
        }
        if len(colors) == 1:
            try:
                self.os_color = colors[0].id
            except:
                pass

        return {'domain': domain}

    name = fields.Char(default=lambda self: self._context.get('so_id'))
    sale_id = fields.Many2one('sale.order', default=lambda self: self.env['sale.order'].browse(self._context.get('so_id')))
    order_type_name = fields.Char(default=lambda self: self._context.get('order_ref'))
    partner_id = fields.Many2one('res.partner', default=lambda self: self._context.get('partner_id'))
    partner_cell = fields.Char(related='partner_id.phone', string="Cell #")
    partner_name = fields.Char(compute='partner_id_name')
    insurance_id = fields.Many2one('spec.insurance', related='sale_id.insurance_id')
    authorization_id = fields.Many2one('spec.insurance.authorizations', related='sale_id.authorization_id')

    # frames_products = fields.Many2one('product.template', string="Frames",
    #                                   domain="[('spec_product_type','=','frame')]")
    frames_products_variants = fields.Many2one('product.product', string="Frames",
                                               domain="[('product_tmpl_id.categ_id.name','=','Frames')]")
    lens_products = fields.Many2one('product.product', string="Lens", domain="[('product_tmpl_id.categ_id.name','=','Lens')]")
    vcodes_lens = fields.One2many('spec.lens.treatment.line', related='lens_products.treatment_line_ids',
                                  string="HCPCS")
    contact_lens_products_od = fields.Many2one('product.product', string="OD")
    package_od = fields.Many2one('product.packaging', related='contact_lens_products_od.product_packaging_id')
    uom_id_od = fields.Many2one('uom.uom', related='contact_lens_products_od.uom_id')
    list_price_od = fields.Float(related='contact_lens_products_od.list_price', string='Price')
    contact_lens_products_os = fields.Many2one('product.product', string="OS")
    package_os = fields.Many2one('product.packaging', string="Package",
                                 related='contact_lens_products_os.product_packaging_id')
    uom_id_os = fields.Many2one('uom.uom', related='contact_lens_products_os.uom_id')
    list_price_os = fields.Float(string="Price", related='contact_lens_products_os.list_price')
    lenstreatment_products = fields.Many2many('product.product', 'lenstreatment_products_rel', string="Lens Treatment",
                                              domain="[('product_tmpl_id.categ_id.name','=','Lens Treatment')]")
    vcodes_lenstreatment = fields.One2many('spec.lens.treatment.line',
                                           related='lenstreatment_products.treatment_line_ids', string="HCPCS")
    miscellaneous_products = fields.One2many('miscellaneous.products', 'multi_order_type_id', string="Miscellaneous")
    service_products = fields.One2many('service.products', 'multi_order_type_id', string="Service")

    @api.onchange('lenstreatment_products')
    def get_compatible_lens_treatment(self):
        all_selected_prds = list(self.lenstreatment_products.ids)
        lenstreatment_products = []
        if self.lens_products.treatment_child_ids and self.lens_products.treatment_child_ids:
            for LT in self.lens_products.treatment_child_ids:
                lenstreatment_products += [x.id for x in self.env['product.product']
                                                            .search([('category_id', '=', LT.category_id.id),
                                                                     ('vw_code', '=', LT.lens_treatment_id.code)])]
        for rec in self.lenstreatment_products:
            if rec.ids[0] not in lenstreatment_products:
                raise exceptions.ValidationError(
                    _('The Lens Treatment selected are not present in any lens.\n Please make another selection.'))
            for line in rec.incompatible_treatments_ids.product_variant_id.filtered(lambda x: x.ids[0] in all_selected_prds):
                raise exceptions.ValidationError(
                    _('The Lens Treatment selected are not compatible.\n Please make another selection.'))

    @api.onchange('lens_products')
    def get_lens_treatment(self):
        for rec in self:
            if rec.lens_products.treatment_child_ids and rec.lens_products.treatment_child_ids.filtered(lambda x: x.lnclude):
                for LT in rec.lens_products.treatment_child_ids.filtered(lambda x: x.lnclude):
                    lenstreatment_products = [(4, x.id) for x in self.env['product.product'].search([('category_id', '=', LT.category_id.id),
                                                                                                     ('vw_code', '=', LT.lens_treatment_id.code)])]
                    lenstreatment_products.insert(0, (5, 0, 0))
                    rec.lenstreatment_products = lenstreatment_products
            for ven in rec.lens_products.semi_finish_lens_ids and rec.lens_products.semi_finish_lens_ids.mapped(
                    'vendor_id').filtered(lambda x: x.is_lab == True):
                rec.details = ven.id

    # patients own frame
    model_number = fields.Char(string='Model Number')
    color_patient_frame = fields.Char(string='Color #')
    a = fields.Float(string='A')
    b = fields.Float(string='B')
    dbl = fields.Float(string='DBL')
    ed = fields.Float(string='ED')
    bridge = fields.Char(string='Bridge')
    temple = fields.Char(string='Temple')
    edge_id = fields.Selection(
        [('beveled', 'Beveled'), ('drill_mount', 'Drill-mount'), ('grooved', 'Grooved'), ('industrial', 'Industrial'),
         ('other', 'Other')], string="Edge Type")
    frame_id = fields.Many2one('spec.frame.type', string="Frame Type")
    # brand_id = fields.Many2one(
    #     'spec.brand.brand', string='Brand', domain="[('brand_type', '=', 'frame')]")

    # Measurements
    dist_pd_lab_details = fields.Char(string="Dist PD", )
    near_pd_lab_details = fields.Char(string="Near PD")
    oc_hit_lab_details = fields.Char(string="O.C Ht")
    seg_ht_lab_details = fields.Char(string="Seg Ht")
    bc_lab_details = fields.Char(string="BC")
    dist_pd_lab_details_os = fields.Char(string="Dist PD")
    near_pd_lab_details_os = fields.Char(string="Near PD")
    oc_hit_lab_details_os = fields.Char(string="O.C Ht")
    seg_ht_lab_details_os = fields.Char(string="Seg Ht")
    bc_lab_details_os = fields.Char(string="BC")
    panto_lab_details = fields.Char(string="Panto")
    thickness_lab_details = fields.Char(string="Thickness")
    wrap_lab_details = fields.Char(string="Wrap")
    vertex_mlab_details = fields.Char(string="Vertex", )

    # Lens
    eye_lab_details = fields.Selection([('Both', 'Both'), ('Right Only', 'Right Only'), ('Left Only', 'Left Only')],
                                       string='Eye', default='Both')
    # uom_lab_details = fields.Selection([('Pair','Pair'),('Units','Unit')], string='Product uom', default='Pair')

    # Lens Treatement
    tint_color_lab_details = fields.Selection([('Brown', 'Brown'), ('Yellow', 'Yellow')], string="Tint Color")
    tint_sample_lab_details = fields.Selection(
        [('Lighten', 'Lighten'), ('Darken', 'Darken'), ('Match', 'Match'), ('No Sample', 'No Sample')],
        string="Tint Sample")
    mirror_coating_lab_details = fields.Char(string="Mirror Coating")
    by_lab_details = fields.Float(string="by")

    # Frame
    frame_rel = fields.Many2one('product.template', related='frames_products_variants.product_tmpl_id')
    edge_type = fields.Selection(
        [('beveled', 'Beveled'), ('drill_mount', 'Drill-mount'), ('grooved', 'Grooved'), ('industrial', 'Industrial'),
         ('other', 'Other')], string="Edge Type")
    frame_type = fields.Many2one('spec.frame.type', string="Frame Type")

    a_lab_details = fields.Float(string="A")
    b_lab_details = fields.Float(string="B")
    dbl_lab_details = fields.Float(string="DBL")
    ed_lab_details = fields.Float(string="ED")

   # frame information

    @api.onchange('dist_pd_lab_details')
    def onchange_dist_pd_lab_details(self):
        if self.dist_pd_lab_details and  self.dist_pd_lab_details.isdigit():
            self.dist_pd_lab_details = str(float(self.dist_pd_lab_details))
            self.dist_pd_lab_details_os = str(float(self.dist_pd_lab_details))

    @api.onchange('dist_pd_lab_details_os')
    def onchange_dist_pd_lab_details_os(self):
        if self.dist_pd_lab_details_os and  self.dist_pd_lab_details_os.isdigit():
            self.dist_pd_lab_details_os = str(float(self.dist_pd_lab_details_os))

    @api.onchange('near_pd_lab_details')
    def onchange_near_pd_lab_details(self):
        if self.near_pd_lab_details and  self.near_pd_lab_details.isdigit():
            self.near_pd_lab_details = str(float(self.near_pd_lab_details))
            self.near_pd_lab_details_os = str(float(self.near_pd_lab_details))

    @api.onchange('near_pd_lab_details_os')
    def onchange_near_pd_lab_details_os(self):
        if self.near_pd_lab_details_os and  self.near_pd_lab_details_os.isdigit():
            self.near_pd_lab_details_os = str(float(self.near_pd_lab_details_os))

    @api.onchange('oc_hit_lab_details')
    def onchange_oc_hit_lab_details(self):
        if self.oc_hit_lab_details and  self.oc_hit_lab_details.isdigit():
            self.oc_hit_lab_details = str(float(self.oc_hit_lab_details))
            self.oc_hit_lab_details_os = str(float(self.oc_hit_lab_details))

    @api.onchange('oc_hit_lab_details_os')
    def onchange_oc_hit_lab_details_os(self):
        if self.oc_hit_lab_details_os and  self.oc_hit_lab_details_os.isdigit():
            self.oc_hit_lab_details_os = str(float(self.oc_hit_lab_details_os))

    @api.onchange('seg_ht_lab_details')
    def onchange_seg_ht_lab_details(self):
        if self.seg_ht_lab_details and  self.seg_ht_lab_details.isdigit():
            self.seg_ht_lab_details = str(float(self.seg_ht_lab_details))
            self.seg_ht_lab_details_os = str(float(self.seg_ht_lab_details))

    @api.onchange('seg_ht_lab_details_os')
    def onchange_seg_ht_lab_details_os(self):
        if self.seg_ht_lab_details_os and  self.seg_ht_lab_details_os.isdigit():
            self.seg_ht_lab_details_os = str(float(self.seg_ht_lab_details_os))

    @api.onchange('bc_lab_details')
    def onchange_bc_lab_details(self):
        if self.bc_lab_details and  self.bc_lab_details.isdigit():
            self.bc_lab_details = str(float(self.bc_lab_details))
            self.bc_lab_details_os = str(float(self.bc_lab_details))

    @api.onchange('bc_lab_details_os')
    def onchange_bc_lab_details_os(self):
        if self.bc_lab_details_os and  self.bc_lab_details_os.isdigit():
            self.bc_lab_details_os = str(float(self.bc_lab_details_os))

    @api.onchange('panto_lab_details')
    def onchange_panto_lab_details(self):
        if self.panto_lab_details and  self.panto_lab_details.isdigit():
            self.panto_lab_details = str(float(self.panto_lab_details))

    @api.onchange('thickness_lab_details')
    def onchange_thickness_lab_details(self):
        if self.thickness_lab_details and  self.thickness_lab_details.isdigit():
            self.thickness_lab_details = str(float(self.thickness_lab_details))

    @api.onchange('wrap_lab_details')
    def onchange_wrap_lab_details(self):
        if self.wrap_lab_details and  self.wrap_lab_details.isdigit():
            self.wrap_lab_details = str(float(self.wrap_lab_details))

    @api.onchange('vertex_mlab_details')
    def onchange_vertex_mlab_details(self):
        if self.vertex_mlab_details and  self.vertex_mlab_details.isdigit():
            self.vertex_mlab_details = str(float(self.vertex_mlab_details))

    @api.onchange('frames_products_variants')
    def get_lab_frame_details(self):
        if self.frames_products_variants:
            self.edge_type = self.frames_products_variants.product_tmpl_id.edge_type
            self.frame_type = self.frames_products_variants.product_tmpl_id.frame_type_id
            self.a_lab_details = self.frames_products_variants.a
            self.b_lab_details = self.frames_products_variants.b
            self.dbl_lab_details = self.frames_products_variants.dbl
            self.ed_lab_details = self.frames_products_variants.ed

    # lab information
    @api.onchange('order_type_name')
    def get_lab_details(self):
        if self._context.get('order_ref') == 'Contact Lens':
            vendors_list = []
            contact_lens_search = self.env['product.template'].search([('categ_id.name', '=', 'Contact Lens')])
            for prd in contact_lens_search:
                for ven in prd.seller_ids:
                    vendors_list.append(ven.name.id)
            return {'domain': {'lab_details': [('id', 'in', vendors_list)]}}
        else:
            return {'domain': {'lab_details': [('is_lab', '=', True)]}}

    lab_details = fields.Many2one('res.partner', string="Lab", domain="[('is_lab', '=', True)]")
    lab_instructions = fields.Text()
    physician_id = fields.Many2one('hr.employee', string="Provider", domain="['|', ('doctor','=',True), ('is_outside_doctor','=',True)]")
    finishing_status = fields.Selection([('Uncut', 'Uncut'),
                                         ('Frame to Come', 'Frame to Come'),
                                         ('Supply Frame', 'Supply Frame'),
                                         ('Lab Supplied', 'Lab Supplied'),
                                         ('Lens Only', 'Lens Only'),
                                         ], string="Frame Lab Status")
    tray_no = fields.Char(string="Tray #")
    order_status = fields.Many2one('order.status')
    dispensing_notes = fields.Many2one('dispensing.notes')
    promised_date = fields.Date(string='Promised')
    ship_to = fields.Many2one('res.partner', domain="[('parent_id', '=', partner_id),('type','=', 'delivery')]")

    # Prescription
    prescription_id = fields.Many2one('spec.contact.lenses', string="Prescription",
                                      domain=lambda
                                          self: f"[('partner_id','=',{self.get_default_lines()}), {self.get_rx_domain()}]")
    rx = fields.Selection([('glasses', 'Glasses'), ('soft', 'Soft Contact Lens'), ('hard', 'Hard Contact Lens')],
                          related="prescription_id.rx", string="Rx", default='glasses')
    rx_usage_id = fields.Many2one('spec.rx.usage', related='prescription_id.rx_usage_id', string="Rx Usage")
    is_expired = fields.Boolean(compute='compute_expired_prescription')
    expired_prescription_date = fields.Date(string="Expired", related='prescription_id.expiration_date')
    # recommendations
    gls_lens_style_id = fields.Many2one('spec.lens.style', string="Lens Style",
                                        related='prescription_id.gls_lens_style_id')
    gls_lens_material_id = fields.Many2one('spec.lens.material', string="Lens Material",
                                           related='prescription_id.gls_lens_material_id')
    gls_ar_coating = fields.Boolean(string="AR Coating", related='prescription_id.gls_ar_coating')
    gls_photochromic = fields.Boolean(string="Photochromic", related='prescription_id.gls_photochromic')
    gls_polarized = fields.Boolean(string="Polarized", related='prescription_id.gls_polarized')
    gls_tint = fields.Boolean(string="Tint", related='prescription_id.gls_tint')
    rx_notes = fields.Text(string="Rx Notes", related='prescription_id.rx_notes')

    """Rx Type Glasses"""
    gls_sphere = fields.Selection(sphere_list, string='Sphere')
    gls_cylinder = fields.Selection(cylinder_list, string='Cylinder')
    gls_axis = fields.Selection(axis_list, string='Axis')
    gls_add = fields.Selection(add_list, string='Add')
    gls_h_prism = fields.Char(related='prescription_id.gls_h_prism', string="H.Prism")
    gls_v_prism = fields.Char(related='prescription_id.gls_v_prism', string="V.Prism")
    gls_h_base = fields.Selection(related='prescription_id.gls_h_base', string="H.Base")
    gls_v_base = fields.Selection(related='prescription_id.gls_v_base', string="V.Base")
    gls_left_lens_sphere = fields.Selection(sphere_list, string='Sphere')
    gls_left_lens_cylinder = fields.Selection(cylinder_list, string='Cylinder')
    gls_left_lens_axis = fields.Selection(axis_list, string='Axis')
    gls_left_lens_add = fields.Selection(add_list, string='Add')
    gls_left_lens_h_prism = fields.Char(related='prescription_id.gls_left_lens_h_prism', string="H.Prism")
    gls_left_lens_v_prism = fields.Char(related='prescription_id.gls_left_lens_v_prism', string="V.Prism")
    gls_left_h_base = fields.Selection(related='prescription_id.gls_left_h_base', string="H.Base")
    gls_left_v_base = fields.Selection(related='prescription_id.gls_left_v_base', string="V.Base")
    gls_computer_lens = fields.Boolean(related='prescription_id.gls_computer_lens', string="Computer Lens")
    gls_anti_reflective = fields.Boolean(related='prescription_id.gls_anti_reflective', string="Anti-Reflective")
    gls_balance = fields.Boolean(string="Balance", related='prescription_id.gls_balance')
    gls_left_balance = fields.Boolean(string="Balance", related='prescription_id.gls_left_balance')
    """Rx Type Soft Contact Lens"""
    soft_manufacturer_id = fields.Many2one('product.template', related="prescription_id.soft_manufacturer_id",
                                           domain="[('categ_id.name','=','Contact Lens')]",
                                           string="Manufacturer & Name")
    soft_style = fields.Char(related="prescription_id.soft_style", string="Style")
    soft_color = fields.Char(related="prescription_id.soft_color", string="Color")
    select_soft_color = fields.Char(related="prescription_id.select_soft_color", string="Color")
    soft_base_curve = fields.Char(related="prescription_id.soft_base_curve", string="Base Curve")
    select_soft_base_curve = fields.Char(related="prescription_id.select_soft_base_curve", string="Base Curve")
    # soft_base_curve = fields.Selection(selection="get_soft_sphere_list", string="Base Curve")
    soft_diameter = fields.Char(related="prescription_id.soft_diameter", string="Diameter")
    select_soft_diameter = fields.Char(related="prescription_id.select_soft_diameter", string="Diameter")
    soft_sphere = fields.Char(related="prescription_id.soft_sphere", string="Sphere")
    select_soft_sphere = fields.Selection(sphere_list, related="prescription_id.select_soft_sphere", string="Sphere")
    soft_cylinder = fields.Char(related="prescription_id.soft_cylinder", string="Cylinder")
    select_soft_cylinder = fields.Selection(cylinder_list, related="prescription_id.select_soft_cylinder", string="Cylinder")
    soft_axis = fields.Char(related="prescription_id.soft_axis", string="Axis")
    select_soft_axis = fields.Selection(axis_list, related="prescription_id.select_soft_axis", string="Axis")
    soft_add_power = fields.Char(related="prescription_id.soft_add_power", string="Add Power")
    select_soft_add_power = fields.Selection(add_list, related="prescription_id.select_soft_add_power", string="Add Power")
    soft_va = fields.Char(related="prescription_id.soft_va", string="VA")
    select_soft_va = fields.Char(related="prescription_id.select_soft_va", string="VA")
    soft_multifocal = fields.Char(related="prescription_id.soft_multifocal", string="Multifocal")
    select_soft_multifocal = fields.Char(related="prescription_id.select_soft_multifocal", string="Multifocal")
    soft_left_manufacturer_id = fields.Many2one('product.template', related="prescription_id.soft_left_manufacturer_id",
                                                domain="[('categ_id.name','=','Contact Lens')]",
                                                string="Manufacturer & Brand")
    soft_left_style = fields.Char(related="prescription_id.soft_left_style", string="Style")
    soft_left_color = fields.Char(related="prescription_id.soft_left_color", string="Color")
    soft_left_base_curve = fields.Char(related="prescription_id.soft_left_base_curve", string="Base Curve")
    soft_left_diameter = fields.Char(related="prescription_id.soft_left_diameter", string="Diameter")
    soft_left_sphere = fields.Selection(sphere_list, related="prescription_id.soft_left_sphere", string="Sphere")
    soft_left_cylinder = fields.Selection(cylinder_list, related="prescription_id.soft_left_cylinder", string="Cylinder")
    soft_left_axis = fields.Selection(axis_list, related="prescription_id.soft_left_axis", string="Axis")
    soft_left_add_power = fields.Selection(add_list, related="prescription_id.soft_left_add_power", string="Add Power")
    soft_left_va = fields.Char(related="prescription_id.soft_left_va", string="VA")
    soft_left_multifocal = fields.Char(related="prescription_id.soft_left_multifocal", string="Multifocal")
    wearing_schedulen = fields.Many2one('spec.contact.lens.wear.period', related="prescription_id.wearing_schedulen",
                                        string="Wearing Period")
    replcement = fields.Many2one('spec.contact.lens.replacement.schedule', related="prescription_id.replcement",
                                 string="Replacement")

    """Hard Contact Lens Fields"""
    """OD"""
    manufacturer_id = fields.Many2one('product.template', related="prescription_id.manufacturer_id",
                                      domain="[('categ_id.name','=','Contact Lens'), ('lens_type', '=', 'rgp')]",
                                      string="Manufacturer")
    style = fields.Char(related="prescription_id.style", string="Name")
    material = fields.Char(related="prescription_id.material", string="Material")
    base_curve = fields.Char(related="prescription_id.base_curve", string="BC")
    diameter = fields.Char(related="prescription_id.diameter", string="Diameter")
    sphere = fields.Selection(sphere_list, related="prescription_id.sphere", string="Sphere")
    cylinder = fields.Selection(cylinder_list, related="prescription_id.cylinder", string="Cylinder")
    axis = fields.Selection(axis_list, related="prescription_id.axis", string="Axis")
    add = fields.Selection(add_list, related="prescription_id.add", string="Add")
    seg_height = fields.Char(related="prescription_id.seg_height", string="Seg  Ht")
    pc_radius = fields.Char(related="prescription_id.pc_radius", string="PC Radius")
    pc_width = fields.Char(related="prescription_id.pc_width", string="PC width")
    ct = fields.Char(related="prescription_id.ct", string="CT")
    oz = fields.Char(related="prescription_id.oz", string="OZ")
    base_curve_2 = fields.Char(related="prescription_id.base_curve_2", string="BC 2")
    color = fields.Selection([('clear', 'Clear'), ('dlue', 'Blue')], related="prescription_id.color", string="Color")
    sphere_2 = fields.Char(related="prescription_id.sphere_2", string="Sph 2")
    axis_2 = fields.Char(related="prescription_id.axis_2", string="Axis 2")
    cylinder_2 = fields.Char(related="prescription_id.cylinder_2", string="Cyl 2")
    add_diam_2 = fields.Char(related="prescription_id.add_diam_2", string="Add Diam")
    dot = fields.Boolean(related="prescription_id.dot", string="Dot")
    """OS"""
    left_manufacturer_id = fields.Many2one('product.template', related="prescription_id.left_manufacturer_id",
                                           domain="[('categ_id.name','=','Contact Lens'), ('lens_type', '=', 'rgp')]",
                                           string="Manufacturer")
    left_style = fields.Char(related="prescription_id.left_style", string="Name")
    left_material = fields.Char(related="prescription_id.left_material", string="Material")
    left_base_curve = fields.Char(related="prescription_id.left_base_curve", string="BC")
    left_diameter = fields.Char(related="prescription_id.left_diameter", string="Diameter")
    left_sphere = fields.Selection(sphere_list, related="prescription_id.left_sphere", string="Sphere")
    left_cylinder = fields.Selection(cylinder_list, related="prescription_id.left_cylinder", string="Cylinder")
    left_axis = fields.Selection(axis_list, related="prescription_id.left_axis", string="Axis")
    left_add = fields.Selection(add_list, related="prescription_id.left_add", string="Add")
    left_seg_height = fields.Char(related="prescription_id.left_seg_height", string="Seg Ht")
    left_pc_radius = fields.Char(related="prescription_id.left_pc_radius", string="PC Radius")
    left_ct = fields.Char(related="prescription_id.left_ct", string="CT")
    left_oz = fields.Char(related="prescription_id.left_oz", string="OZ")
    left_pc_width = fields.Char(related="prescription_id.left_pc_width", string="PC width")
    left_base_curve_2 = fields.Char(related="prescription_id.left_base_curve_2", string="BC 2")
    left_color = fields.Selection([('clear', 'Clear'), ('dlue', 'Blue')], related="prescription_id.left_color",
                                  string="Color")
    left_sphere_2 = fields.Char(related="prescription_id.left_sphere_2", string="Sph 2")
    left_cylinder_2 = fields.Char(related="prescription_id.left_cylinder_2", string="Cyl 2")
    left_axis_2 = fields.Char(related="prescription_id.left_axis_2", string="Axis 2")
    left_add_diam_2 = fields.Char(related="prescription_id.left_add_diam_2", string="Add Diam")
    left_dot = fields.Boolean(related="prescription_id.left_dot", string="Dot", default=True)

    od_color = fields.Many2one('spec.contact.lens.color.type')
    os_color = fields.Many2one('spec.contact.lens.color.type')
    od_qty = fields.Integer(default=1)
    os_qty = fields.Integer(default=1)
    od_contact_lens_visibility = fields.Boolean(compute='check_visibility', default=True)
    os_contact_lens_visibility = fields.Boolean(compute='check_visibility', default=True)
    copy_contact_lens = fields.Boolean(string="OS = OD")
    hcpcs_id = fields.One2many('sale.order.line.hcpcs', 'sale_order_line_wizard_id')
    reading_rx = fields.Boolean(string='Reading RX', default=False)
    distance_rx = fields.Boolean(string='Distance RX', default=False)
    lens_type_add = fields.Boolean(default=False)
    patient_name = fields.Many2one('res.partner', domain=[('patient', '=', True)], string='Patient')
    patient_phone = fields.Char(related='patient_name.phone', string='Phone')
    current_datetime = fields.Datetime(default=lambda self: fields.datetime.now())
    sale_order_id = fields.Many2one('sale.order', string='Sale Order ID')
    sale_order_status = fields.Selection([
                                        ('draft', 'Quotation'),
                                        ('sent', 'Quotation Sent'),
                                        ('sale', 'Sales Order'),
                                        ('done', 'Locked'),
                                        ('cancel', 'Cancelled'),
                                        ], related='sale_order_id.state')
    sale_order_date_order = fields.Datetime(related='sale_order_id.date_order')

    def show_multi_order_type_historical_tree(self):
        return {
            'name': 'Order Status',
            'view_mode': 'tree',
            'view_id': self.env.ref('ivis_order_grouping.multi_order_type_historical_tree').id,
            'res_model': 'multi.order.type.historical',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': ([('multi_order_type_id', '=', self.id)])
        }

    @api.onchange('order_status')
    def _onchange_order_status(self):
        for res in self:
            if res.create_date:
                res.env['multi.order.type.historical'].create({
                    'status': res.order_status.name,
                    'multi_order_type_id': res.ids[0]
                })

    @api.onchange('copy_contact_lens')
    def equate_lensses_onchange(self):
        if self.copy_contact_lens:
            if self.contact_lens_products_od:
                self.contact_lens_products_os = self.contact_lens_products_od.id
                self.os_color = self.od_color.id
                self.os_qty = self.od_qty
        elif not self.copy_contact_lens and not self.env.context.get('contact_lens_products_os', False):
            self.contact_lens_products_os = False
            self.os_color = False
            self.os_qty = 1

    def equate_lensses(self):
        if self.contact_lens_products_od and self.od_color and self.od_qty:
            self.contact_lens_products_os = self.contact_lens_products_od.id
            self.os_color = self.od_color.id
            self.os_qty = self.od_qty

        if self.contact_lens_products_os and self.os_color and self.os_qty:
            self.contact_lens_products_od = self.contact_lens_products_os.id
            self.od_color = self.os_color.id
            self.od_qty = self.os_qty

        # return{
        #     "type": "ir.actions.do_nothing",
        # }
        # self.my_field_ids = [(6, 0, my_values_ids)]
        return {
            'name': 'Same title',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'multi.order.type',
            'domain': [],
            'context': dict(self._context, active_ids=self.ids),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.depends('prescription_id')
    def compute_expired_prescription(self):
        for rec in self:
            rec.is_expired = True if rec.prescription_id and rec.prescription_id.expiration_date and rec.prescription_id.expiration_date < date.today() else False

    @api.model
    def create(self, vals):
        res = super(MultiOrderTypes, self).create(vals)
        if res.order_type_name == "Lenses Only" and not res.lens_products and (
                res.model_number == '' or not res.model_number):
            raise exceptions.Warning("Frame information or lenses must be selected for a Lenses Only Sale")
        return res

    def create_lines(self):
        pass

    @api.onchange('frames_products_variants', 'lens_products', 'contact_lens_products_od', 'contact_lens_products_os',
                  'miscellaneous_products', 'lenstreatment_products', 'service_products', 'od_qty', 'os_qty','reading_rx')
    def hcpcs_frame_onchange(self):
        for rec in self:
            hcpcs_id = [(5, 0, 0)]
            if rec.frames_products_variants.id:
                res = (0, 0, {
                    'name': rec.frames_products_variants.name,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                # hcpcs_codes = rec.env['spec.procedure.code'].search(['|',('name','=','V2020'),('name','=','V2025')])
                hcpcs_codes = rec.env['spec.procedure.code'].search(
                    ['|', '|', '|', ('name', '=', 'V2020'), ('name', '=', 'V2025'), ('name', '=', 'v2020'),
                     ('name', '=', 'v2025')])
                for code in hcpcs_codes:
                    if code.name == 'V2020' or code.name == 'v2020':
                        res = (0, 0, {
                            'name': '',
                            'product_id': rec.frames_products_variants.id,
                            'hcpcs_code': [(4,code.id)],
                            'retail_price': rec.frames_products_variants.list_price,
                            'sale_order_line_wizard_id': rec.id,
                            'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                            'insurance_id': rec.sale_id.insurance_id.id,

                        }
                               )
                        hcpcs_id.append(res)
                    elif code.name == 'V2025' or code.name == 'v2025':
                        res = (0, 0, {
                            'name': '',
                            'product_id': rec.frames_products_variants.id,
                            'hcpcs_code': [(4,code.id)],
                            'retail_price': 0,
                            'sale_order_line_wizard_id': rec.id,
                            'categ_id': self.env['product.category'].search([('name', '=', 'Frames')], limit=1),
                            'insurance_id': rec.sale_id.insurance_id.id,
                        }
                               )
                        hcpcs_id.append(res)
            if rec.lens_products.id:
                res = (0, 0, {
                    'name': rec.lens_products.name,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                if rec.lens_products.treatment_line_ids:
                    procedure_code = ''
                    procedure_price = float()
                    for treatment_line in rec.lens_products.treatment_line_ids:
                        if treatment_line.pro_code_id and rec.prescription_id:
                            if rec.gls_sphere and not rec.gls_cylinder and (treatment_line.pro_code_id.name == 'V2100' or treatment_line.pro_code_id.name == 'v2100' or treatment_line.pro_code_id.name == 'V2200' or treatment_line.pro_code_id.name == 'V2300' or treatment_line.pro_code_id.name == 'v2200' or treatment_line.pro_code_id.name == 'v2300'):
                                if (
                                        treatment_line.pro_code_id.min_sphere >= 1 and treatment_line.pro_code_id.max_sphere == 0):
                                    if ((abs(float(rec.gls_sphere)) > treatment_line.pro_code_id.min_sphere)) or ((abs(float(rec.gls_left_lens_sphere)) > treatment_line.pro_code_id.min_sphere)) :
                                        rang = len(hcpcs_id) - 1
                                        while True:
                                            dxt = hcpcs_id[rang:][0]
                                            if 'hcpcs_code' in dxt[2]:
                                                if (4, treatment_line.pro_code_id.id) not in dxt[2]['hcpcs_code']:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                                                else:
                                                    break
                                            else:
                                                rang += 1
                                                res = (0, 0, {
                                                    'name': '',
                                                    'product_id': rec.lens_products.id,
                                                    'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                    'hcpcs_modifier': treatment_line.modifier_id.id,
                                                    'retail_price': treatment_line.price,
                                                    'sale_order_line_wizard_id': rec.id,
                                                    'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                    'insurance_id': rec.sale_id.insurance_id.id,
                                                }
                                                       )
                                                hcpcs_id.append(res)
                                    else:
                                        hcpcs_series = treatment_line.pro_code_id.name[0:3]
                                        procedures = rec.env['spec.procedure.code'].search(
                                            [('name', 'like', hcpcs_series), ('sphere_or_cyclinder', '=', 'sphere')])
                                        pros = []
                                        for pro in procedures:
                                            if (pro.min_sphere >= 1 and pro.max_sphere == 0) or (
                                                    pro.min_sphere_2 <= -1 and pro.max_sphere_2 == 0):
                                                if (abs((float(rec.gls_sphere)) > pro.min_sphere)) or (abs((float(rec.gls_left_lens_sphere)) > pro.min_sphere)):
                                                    pros.append(pro)
                                        for pr in pros:
                                            rang = len(hcpcs_id) - 1
                                            while True:
                                                dxt = hcpcs_id[rang:][0]
                                                if 'hcpcs_code' in dxt[2]:
                                                    if 'hcpcs_code' in dxt[2]:
                                                        if (4, pr.id) not in dxt[2]['hcpcs_code']:
                                                            dxt[2]['hcpcs_code'].append((4, pr.id))
                                                        else:
                                                            break
                                                else:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,pr.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                                else:
                                    if (abs((float(rec.gls_sphere)) >= treatment_line.pro_code_id.min_sphere and abs(float(
                                            rec.gls_sphere)) <= treatment_line.pro_code_id.max_sphere)) or (abs((float(rec.gls_left_lens_sphere)) >= treatment_line.pro_code_id.min_sphere and abs(float(
                                            rec.gls_left_lens_sphere)) <= treatment_line.pro_code_id.max_sphere)):
                                        rang = len(hcpcs_id) - 1
                                        while True:
                                            dxt = hcpcs_id[rang:][0]
                                            if 'hcpcs_code' in dxt[2]:
                                                if (4, treatment_line.pro_code_id.id) not in dxt[2]['hcpcs_code']:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                                                else:
                                                    break
                                            else:
                                                rang += 1
                                                res = (0, 0, {
                                                    'name': '',
                                                    'product_id': rec.lens_products.id,
                                                    'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                    'hcpcs_modifier': treatment_line.modifier_id.id,
                                                    'retail_price': treatment_line.price,
                                                    'sale_order_line_wizard_id': rec.id,
                                                    'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                    'insurance_id': rec.sale_id.insurance_id.id,
                                                }
                                                       )
                                                hcpcs_id.append(res)
                                    else:
                                        hcpcs_series = treatment_line.pro_code_id.name[0:3]
                                        procedures = rec.env['spec.procedure.code'].search(
                                            [('name', 'like', hcpcs_series), ('sphere_or_cyclinder', '=', 'sphere')])
                                        pros = []
                                        for pro in procedures:
                                            if ((abs(float(
                                                    rec.gls_sphere)) >= pro.min_sphere and abs(float(
                                                rec.gls_sphere)) <= pro.max_sphere)) or ((abs(float(
                                                    rec.gls_left_lens_sphere)) >= pro.min_sphere and abs(float(
                                                rec.gls_left_lens_sphere)) <= pro.max_sphere)):
                                                pros.append(pro)
                                        for pr in pros:
                                            rang=len(hcpcs_id)-1
                                            while True:
                                                dxt= hcpcs_id[rang:][0]
                                                if 'hcpcs_code' in dxt[2]:
                                                    if (4, pr.id) not in dxt[2]['hcpcs_code']:
                                                        dxt[2]['hcpcs_code'].append((4, pr.id))
                                                    else:
                                                        break
                                                else:
                                                    rang+=1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,pr.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                            elif rec.gls_sphere and rec.gls_cylinder and (treatment_line.pro_code_id.name == 'V2100' or treatment_line.pro_code_id.name == 'v2100' or treatment_line.pro_code_id.name == 'V2200' or treatment_line.pro_code_id.name == 'V2300' or treatment_line.pro_code_id.name == 'v2200' or treatment_line.pro_code_id.name == 'v2300'):
                                if (treatment_line.pro_code_id.min_sphere >= 1 and treatment_line.pro_code_id.max_sphere == 0 and treatment_line.pro_code_id.min_cylinder >= 1 and treatment_line.pro_code_id.max_cylinder == 0):
                                    if ((abs(float(rec.gls_sphere)) > treatment_line.pro_code_id.min_sphere and abs(float(rec.gls_cylinder)) > treatment_line.pro_code_id.min_cylinder)) or ((abs(float(rec.gls_left_lens_sphere)) > treatment_line.pro_code_id.min_sphere and abs(float(rec.gls_left_lens_cylinder)) > treatment_line.pro_code_id.min_cylinder)):
                                        rang = len(hcpcs_id) - 1
                                        while True:
                                            dxt = hcpcs_id[rang:][0]
                                            if 'hcpcs_code' in dxt[2]:
                                                if (4, treatment_line.pro_code_id.id) not in dxt[2]['hcpcs_code']:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                                                else:
                                                    break
                                            else:
                                                rang += 1
                                                res = (0, 0, {
                                                    'name': '',
                                                    'product_id': rec.lens_products.id,
                                                    'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                    'hcpcs_modifier': treatment_line.modifier_id.id,
                                                    'retail_price': treatment_line.price,
                                                    'sale_order_line_wizard_id': rec.id,
                                                    'categ_id': self.env['product.category'].search(
                                                        [('name', '=', 'Lens')], limit=1),
                                                    'insurance_id': rec.sale_id.insurance_id.id,
                                                }
                                                       )
                                                hcpcs_id.append(res)
                                    else:
                                        hcpcs_series = treatment_line.pro_code_id.name[0:3]
                                        procedures = rec.env['spec.procedure.code'].search(
                                            [('name', 'like', hcpcs_series), ('sphere_or_cyclinder', '=', 'sphereocyclinder')])
                                        pros = []
                                        for pro in procedures:
                                            if (pro.min_sphere >= 1 and pro.max_sphere == 0 and pro.min_cylinder >= 1 and pro.max_cylinder == 0) or (
                                                    pro.min_sphere_2 <= -1 and pro.max_sphere_2 == 0 and pro.min_cylinder_2 <= -1 and pro.max_cylinder_2 == 0):
                                                if ((abs(float(rec.gls_sphere)) > pro.min_sphere and abs(float(rec.gls_cylinder)) > pro.min_cylinder) or (
                                                        abs(float(
                                                            rec.gls_sphere)) < pro.min_sphere_2 and abs(float(
                                                            rec.cylinder)) < pro.min_cylinder_2)) or ((abs(float(rec.gls_left_lens_sphere)) > pro.min_sphere and abs(float(rec.gls_left_lens_cylinder)) > pro.min_cylinder)):
                                                    pros.append(pro)
                                        for pr in pros:
                                            rang = len(hcpcs_id) - 1
                                            while True:
                                                dxt = hcpcs_id[rang:][0]
                                                if 'hcpcs_code' in dxt[2]:
                                                    if (4, pr.id) not in dxt[2]['hcpcs_code']:
                                                        dxt[2]['hcpcs_code'].append((4, pr.id))
                                                    else:
                                                        break
                                                else:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,pr.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                                else:
                                    if ((abs(float(rec.gls_sphere)) >= treatment_line.pro_code_id.min_sphere and abs(float(
                                            rec.gls_sphere)) <= treatment_line.pro_code_id.max_sphere and abs(float(rec.gls_cylinder)) >= treatment_line.pro_code_id.min_cylinder and abs(float(
                                            rec.gls_cylinder)) <= treatment_line.pro_code_id.max_cylinder)) or ((abs(float(rec.gls_left_lens_sphere)) >= treatment_line.pro_code_id.min_sphere and abs(float(
                                            rec.gls_left_lens_sphere)) <= treatment_line.pro_code_id.max_sphere and abs(float(rec.gls_left_lens_cylinder)) >= treatment_line.pro_code_id.min_cylinder and abs(float(
                                            rec.gls_left_lens_cylinder)) <= treatment_line.pro_code_id.max_cylinder)):
                                        rang = len(hcpcs_id) - 1
                                        while True:
                                            dxt = hcpcs_id[rang:][0]
                                            if 'hcpcs_code' in dxt[2]:
                                                if (4, treatment_line.pro_code_id.id) not in dxt[2]['hcpcs_code']:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                                                else:
                                                    break
                                            else:
                                                rang += 1
                                                res = (0, 0, {
                                                    'name': '',
                                                    'product_id': rec.lens_products.id,
                                                    'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                    'hcpcs_modifier': treatment_line.modifier_id.id,
                                                    'retail_price': treatment_line.price,
                                                    'sale_order_line_wizard_id': rec.id,
                                                    'categ_id': self.env['product.category'].search(
                                                        [('name', '=', 'Lens')], limit=1),
                                                    'insurance_id': rec.sale_id.insurance_id.id,
                                                }
                                                       )
                                                hcpcs_id.append(res)
                                    else:
                                        hcpcs_series = treatment_line.pro_code_id.name[0:3]
                                        procedures = rec.env['spec.procedure.code'].search(
                                            [('name', 'like', hcpcs_series), ('sphere_or_cyclinder', '=', 'sphereocyclinder')])
                                        pros = []
                                        for pro in procedures:
                                            if ((abs(float(
                                                    rec.gls_sphere)) >= pro.min_sphere and abs(float(
                                                rec.gls_sphere)) <= pro.max_sphere and abs(float(
                                                    rec.gls_cylinder)) >= pro.min_cylinder and abs(float(
                                                rec.gls_cylinder)) <= pro.max_cylinder)) or ((abs(float(
                                                    rec.gls_left_lens_sphere)) >= pro.min_sphere and abs(float(
                                                rec.gls_left_lens_sphere)) <= pro.max_sphere and abs(float(
                                                    rec.gls_left_lens_cylinder)) >= pro.min_cylinder and abs(float(
                                                rec.gls_left_lens_cylinder)) <= pro.max_cylinder)):
                                                pros.append(pro)
                                        for pr in pros:
                                            rang = len(hcpcs_id) - 1
                                            while True:
                                                dxt = hcpcs_id[rang:][0]
                                                if 'hcpcs_code' in dxt[2]:

                                                    if (4,pr.id) not in dxt[2]['hcpcs_code']:
                                                        dxt[2]['hcpcs_code'].append((4,pr.id))
                                                    else:
                                                        break
                                                else:
                                                    rang += 1
                                                    res = (0, 0, {
                                                        'name': '',
                                                        'product_id': rec.lens_products.id,
                                                        'hcpcs_code': [(4,pr.id)],
                                                        'hcpcs_modifier': treatment_line.modifier_id.id,
                                                        'retail_price': treatment_line.price,
                                                        'sale_order_line_wizard_id': rec.id,
                                                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                                                        'insurance_id': rec.sale_id.insurance_id.id,
                                                    }
                                                           )
                                                    hcpcs_id.append(res)
                            else:
                                rang = len(hcpcs_id) - 1
                                while True:
                                    dxt = hcpcs_id[rang:][0]
                                    if 'hcpcs_code' in dxt[2]:
                                        if (4,treatment_line.pro_code_id.id) not in dxt[2]['hcpcs_code']:
                                            rang += 1
                                            res = (0, 0, {
                                                'name': '',
                                                'product_id': rec.lens_products.id,
                                                'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                                'hcpcs_modifier': treatment_line.modifier_id.id,
                                                'retail_price': treatment_line.price,
                                                'sale_order_line_wizard_id': rec.id,
                                                'categ_id': self.env['product.category'].search([('name', '=', 'Lens')],
                                                                                                limit=1),
                                                'insurance_id': rec.sale_id.insurance_id.id,
                                            }
                                                   )
                                            hcpcs_id.append(res)
                                        else:
                                            break
                                    else:
                                        rang += 1
                                        res = (0, 0, {
                                            'name': '',
                                            'product_id': rec.lens_products.id,
                                            'hcpcs_code': [(4,treatment_line.pro_code_id.id)],
                                            'hcpcs_modifier': treatment_line.modifier_id.id,
                                            'retail_price': treatment_line.price,
                                            'sale_order_line_wizard_id': rec.id,
                                            'categ_id': self.env['product.category'].search([('name', '=', 'Lens')],
                                                                                            limit=1),
                                            'insurance_id': rec.sale_id.insurance_id.id,
                                        }
                                               )
                                        hcpcs_id.append(res)
                elif rec.lens_products:
                    res = (0, 0, {
                        'name': '',
                        'product_id': rec.lens_products.id,
                        'hcpcs_code': None,
                        'hcpcs_modifier': '',
                        'retail_price': 0,
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
            if rec.contact_lens_products_od.id:
                res = (0, 0, {
                    'name': rec.contact_lens_products_od.name,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                if rec.contact_lens_products_od.procedure_code.id:
                    res = (0, 0, {
                        'name': '',
                        'product_id': rec.contact_lens_products_od.id,
                        'hcpcs_code': [(4, rec.contact_lens_products_od.procedure_code.id)],
                        'retail_price': rec.contact_lens_products_od.list_price,
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Contact Lens')], limit=1),
                        'qty': rec.od_qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
                else:
                    res = (0, 0, {
                        'name': '',
                        'product_id': rec.contact_lens_products_od.id,
                        'hcpcs_code': False,
                        'retail_price': '',
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens')], limit=1),
                        'qty': rec.od_qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
            if rec.contact_lens_products_os.id:
                res = (0, 0, {
                    'name': rec.contact_lens_products_os.name,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                if rec.contact_lens_products_os.procedure_code.id:
                    res = (0, 0, {
                        'name': '',
                        'product_id': rec.contact_lens_products_os.id,
                        'hcpcs_code': [(4, rec.contact_lens_products_os.procedure_code.id)],
                        'retail_price': rec.contact_lens_products_os.list_price,
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Contact Lens')], limit=1),
                        'qty': rec.os_qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
                else:
                    res = (0, 0, {
                        'name': '',
                        'product_id': rec.contact_lens_products_os.id,
                        'hcpcs_code': False,
                        'retail_price': '',
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Contact Lens')], limit=1),
                        'qty': rec.os_qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
            for product in rec.miscellaneous_products:
                res = (0, 0, {
                    'name': product.miscellaneous_products.description,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                if product.miscellaneous_products.procedure_code:
                    res = (0, 0, {
                        'name': '',
                        'product_id': product.miscellaneous_products.id,
                        'hcpcs_code': [(4,product.miscellaneous_products.procedure_code.id)],
                        'retail_price': product.miscellaneous_products.list_price,
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Accessory')], limit=1),
                        'qty': product.qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
                else:
                    res = (0, 0, {
                        'name': '',
                        'product_id': product.miscellaneous_products.id,
                        'hcpcs_code': None,
                        'retail_price': '',
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Accessory')], limit=1),
                        'qty': product.qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
            for lens_treatment in rec.lenstreatment_products:
                res = (0, 0, {
                    'name': lens_treatment.name,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                if lens_treatment.treatment_line_ids:
                    for hcpcs_code in lens_treatment.treatment_line_ids:
                        res = (0, 0, {
                            'name': '',
                            'product_id': lens_treatment.ids[0],
                            'hcpcs_code': [(4,hcpcs_code.pro_code_id.id)],
                            'hcpcs_modifier': hcpcs_code.modifier_id.id,
                            'retail_price': hcpcs_code.price,
                            'sale_order_line_wizard_id': rec.id,
                            'categ_id': self.env['product.category'].search([('name', '=', 'Lens Treatment')], limit=1),
                            'insurance_id': rec.sale_id.insurance_id.id,
                        }
                               )
                        hcpcs_id.append(res)
                elif lens_treatment:
                    res = (0, 0, {
                        'name': '',
                        'product_id': lens_treatment.ids[0],
                        'hcpcs_code': None,
                        'hcpcs_modifier': '',
                        'retail_price': 0,
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Lens Treatment')], limit=1),
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
            for service in rec.service_products:
                res = (0, 0, {
                    'name': service.service_products.name,
                    'display_type': 'line_section',
                }
                       )
                hcpcs_id.append(res)
                if service.service_products.ser_pro_code_id:
                    res = (0, 0, {
                        'name': '',
                        'product_id': service.service_products.id,
                        'hcpcs_code': [(4,service.service_products.ser_pro_code_id.id)],
                        'retail_price': service.service_products.list_price,
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Services')], limit=1),
                        'line_id': service.id,
                        'qty': service.qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)
                else:
                    res = (0, 0, {
                        'name': '',
                        'product_id': service.service_products.id,
                        'hcpcs_code': None,
                        'retail_price': '',
                        'sale_order_line_wizard_id': rec.id,
                        'categ_id': self.env['product.category'].search([('name', '=', 'Services')], limit=1),
                        'line_id': '',
                        'qty': service.qty,
                        'insurance_id': rec.sale_id.insurance_id.id,
                    }
                           )
                    hcpcs_id.append(res)

            rec.update({'hcpcs_id': hcpcs_id})

    @api.onchange('reading_rx')
    def reading_rx_function(self):
        for rec in self:
            if rec.reading_rx:
                rec.gls_sphere = "{:.2f}".format(float(rec.gls_add) + float(rec.gls_sphere))
                rec.gls_left_lens_sphere = "{:.2f}".format(float(rec.gls_left_lens_add) + float(rec.gls_left_lens_sphere))
                rec.gls_add = None
                rec.gls_left_lens_add = None
                rec.lens_type_add = False
            return {
                'type': 'ir.actions.do_nothing'
            }

    @api.onchange('distance_rx')
    def distance_rx_function(self):
        for rec in self:
            if rec.distance_rx:
                rec.gls_add = None
                rec.gls_left_lens_add = None
                rec.lens_type_add = False
            return {
                'type': 'ir.actions.do_nothing'
            }

    @api.onchange('lens_type_add')
    def _lens_products_domain(self):
        for rec in self:
            if rec.lens_type_add:
                domain = [('product_tmpl_id.categ_id.name', '=', 'Lens'),
                          ('lens_type_id', 'in', rec.env['spec.lens.type'].search([('name', 'in', ['Bifocal', 'Bifocal', 'Bifocal', 'Progressive'])]).ids)]
                return {'domain': {'lens_products': domain}}
            else:
                domain = [('product_tmpl_id.categ_id.name', '=', 'Lens'),
                          ('lens_type_id', 'in', rec.env['spec.lens.type'].search([('name', 'in', ['Single Vision', 'SV'])]).ids)]
                return {'domain': {'lens_products': domain}}

    @api.onchange('prescription_id')
    def prescription_validations(self):
        for rec in self:
            if rec.prescription_id:
                rec.reading_rx = False
                if rec.prescription_id.gls_add or rec.prescription_id.gls_left_lens_add:
                    rec.lens_type_add = True
                else:
                    rec.lens_type_add = False

                #for glasses
                rec.gls_sphere = rec.prescription_id.gls_sphere
                rec.gls_add = rec.prescription_id.gls_add
                rec.gls_axis = rec.prescription_id.gls_axis
                rec.gls_cylinder = rec.prescription_id.gls_cylinder
                rec.gls_left_lens_sphere = rec.prescription_id.gls_left_lens_sphere
                rec.gls_left_lens_axis = rec.prescription_id.gls_left_lens_axis
                rec.gls_left_lens_add = rec.prescription_id.gls_left_lens_add
                rec.gls_left_lens_cylinder = rec.prescription_id.gls_left_lens_cylinder
                if rec.prescription_id.name.id:
                    rec.physician_id = rec.prescription_id.name.id
                if rec.prescription_id.expiration_date and rec.prescription_id.expiration_date < date.today():
                    return {'warning': {'title': _("User Alert!"),
                                        'message': _(
                                            "You Selected Expired Prescription")}}
            else:
                rec.lens_type_add = False

    @api.onchange('insurance_id')
    def reset_values(self):
        for rec in self:
            if len(rec.hcpcs_id) > 0 and rec.insurance_id.id == 0:
                rec.authorization_id = False
                rec.hcpcs_frame_onchange()
            #     for hcpcs in rec.hcpcs_id:
            #         hcpcs.unlink()

    @api.onchange('a')
    def _onchange_patients_own_frame_a(self):
        for res in self:
            if res.order_type_name == "Lenses Only":
                res.a_lab_details = res.a

    @api.onchange('b')
    def _onchange_patients_own_frame_b(self):
        for res in self:
            if res.order_type_name == "Lenses Only":
                res.b_lab_details = res.b

    @api.onchange('dbl')
    def _onchange_patients_own_frame_dbl(self):
        for res in self:
            if res.order_type_name == "Lenses Only":
                res.dbl_lab_details = res.dbl

    @api.onchange('ed')
    def _onchange_patients_own_frame_ed(self):
        for res in self:
            if res.order_type_name == "Lenses Only":
                res.ed_lab_details = res.ed
