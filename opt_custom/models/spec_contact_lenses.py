# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning
from datetime import date, datetime
import dateutil.rrule as rrule
import re
from dateutil.relativedelta import relativedelta
from email.policy import default
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG

sphere_list = [
    ('30.00', '+30.00'), ('29.75', '+29.75'), ('29.50', '+29.50'), ('29.25', '+29.25'), ('29.00', '+29.00'),
    ('28.75', '+28.75'), ('28.50', '+28.50'), ('28.25', '+28.25'), ('28.00', '+28.00'),
    ('27.75', '+27.75'), ('27.50', '+27.50'), ('27.25', '+27.25'), ('27.00', '+27.00'),
    ('26.75', '+26.75'), ('26.50', '+26.50'), ('26.25', '+26.25'), ('26.00', '+26.00'),
    ('25.75', '+25.75'), ('25.50', '+25.50'), ('25.25', '+25.25'), ('25.00', '+25.00'),
    ('24.75', '+24.75'), ('24.50', '+24.50'), ('24.25', '+24.25'), ('24.00', '+24.00'),
    ('23.75', '+23.75'), ('23.50', '+23.50'), ('23.25', '+23.25'), ('23.00', '+23.00'),
    ('22.75', '+22.75'), ('22.50', '+22.50'), ('22.25', '+22.25'), ('22.00', '+22.00'),
    ('21.75', '+21.75'), ('21.50', '+21.50'), ('21.25', '+21.25'), ('21.00', '+21.00'),
    ('20.75', '+20.75'), ('20.50', '+20.50'), ('20.25', '+20.25'), ('20.00', '+20.00'),
    ('19.75', '+19.75'), ('19.50', '+19.50'), ('19.25', '+19.25'), ('19.00', '+19.00'),
    ('18.75', '+18.75'), ('18.50', '+18.50'), ('18.25', '+18.25'), ('18.00', '+18.00'),
    ('17.75', '+17.75'), ('17.50', '+17.50'), ('17.25', '+17.25'), ('17.00', '+17.00'),
    ('16.75', '+16.75'), ('16.50', '+16.50'), ('16.25', '+16.25'), ('16.00', '+16.00'),
    ('15.75', '+15.75'), ('15.50', '+15.50'), ('15.25', '+15.25'), ('15.00', '+15.00'),
    ('14.75', '+14.75'), ('14.50', '+14.50'), ('14.25', '+14.25'), ('14.00', '+14.00'),
    ('13.75', '+13.75'), ('13.50', '+13.50'), ('13.25', '+13.25'), ('13.00', '+13.00'),
    ('12.75', '+12.75'), ('12.50', '+12.50'), ('12.25', '+12.25'), ('12.00', '+12.00'),
    ('11.75', '+11.75'), ('11.50', '+11.50'), ('11.25', '+11.25'), ('11.00', '+11.00'),
    ('10.75', '+10.75'), ('10.50', '+10.50'), ('10.25', '+10.25'), ('10.00', '+10.00'),
    ('9.75', '+9.75'), ('9.50', '+9.50'), ('9.25', '+9.25'), ('9.00', '+9.00'),
    ('8.75', '+8.75'), ('8.50', '+8.50'), ('8.25', '+8.25'), ('8.00', '+8.00'),
    ('7.75', '+7.75'), ('7.50', '+7.50'), ('7.25', '+7.25'), ('7.00', '+7.00'),
    ('6.75', '+6.75'), ('6.50', '+6.50'), ('6.25', '+6.25'), ('6.00', '+6.00'),
    ('5.75', '+5.75'), ('5.50', '+5.50'), ('5.25', '+5.25'), ('5.00', '+5.00'),
    ('4.75', '+4.75'), ('4.50', '+4.50'), ('4.25', '+4.25'), ('4.00', '+4.00'),
    ('3.75', '+3.75'), ('3.50', '+3.50'), ('3.25', '+3.25'), ('3.00', '+3.00'),
    ('2.75', '+2.75'), ('2.50', '+2.50'), ('2.25', '+2.25'), ('2.00', '+2.00'),
    ('1.75', '+1.75'), ('1.50', '+1.50'), ('1.25', '+1.25'), ('1.00', '+1.00'),
    ('0.75', '+0.75'), ('0.50', '+0.50'), ('0.25', '+0.25'),
    ('0.00', 'PL'),
    ('-0.25', '-0.25'), ('-0.50', '-0.50'), ('-0.75', '-0.75'), ('-1.00', '-1.00'), ('-1.25', '-1.25'),
    ('-1.50', '-1.50'), ('-1.75', '-1.75'), ('-2.00', '-2.00'), ('-2.25', '-2.25'), ('-2.50', '-2.50'),
    ('-2.75', '-2.75'), ('-3.00', '-3.00'), ('-3.25', '-3.25'), ('-3.50', '-3.50'), ('-3.75', '-3.75'),
    ('-4.00', '-4.00'), ('-4.25', '-4.25'), ('-4.50', '-4.50'), ('-4.75', '-4.75'), ('-5.00', '-5.00'),
    ('-5.25', '-5.25'), ('-5.50', '-5.50'), ('-5.75', '-5.75'), ('-6.00', '-6.00'), ('-6.25', '-6.25'),
    ('-6.50', '-6.50'), ('-6.75', '-6.75'), ('-7.00', '-7.00'), ('-7.25', '-7.25'), ('-7.50', '-7.50'),
    ('-7.75', '-7.75'), ('-8.00', '-8.00'), ('-8.25', '-8.25'), ('-8.50', '-8.50'), ('-8.75', '-8.75'),
    ('-9.00', '-9.00'), ('-9.25', '-9.25'), ('-9.50', '-9.50'), ('-9.75', '-9.75'), ('-10.00', '-10.00'),
    ('-10.25', '-10.25'), ('-10.50', '-10.50'), ('-10.75', '-10.75'), ('-11.00', '-11.00'), ('-11.25', '-11.25'),
    ('-11.50', '-11.50'), ('-11.75', '-11.75'), ('-12.00', '-12.00'), ('-12.25', '-12.25'), ('-12.50', '-12.50'),
    ('-12.75', '-12.75'), ('-13.00', '-13.00'), ('-13.25', '-13.25'), ('-13.50', '-13.50'), ('-13.75', '-13.75'),
    ('-14.00', '-14.00'), ('-14.25', '-14.25'), ('-14.50', '-14.50'), ('-14.75', '-14.75'), ('-15.00', '-15.00'),
    ('-15.25', '-15.25'), ('-15.50', '-15.50'), ('-15.75', '-15.75'), ('-16.00', '-16.00'), ('-16.25', '-16.25'),
    ('-16.50', '-16.50'), ('-16.75', '-16.75'), ('-17.00', '-17.00'), ('-17.25', '-17.25'), ('-17.50', '-17.50'),
    ('-17.75', '-17.75'), ('-18.00', '-18.00'), ('-18.25', '-18.25'), ('-18.50', '-18.50'), ('-18.75', '-18.75'),
    ('-19.00', '-19.00'), ('-19.25', '-19.25'), ('-19.50', '-19.50'), ('-19.75', '-19.75'), ('-20.00', '-20.00'),
    ('-20.25', '-20.25'), ('-20.50', '-20.50'), ('-20.75', '-20.75'), ('-21.00', '-21.00'), ('-21.25', '-21.25'),
    ('-21.50', '-21.50'), ('-21.75', '-21.75'), ('-22.00', '-22.00'), ('-22.25', '-22.25'), ('-22.50', '-22.50'),
    ('-22.75', '-22.75'), ('-23.00', '-23.00'), ('-23.25', '-23.25'), ('-23.50', '-23.50'), ('-23.75', '-23.75'),
    ('-24.00', '-24.00'), ('-24.25', '-24.25'), ('-24.50', '-24.50'), ('-24.75', '-24.75'), ('-25.00', '-25.00'),
    ('-25.25', '-25.25'), ('-25.50', '-25.50'), ('-25.75', '-25.75'), ('-26.00', '-26.00'), ('-26.25', '-26.25'),
    ('-26.50', '-26.50'), ('-26.75', '-26.75'), ('-27.00', '-27.00'), ('-27.25', '-27.25'), ('-27.50', '-27.50'),
    ('-27.75', '-27.75'), ('-28.00', '-28.00'), ('-28.25', '-28.25'), ('-28.50', '-28.50'), ('-28.75', '-28.75'),
    ('-29.00', '-29.00'), ('-29.25', '-29.25'), ('-29.50', '-29.50'), ('-29.75', '-29.75'), ('-30.00', '-30.00'),
]
cylinder_list = [
    ('20.00', '+20.00'),
    ('19.75', '+19.75'), ('19.50', '+19.50'), ('19.25', '+19.25'), ('19.00', '+19.00'),
    ('18.75', '+18.75'), ('18.50', '+18.50'), ('18.25', '+18.25'), ('18.00', '+18.00'),
    ('17.75', '+17.75'), ('17.50', '+17.50'), ('17.25', '+17.25'), ('17.00', '+17.00'),
    ('16.75', '+16.75'), ('16.50', '+16.50'), ('16.25', '+16.25'), ('16.00', '+16.00'),
    ('15.75', '+15.75'), ('15.50', '+15.50'), ('15.25', '+15.25'), ('15.00', '+15.00'),
    ('14.75', '+14.75'), ('14.50', '+14.50'), ('14.25', '+14.25'), ('14.00', '+14.00'),
    ('13.75', '+13.75'), ('13.50', '+13.50'), ('13.25', '+13.25'), ('13.00', '+13.00'),
    ('12.75', '+12.75'), ('12.50', '+12.50'), ('12.25', '+12.25'), ('12.00', '+12.00'),
    ('11.75', '+11.75'), ('11.50', '+11.50'), ('11.25', '+11.25'), ('11.00', '+11.00'),
    ('10.75', '+10.75'), ('10.50', '+10.50'), ('10.25', '+10.25'), ('10.00', '+10.00'),
    ('9.75', '+9.75'), ('9.50', '+9.50'), ('9.25', '+9.25'), ('9.00', '+9.00'),
    ('8.75', '+8.75'), ('8.50', '+8.50'), ('8.25', '+8.25'), ('8.00', '+8.00'),
    ('7.75', '+7.75'), ('7.50', '+7.50'), ('7.25', '+7.25'), ('7.00', '+7.00'),
    ('6.75', '+6.75'), ('6.50', '+6.50'), ('6.25', '+6.25'), ('6.00', '+6.00'),
    ('5.75', '+5.75'), ('5.50', '+5.50'), ('5.25', '+5.25'), ('5.00', '+5.00'),
    ('4.75', '+4.75'), ('4.50', '+4.50'), ('4.25', '+4.25'), ('4.00', '+4.00'),
    ('3.75', '+3.75'), ('3.50', '+3.50'), ('3.25', '+3.25'), ('3.00', '+3.00'),
    ('2.75', '+2.75'), ('2.50', '+2.50'), ('2.25', '+2.25'), ('2.00', '+2.00'),
    ('1.75', '+1.75'), ('1.50', '+1.50'), ('1.25', '+1.25'), ('1.00', '+1.00'),
    ('0.75', '+0.75'), ('0.50', '+0.50'), ('0.25', '+0.25'),
    ('0.00', 'D.S.'),
    ('-0.25', '-0.25'), ('-0.50', '-0.50'), ('-0.75', '-0.75'), ('-1.00', '-1.00'), ('-1.25', '-1.25'),
    ('-1.50', '-1.50'), ('-1.75', '-1.75'), ('-2.00', '-2.00'), ('-2.25', '-2.25'), ('-2.50', '-2.50'),
    ('-2.75', '-2.75'), ('-3.00', '-3.00'), ('-3.25', '-3.25'), ('-3.50', '-3.50'), ('-3.75', '-3.75'),
    ('-4.00', '-4.00'), ('-4.25', '-4.25'), ('-4.50', '-4.50'), ('-4.75', '-4.75'), ('-5.00', '-5.00'),
    ('-5.25', '-5.25'), ('-5.50', '-5.50'), ('-5.75', '-5.75'), ('-6.00', '-6.00'), ('-6.25', '-6.25'),
    ('-6.50', '-6.50'), ('-6.75', '-6.75'), ('-7.00', '-7.00'), ('-7.25', '-7.25'), ('-7.50', '-7.50'),
    ('-7.75', '-7.75'), ('-8.00', '-8.00'), ('-8.25', '-8.25'), ('-8.50', '-8.50'), ('-8.75', '-8.75'),
    ('-9.00', '-9.00'), ('-9.25', '-9.25'), ('-9.50', '-9.50'), ('-9.75', '-9.75'), ('-10.00', '-10.00'),
    ('-10.25', '-10.25'), ('-10.50', '-10.50'), ('-10.75', '-10.75'), ('-11.00', '-11.00'), ('-11.25', '-11.25'),
    ('-11.50', '-11.50'), ('-11.75', '-11.75'), ('-12.00', '-12.00'), ('-12.25', '-12.25'), ('-12.50', '-12.50'),
    ('-12.75', '-12.75'), ('-13.00', '-13.00'), ('-13.25', '-13.25'), ('-13.50', '-13.50'), ('-13.75', '-13.75'),
    ('-14.00', '-14.00'), ('-14.25', '-14.25'), ('-14.50', '-14.50'), ('-14.75', '-14.75'), ('-15.00', '-15.00'),
    ('-15.25', '-15.25'), ('-15.50', '-15.50'), ('-15.75', '-15.75'), ('-16.00', '-16.00'), ('-16.25', '-16.25'),
    ('-16.50', '-16.50'), ('-16.75', '-16.75'), ('-17.00', '-17.00'), ('-17.25', '-17.25'), ('-17.50', '-17.50'),
    ('-17.75', '-17.75'), ('-18.00', '-18.00'), ('-18.25', '-18.25'), ('-18.50', '-18.50'), ('-18.75', '-18.75'),
    ('-19.00', '-19.00'), ('-19.25', '-19.25'), ('-19.50', '-19.50'), ('-19.75', '-19.75'), ('-20.00', '-20.00'),
]
axis_list = [('1', '001'), ('2', '002'), ('3', '003'), ('4', '004'), ('5', '005'), ('6', '006'), ('7', '007'),
             ('08', '008'), ('09', '009'), ('10', '010'), ('11', '011'), ('12', '012'),
             ('13', '013'), ('14', '014'), ('15', '015'), ('16', '016'), ('17', '017'), ('18', '018'), ('19', '019'),
             ('20', '020'), ('21', '021'), ('22', '022'), ('23', '023'), ('24', '024'),
             ('25', '025'), ('26', '026'), ('27', '027'), ('28', '028'), ('29', '029'), ('30', '030'), ('31', '031'),
             ('32', '032'), ('33', '033'), ('34', '034'), ('35', '035'), ('36', '036'),
             ('37', '037'), ('38', '038'), ('39', '039'), ('40', '040'), ('41', '041'), ('42', '042'), ('43', '043'),
             ('44', '044'), ('45', '045'), ('46', '046'), ('47', '047'), ('48', '048'),
             ('49', '049'), ('050', '050'), ('51', '051'), ('52', '052'), ('53', '053'), ('54', '054'), ('55', '055'),
             ('56', '056'), ('57', '057'), ('58', '058'), ('59', '059'), ('60', '060'),
             ('61', '061'), ('62', '062'), ('63', '063'), ('64', '064'), ('65', '065'), ('66', '066'), ('67', '067'),
             ('68', '068'), ('69', '069'), ('70', '070'), ('71', '071'), ('72', '072'),
             ('73', '073'), ('74', '074'), ('75', '075'), ('76', '076'), ('77', '077'), ('78', '078'), ('79', '079'),
             ('80', '080'), ('81', '081'), ('82', '082'), ('83', '083'), ('84', '084'),
             ('85', '085'), ('86', '086'), ('87', '087'), ('88', '088'), ('89', '089'), ('90', '090'), ('91', '091'),
             ('92', '092'), ('93', '093'), ('094', '094'), ('95', '095'), ('096', '096'),
             ('97', '097'), ('98', '098'), ('99', '099'), ('100', '100'), ('101', '101'), ('102', '102'),
             ('103', '103'), ('104', '104'), ('105', '105'), ('106', '106'), ('107', '107'), ('108', '108'),
             ('109', '109'), ('110', '110'), ('111', '111'), ('112', '112'), ('113', '113'), ('114', '114'),
             ('115', '115'), ('116', '116'), ('117', '117'), ('118', '118'), ('119', '119'), ('120', '120'),
             ('121', '121'), ('122', '122'), ('123', '123'), ('124', '124'), ('125', '125'), ('126', '126'),
             ('127', '127'), ('128', '128'), ('129', '129'), ('130', '130'), ('131', '131'), ('132', '132'),
             ('133', '133'), ('134', '134'), ('135', '135'), ('136', '136'), ('137', '137'), ('138', '138'),
             ('139', '139'), ('140', '140'), ('141', '141'), ('142', '142'), ('143', '143'), ('144', '144'),
             ('145', '145'), ('146', '146'), ('147', '147'), ('148', '148'), ('149', '149'), ('150', '150'),
             ('151', '151'), ('152', '152'), ('153', '153'), ('154', '154'), ('155', '155'), ('156', '156'),
             ('157', '157'), ('158', '158'), ('159', '159'), ('160', '160'), ('161', '161'), ('162', '162'),
             ('163', '163'), ('164', '164'), ('165', '165'), ('166', '166'), ('167', '167'), ('168', '168'),
             ('169', '169'), ('170', '170'), ('171', '171'), ('172', '172'), ('173', '173'), ('174', '174'),
             ('175', '175'), ('176', '176'), ('177', '177'), ('178', '178'), ('179', '179'), ('180', '180')]
add_list = [('0.00', '+0.00'), ('0.25', '+0.25'), ('0.50', '+0.50'), ('0.75', '+0.75'), ('1.00', '+1.00'),
            ('1.25', '+1.25'), ('1.50', '+1.50'), ('1.75', '+1.75'), ('2.00', '+2.00'), ('2.25', '+2.25'),
            ('2.50', '+2.50'), ('2.75', '+2.75'), ('3.00', '+3.00'), ('3.25', '+3.25'), ('3.50', '+3.50'),
            ('3.75', '+3.75'), ('4.00', '+4.00'), ('4.25', '+4.25'), ('4.50', '+4.50'), ('4.75', '+4.75'),
            ('5.00', '+5.00'),
            ('5.25', '+5.25'), ('5.50', '+5.50'), ('5.75', '+5.75'), ('6.00', '+6.00')]


class ContactLens(models.Model):
    _name = 'spec.contact.lenses'
    _description = 'Contact Lens'
    _order = "discontinued, expiration_date DESC"

    # def _compute_advance_expiration_date(self):
    #     for rec in self:
    #         rec.advance_expiration_date = ''
    #         if rec.expiration_date:
    #             rec.advance_expiration_date = rec.expiration_date.strftime('%m/%d/%Y')
    #             rec.discontinued = False
    #             if rec.discontinue_date:
    #                 if rec.expiration_date > rec.discontinue_date:
    #                     rec.advance_expiration_date += " (Discontinued)"
    #                     rec.discontinued = True
    #             if rec.expiration_date < fields.date.today():
    #                 rec.advance_expiration_date += " (Expired)"

    advance_expiration_date = fields.Char(string='Expiration Date')
    # advance_expiration_date = fields.Char(string='Expiration Date')
    discontinued = fields.Boolean(string="Discontinued", default=True)

    provide = fields.Selection([('provide', 'Provider'), ('outside_provide', 'Outside Provider')], default='provide',
                               string="Provider")
    name = fields.Many2one('hr.employee', string="Provider",
                           domain="['|', ('doctor','=',True), ('is_outside_doctor','=',True)]")
    outsider_name = fields.Many2one('hr.employee', string="Provider",
                                    domain="['|', ('doctor','=',True), ('is_outside_doctor','=',True)]")

    @api.onchange('outsider_name')
    def _onchange_outsider_name(self):
        for res in self:
            res.name = res.outsider_name.id

    rx_type_char = fields.Char(string="Type")
    # outsider_name = fields.Many2one('outside.doctor.class', string='Outside Provider')
    rx = fields.Selection([('glasses', 'Glasses'), ('soft', 'Soft Contact Lens'), ('hard', 'Hard Contact Lens')],
                          string="Rx", default='glasses')
    rx_usage = fields.Selection(
        [('distance', 'Distance'), ('computer', 'Computer'), ('computer_over_contacts', 'Computer Over Contacts'),
         ('occupational', 'Occupational'), ('ready_over_contacts', 'Ready Over Contacts'),
         ('full_time_wear,', 'Full Time Wear'),
         ('sports_hobby', 'Sports/Hobby')], string="Rx Usage")
    rx_usage_id = fields.Many2one('spec.rx.usage', string="Rx Usage")
    discontinue_reason = fields.Many2one('rx.discontinue.reason', string="Discontinue Reason")
    discontinue_date = fields.Date(string="Discontinue Date", default=fields.Date.today())
    exam_date = fields.Date(string="Exam Date", default=fields.Date.today())
    expiration_date = fields.Date(string="Expiration Date")
    """Soft Conatct Lens Fields"""
    soft_manufacturer_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Contact Lens')]",
                                           string="Manufacturer & Brand")
    soft_style = fields.Char(string="Style")
    soft_color = fields.Char(string="Color")
    select_soft_color = fields.Char(string="Color")
    soft_base_curve = fields.Char(string="Base Curve")
    select_soft_base_curve = fields.Char(string="Base Curve")
    # soft_base_curve = fields.Selection(selection="get_soft_sphere_list", string="Base Curve")
    soft_diameter = fields.Char(string="Diameter")
    select_soft_diameter = fields.Char(string="Diameter")
    soft_sphere = fields.Char(string="Sphere")
    # select_soft_sphere = fields.Char(string="Sphere")
    select_soft_sphere = fields.Selection(sphere_list, string="Sphere", default='0.00')
    soft_cylinder = fields.Char(string="Cylinder")
    select_soft_cylinder = fields.Selection(cylinder_list, string="Cylinder", default='0.00')
    soft_axis = fields.Char(string="Axis")
    select_soft_axis = fields.Selection(axis_list, string="Axis")
    soft_add_power = fields.Char(string="Add Power")
    select_soft_add_power = fields.Selection(add_list, string="Add Power")
    soft_va = fields.Char(string="VA")
    select_soft_va = fields.Char(string="VA")
    soft_multifocal = fields.Char(string="Multifocal")
    select_soft_multifocal = fields.Char(string="Multifocal")
    soft_left_manufacturer_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Contact Lens')]",
                                                string="Manufacturer & Brand", default="")
    soft_left_style = fields.Char(string="Style")
    soft_left_color = fields.Char(string="Color")
    soft_left_base_curve = fields.Char(string="Base Curve")
    soft_left_diameter = fields.Char(string="Diameter")
    soft_left_sphere = fields.Selection(sphere_list, string="Sphere", default='0.00')
    soft_left_cylinder = fields.Selection(cylinder_list, string="Cylinder", default='0.00')
    soft_left_axis = fields.Selection(axis_list, string="Axis")
    soft_left_add_power = fields.Selection(add_list, string="Add Power")
    soft_left_va = fields.Char(string="VA")
    soft_left_multifocal = fields.Char(string="Multifocal")
    wearing_schedulen = fields.Many2one('spec.contact.lens.wear.period', string="Wearing Period")
    replcement = fields.Many2one('spec.contact.lens.replacement.schedule', string="Replacement")
    """Hard Contact Lens Fields"""
    """OD"""
    manufacturer_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Contact Lens'), ('lens_type', '=', 'rgp')]",
                                      string="Manufacturer")
    style = fields.Char(string="Name")
    material = fields.Char(string="Material")
    base_curve = fields.Char(string="BC")
    diameter = fields.Char(string="Diameter")
    sphere = fields.Selection(sphere_list, string="Sphere", default='0.00')
    cylinder = fields.Selection(cylinder_list, string="Cylinder", default='0.00')
    axis = fields.Selection(axis_list, string="Axis")
    add = fields.Selection(add_list, string="Add")
    seg_height = fields.Char(string="Seg  Ht")
    pc_radius = fields.Char(string="PC Radius")
    pc_width = fields.Char(string="PC width")
    ct = fields.Char(string="CT")
    oz = fields.Char(string="OZ")
    base_curve_2 = fields.Char(string="BC 2")
    color = fields.Selection([('clear', 'Clear'), ('dlue', 'Blue')], string="Color")
    sphere_2 = fields.Char(string="Sph 2")
    axis_2 = fields.Char(string="Axis 2")
    cylinder_2 = fields.Char(string="Cyl 2")
    add_diam_2 = fields.Char(string="Add Diam")
    dot = fields.Boolean(string="Dot")
    """OS"""
    left_manufacturer_id = fields.Many2one('product.template', domain="[('categ_id.name','=','Contact Lens'), ('lens_type', '=', 'rgp')]",
                                           string="Manufacturer")
    left_style = fields.Char(string="Name")
    left_material = fields.Char(string="Material")
    left_base_curve = fields.Char(string="BC")
    left_diameter = fields.Char(string="Diameter")
    left_sphere = fields.Selection(sphere_list, string="Sphere")
    left_cylinder = fields.Selection(cylinder_list, string="Cylinder")
    left_axis = fields.Selection(axis_list, string="Axis")
    left_add = fields.Selection(add_list, string="Add")
    left_seg_height = fields.Char(string="Seg Ht")
    left_pc_radius = fields.Char(string="PC Radius")
    left_ct = fields.Char(string="CT")
    left_oz = fields.Char(string="OZ")
    left_pc_width = fields.Char(string="PC width")
    left_base_curve_2 = fields.Char(string="BC 2")
    left_color = fields.Selection([('clear', 'Clear'), ('dlue', 'Blue')], string="Color")
    left_sphere_2 = fields.Char(string="Sph 2")
    left_cylinder_2 = fields.Char(string="Cyl 2")
    left_axis_2 = fields.Char(string="Axis 2")
    left_add_diam_2 = fields.Char(string="Add Diam")
    left_dot = fields.Boolean(string="Dot", default=True)
    """Glasses Fileds"""
    gls_sphere = fields.Selection(sphere_list, string='Sphere', default='0.00')
    gls_cylinder = fields.Selection(cylinder_list, string='Cylinder', default='0.00')
    gls_axis = fields.Selection(axis_list, string='Axis')
    gls_add = fields.Selection(add_list, string='Add')
    gls_h_prism = fields.Char(string="H.Prism")
    gls_v_prism = fields.Char(string="V.Prism")
    gls_h_base = fields.Selection([('bi', 'BI'), ('bo', 'BO')], string="H.Base")
    gls_v_base = fields.Selection([('bu', 'BU'), ('bd', 'BD')], string="V.Base")
    gls_pd = fields.Char(string="PD")
    gls_va = fields.Selection(
        [('20_10', '20/10'), ('20_20 ', '20/20'), ('20_30', '20/30'), ('20_40 ', '20/40'), ('20_50', '20/50'),
         ('20_60 ', '20/60'), ('20_80', '20/80'), ('20_100', '20/100'), ('20_150', '20/150'), ('20_200', '20/200'),
         ('20_400', '20/400'), ('20_800', '20/800')], string="VA")
    gls_near = fields.Selection(
        [('20_10', '20/10'), ('20_20 ', '20/20'), ('20_30', '20/30'), ('20_40 ', '20/40'), ('20_50', '20/50'),
         ('20_60 ', '20/60'), ('20_80', '20/80'), ('20_100', '20/100'), ('20_150', '20/150'), ('20_200', '20/200'),
         ('20_400', '20/400'), ('20_800', '20/800')], string="VA Near")
    gls_balance = fields.Boolean(string="Balance")
    gls_sub_cff = fields.Boolean(string="Slub Off")
    gls_left_lens_sphere = fields.Selection(sphere_list, string='Sphere', default='0.00')
    gls_left_lens_cylinder = fields.Selection(cylinder_list, string='Cylinder', default='0.00')
    gls_left_lens_axis = fields.Selection(axis_list, string='Axis')
    gls_left_lens_add = fields.Selection(add_list, string='Add')
    gls_left_lens_h_prism = fields.Char(string="H.Prism")
    gls_left_lens_v_prism = fields.Char(string="V.Prism")
    gls_left_h_base = fields.Selection([('bi', 'BI'), ('bo', 'BO')], string="H.Base")
    gls_left_v_base = fields.Selection([('bu', 'BU'), ('bd', 'BD')], string="V.Base")
    gls_left_pd = fields.Char(string="PD")
    gls_left_va = fields.Selection(
        [('20_10', '20/10'), ('20_20 ', '20/20'), ('20_30', '20/30'), ('20_40 ', '20/40'), ('20_50', '20/50'),
         ('20_60 ', '20/60'), ('20_80', '20/80'), ('20_100', '20/100'), ('20_150', '20/150'), ('20_200', '20/200'),
         ('20_400', '20/400'), ('20_800', '20/800')], string="VA")
    gls_left_near = fields.Selection(
        [('20_10', '20/10'), ('20_20 ', '20/20'), ('20_30', '20/30'), ('20_40 ', '20/40'), ('20_50', '20/50'),
         ('20_60 ', '20/60'), ('20_80', '20/80'), ('20_100', '20/100'), ('20_150', '20/150'), ('20_200', '20/200'),
         ('20_400', '20/400'), ('20_800', '20/800')], string="VA Near")
    gls_left_balance = fields.Boolean(string="Balance")
    gls_left_lens_sub_cff = fields.Boolean(string="Slab Off")
    gls_left_lens_base_curve = fields.Char(string="Base Curve")
    gls_distant = fields.Selection([('distance', 'Distance'), ('intermediate_200', 'Intermediate 200cm/80in'),
                                    ('intermediate_100', 'Intermediate 100cm/40in'),
                                    ('intermediate_65', 'Intermediate 65cm/25in'), ('reading_50', 'Reading 50cm/20in,'),
                                    ('reading_40', 'Reading 40 cm/16in'),
                                    ('reading_35', 'Reading 35cm/14in')], string="Rx Distant")
    gls_lens_style_id = fields.Many2one('spec.lens.style', string="Lens Style")
    gls_lens_material_id = fields.Many2one('spec.lens.material', string="Lens Material")
    gls_ar_coating = fields.Boolean(string="AR Coating")
    gls_photochromic = fields.Boolean(string="Photochromic")
    gls_polarized = fields.Boolean(string="Polarized")
    gls_tint = fields.Boolean(string="Tint")
    rx_notes = fields.Text(string="Rx Notes")
    partner_id = fields.Many2one('res.partner', string="Partner")
    gls_custom_cyl = fields.Float()

    @api.model
    def default_get(self, default_fields):
        res = super(ContactLens, self).default_get(default_fields)
        partner_id = self._context.get("partner_id")
        if partner_id:
            res.update({'partner_id': partner_id})
        return res

    # Report Work

    # @api.onchange('soft_left_manufacturer_id')
    # def _onchange_soft_left_manufacturer_id(self):
    #     if self.soft_left_manufacturer_id:
    #         self.soft_left_style = self.soft_left_manufacturer_id.name

    #     @api.onchange('soft_manufacturer_id')
    #     def _onchange_manufacturer(self):
    #         """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #         self.soft_base_curve = False
    #         bc = []
    #         if self.soft_manufacturer_id:
    #             # self.soft_style = self.soft_manufacturer_id.name
    #             new_value = ""
    #             for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #                 self.soft_base_curve = configurations_id.bc
    #                 self.soft_diameter = configurations_id.diam
    #                 self.soft_sphere = configurations_id.sphere
    #                 self.soft_cylinder = configurations_id.cylinder
    #                 self.soft_axis = configurations_id.axis
    #                 self.soft_add_power = configurations_id.add
    #                 self.soft_color = configurations_id.color
    #                 self.soft_multifocal = configurations_id.multi_focal
    #                 if configurations_id.bc and configurations_id.bc not in bc:
    #                     bc.append(configurations_id.bc)
    #                 if not configurations_id.bc and 'No Value' not in bc:
    #                      bc.append('No Value')
    # #                 self.soft_base_curve = configurations_id.bc
    # #                 self.soft_diameter = configurations_id.diam
    # #                 self.soft_sphere = configurations_id.sphere
    # #                 self.soft_cylinder = configurations_id.cylinder
    # #                 self.soft_axis = configurations_id.axis
    # #                 self.soft_add_power = configurations_id.add
    # #                 self.soft_color = configurations_id.color
    # #                 self.soft_multifocal = configurations_id.multi_focal
    #             new_value = ','.join(bc)
    #             if self.select_soft_base_curve == new_value :
    #                 bc.append('@@@@@@@@@@@@@@@')
    #             self.select_soft_base_curve = ','.join(bc)
    #         else:
    #             self.select_soft_base_curve = ','.join(bc)
    #         if self.soft_left_manufacturer_id:
    #             self.soft_left_style = self.soft_left_manufacturer_id.name

    # @api.onchange('soft_base_curve')
    # def _onchange_soft_base_curve(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_diameter = False
    #     soft_base_curve_value = self.soft_base_curve
    #     diameter = []
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if self.soft_base_curve:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if configurations_id.bc == soft_base_curve_value :
    #                 if configurations_id.diam and str(configurations_id.diam) not in diameter:
    #                     diameter.append(str(configurations_id.diam))
    #                 if not configurations_id.diam and 'No Value' not in diameter:
    #                     diameter.append('No Value')
    #         if not diameter:
    #             diameter.append('No Value')
    #         new_value = ','.join(diameter)
    #         if self.select_soft_diameter == new_value :
    #             diameter.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_diameter = ','.join(diameter)
    #     else:
    #         self.select_soft_diameter = ','.join(diameter)
    #
    # @api.onchange('soft_diameter')
    # def _onchange_soft_diameter(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_color = False
    #     soft_diameter_value = self.soft_diameter
    #     soft_base_curve_value = self.soft_base_curve
    #     color = []
    #     if soft_diameter_value == 'No Value':
    #         soft_diameter_value = 0.0
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if self.soft_diameter:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if str(configurations_id.diam) == str(soft_diameter_value) and str(configurations_id.bc) == str(soft_base_curve_value):
    #                 if configurations_id.color and str(configurations_id.color) not in color:
    #                     color.append(str(configurations_id.color))
    #                 if not configurations_id.color and 'No Value' not in color:
    #                     color.append('No Value')
    #         if not color:
    #             color.append('No Value')
    #         new_value = ','.join(color)
    #         if self.select_soft_color == new_value :
    #             color.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_color = ','.join(color)
    #     else:
    #         self.select_soft_color = ','.join(color)
    #
    # @api.onchange('soft_color')
    # def _onchange_soft_color(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_sphere = False
    #     soft_soft_color_value = self.soft_color
    #     soft_diameter_value = self.soft_diameter
    #     soft_base_curve_value = self.soft_base_curve
    #     sphere = []
    #     if soft_diameter_value == 'No Value':
    #         soft_diameter_value = 0.0
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if soft_soft_color_value == 'No Value':
    #         soft_soft_color_value = False
    #     if self.soft_diameter:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if str(configurations_id.diam) == str(soft_diameter_value) and str(configurations_id.bc) == str(soft_base_curve_value) \
    #                 and str(configurations_id.color) == str(soft_soft_color_value):
    #                 if configurations_id.sphere and str(configurations_id.sphere) not in sphere:
    #                     sphere.append(str(configurations_id.sphere))
    #                 if not configurations_id.sphere and 'No Value' not in sphere:
    #                     sphere.append('No Value')
    #         if not sphere:
    #             sphere.append('No Value')
    #         new_value = ','.join(sphere)
    #         if self.select_soft_sphere == new_value :
    #             sphere.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_sphere = ','.join(sphere)
    #     else:
    #         self.select_soft_sphere = ','.join(sphere)
    #
    # @api.onchange('soft_sphere')
    # def _onchange_soft_sphere(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_cylinder = False
    #     soft_base_curve_value = self.soft_base_curve
    #     soft_soft_color_value = self.soft_color
    #     soft_diameter_value = self.soft_diameter
    #     soft_sphere_value = self.soft_sphere
    #     cylinder = []
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if soft_diameter_value == 'No Value':
    #         soft_diameter_value = 0.0
    #     if soft_sphere_value == 'No Value':
    #         soft_sphere_value = 0.0
    #     if soft_soft_color_value == 'No Value':
    #         soft_soft_color_value = False
    #     if self.soft_sphere:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if str(configurations_id.bc) == str(soft_base_curve_value) and \
    #                str(configurations_id.diam) == str(soft_diameter_value) and \
    #                str(configurations_id.color) == str(soft_soft_color_value) and \
    #                str(configurations_id.sphere) == str(soft_sphere_value) :
    #                 if configurations_id.cylinder and str(configurations_id.cylinder) not in cylinder:
    #                     cylinder.append(str(configurations_id.cylinder))
    #                 if not configurations_id.cylinder and 'No Value' not in cylinder:
    #                     cylinder.append('No Value')
    #         if not cylinder:
    #             cylinder.append('No Value')
    #         new_value = ','.join(cylinder)
    #         if self.select_soft_cylinder == new_value :
    #             cylinder.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_cylinder = ','.join(cylinder)
    #     else:
    #         self.select_soft_cylinder = ','.join(cylinder)
    #
    # @api.onchange('soft_cylinder')
    # def _onchange_soft_cylinder(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_axis = False
    #     soft_base_curve_value = self.soft_base_curve
    #     soft_soft_color_value = self.soft_color
    #     soft_diameter_value = self.soft_diameter
    #     soft_sphere_value = self.soft_sphere
    #     soft_cylinder_value = self.soft_cylinder
    #     soft_axis = []
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if soft_diameter_value == 'No Value':
    #         soft_diameter_value = 0.0
    #     if soft_sphere_value == 'No Value':
    #         soft_sphere_value = 0.0
    #     if soft_soft_color_value == 'No Value':
    #         soft_soft_color_value = False
    #     if soft_cylinder_value == 'No Value':
    #         soft_cylinder_value = 0.0
    #     if self.soft_cylinder:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if str(configurations_id.bc) == str(soft_base_curve_value) and \
    #                str(configurations_id.diam) == str(soft_diameter_value) and \
    #                str(configurations_id.sphere) == str(soft_sphere_value) and \
    #                str(configurations_id.color) == str(soft_soft_color_value) and \
    #                str(configurations_id.cylinder) == str(soft_cylinder_value) :
    #                 if configurations_id.axis and str(configurations_id.axis) not in soft_axis:
    #                     soft_axis.append(str(configurations_id.axis))
    #                 if not configurations_id.axis and 'No Value' not in soft_axis:
    #                     soft_axis.append('No Value')
    #         if not soft_axis:
    #             soft_axis.append('No Value')
    #         new_value = ','.join(soft_axis)
    #         if self.select_soft_axis == new_value :
    #             soft_axis.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_axis = ','.join(soft_axis)
    #     else:
    #         self.select_soft_axis = ','.join(soft_axis)
    #
    # @api.onchange('soft_axis')
    # def _onchange_soft_axis(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_add_power = False
    #     soft_soft_color_value = self.soft_color
    #     soft_base_curve_value = self.soft_base_curve
    #     soft_diameter_value = self.soft_diameter
    #     soft_sphere_value = self.soft_sphere
    #     soft_cylinder_value = self.soft_cylinder
    #     soft_axis_value = self.soft_axis
    #     soft_add_power = []
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if soft_diameter_value == 'No Value':
    #         soft_diameter_value = 0.0
    #     if  soft_sphere_value == 'No Value':
    #         soft_sphere_value = 0.0
    #     if soft_cylinder_value == 'No Value':
    #         soft_cylinder_value = 0.0
    #     if soft_soft_color_value == 'No Value':
    #         soft_soft_color_value = False
    #     if soft_axis_value == 'No Value':
    #         soft_axis_value = False
    #     if self.soft_axis:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if str(configurations_id.bc) == str(soft_base_curve_value) and \
    #                str(configurations_id.diam) == str(soft_diameter_value) and \
    #                str(configurations_id.sphere) == str(soft_sphere_value) and \
    #                str(configurations_id.color) == str(soft_soft_color_value) and \
    #                str(configurations_id.cylinder) == str(soft_cylinder_value) and \
    #                str(configurations_id.axis) == str(soft_axis_value) :
    #                 if  configurations_id.add and str(configurations_id.add) not in soft_add_power:
    #                     soft_add_power.append(str(configurations_id.add))
    #                 if not configurations_id.add and 'No Value' not in soft_add_power:
    #                     soft_add_power.append('No Value')
    #         if not soft_add_power:
    #              soft_add_power.append('No Value')
    #         new_value = ','.join(soft_add_power)
    #         if self.select_soft_add_power == new_value :
    #             soft_add_power.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_add_power = ','.join(soft_add_power)
    #     else:
    #         self.select_soft_add_power = ','.join(soft_add_power)
    #
    # @api.onchange('soft_add_power')
    # def _onchange_soft_add_power(self):
    #     """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #     self.soft_multifocal = False
    #     soft_soft_color_value = self.soft_color
    #     soft_base_curve_value = self.soft_base_curve
    #     soft_diameter_value = self.soft_diameter
    #     soft_sphere_value = self.soft_sphere
    #     soft_cylinder_value = self.soft_cylinder
    #     soft_axis_value = self.soft_axis
    #     soft_add_power_value = self.soft_add_power
    #     soft_multifocal = []
    #     if soft_base_curve_value == 'No Value':
    #         soft_base_curve_value = False
    #     if soft_diameter_value == 'No Value':
    #         soft_diameter_value = 0.0
    #     if  soft_sphere_value == 'No Value':
    #         soft_sphere_value = 0.0
    #     if soft_cylinder_value == 'No Value':
    #         soft_cylinder_value = 0.0
    #     if  soft_axis_value == 'No Value':
    #         soft_axis_value = False
    #     if soft_soft_color_value == 'No Value':
    #         soft_soft_color_value = False
    #     if soft_add_power_value == 'No Value':
    #         soft_add_power_value = False
    #     if self.soft_add_power:
    #         new_value = ""
    #         for configurations_id in self.soft_manufacturer_id.product_variant_ids:
    #             if str(configurations_id.bc) == str(soft_base_curve_value) and \
    #                str(configurations_id.diam) == str(soft_diameter_value) and \
    #                str(configurations_id.sphere) == str(soft_sphere_value) and \
    #                str(configurations_id.color) == str(soft_soft_color_value) and \
    #                str(configurations_id.cylinder) == str(soft_cylinder_value) and \
    #                str(configurations_id.axis) == str(soft_axis_value) and \
    #                str(configurations_id.add) == str(soft_add_power_value) :
    #                 if  configurations_id.multi_focal and str(configurations_id.multi_focal) not in soft_multifocal:
    #                     soft_multifocal.append(str(configurations_id.multi_focal))
    #                 if not configurations_id.multi_focal  and 'No Value' not in soft_multifocal:
    #                     soft_multifocal.append('No Value')
    #         if not soft_multifocal:
    #             soft_multifocal.append('No Value')
    #         new_value = ','.join(soft_multifocal)
    #         if self.select_soft_multifocal == new_value :
    #             soft_multifocal.append('@@@@@@@@@@@@@@@')
    #         self.select_soft_multifocal = ','.join(soft_multifocal)
    #     else:
    #         self.select_soft_multifocal = ','.join(soft_multifocal)

    #     @api.onchange('soft_multifocal')
    #     def _onchange_soft_multifocal(self):
    #         """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #         self.soft_color = False
    #         color = []
    #         soft_base_curve_value = self.soft_base_curve
    #         soft_diameter_value = self.soft_diameter
    #         soft_sphere_value = self.soft_sphere
    #         soft_cylinder_value = self.soft_cylinder
    #         soft_axis_value = self.soft_axis
    #         soft_add_power_value = self.soft_add_power
    #         soft_multifocal_value = self.soft_multifocal
    #         if soft_base_curve_value == 'No Value':
    #             soft_base_curve_value = False
    #         if soft_diameter_value == 'No Value':
    #             soft_diameter_value = 0.0
    #         if  soft_sphere_value == 'No Value':
    #             soft_sphere_value = 0.0
    #         if soft_cylinder_value == 'No Value':
    #             soft_cylinder_value = 0.0
    #         if  soft_axis_value == 'No Value':
    #             soft_axis_value = False
    #         if soft_add_power_value == 'No Value':
    #             soft_add_power_value = False
    #         if soft_multifocal_value == 'No Value':
    #             soft_multifocal_value = False
    #         if self.soft_multifocal:
    #             new_value = ""
    #             for configurations_id in self.soft_manufacturer_id.configurations_ids:
    #                 if str(configurations_id.bc) == str(soft_base_curve_value) and \
    #                    str(configurations_id.diam) == str(soft_diameter_value) and \
    #                    str(configurations_id.sphere) == str(soft_sphere_value) and \
    #                    str(configurations_id.cylinder) == str(soft_cylinder_value) and \
    #                    str(configurations_id.axis) == str(soft_axis_value) and \
    #                    str(configurations_id.add) == str(soft_add_power_value) and \
    #                    str(configurations_id.multi_focal) == str(soft_multifocal_value) :
    #                     if configurations_id.color and str(configurations_id.color) not in color:
    #                         color.append(str(configurations_id.color))
    #                     if not configurations_id.color and 'No Value' not in color:
    #                         color.append('No Value')
    #             if not color:
    #                 color.append('No Value')
    #             new_value = ','.join(color)
    #             if self.select_soft_color == new_value :
    #                 color.append('@@@@@@@@@@@@@@@')
    #             self.select_soft_color = ','.join(color)
    #         else:
    #             self.select_soft_color = ','.join(color)

    #    @api.onchange('soft_color')
    #    def _onchange_soft_color(self):
    #        """ Onchnage on Manufacture id for soft or right and left and right lens"""
    #        self.soft_va = False
    #        self.select_soft_va = False
    #        soft_base_curve_value = self.soft_base_curve
    #        soft_diameter_value = self.soft_diameter
    #        soft_sphere_value = self.soft_sphere
    #        soft_cylinder_value = self.soft_cylinder
    #        soft_axis_value = self.soft_axis
    #        soft_add_power_value = self.soft_add_power
    #        soft_multifocal_value = self.soft_multifocal
    #        soft_color_value = self.soft_color
    #        soft_va = []
    #        if soft_base_curve_value == 'No Value':
    #            soft_base_curve_value = False
    #        if soft_diameter_value == 'No Value':
    #            soft_diameter_value = 0.0
    #        if  soft_sphere_value == 'No Value':
    #            soft_sphere_value = 0.0
    #        if soft_cylinder_value == 'No Value':
    #            soft_cylinder_value = 0.0
    #        if  soft_axis_value == 'No Value':
    #            soft_axis_value = False
    #        if soft_add_power_value == 'No Value':
    #            soft_add_power_value = False
    #        if soft_multifocal_value == 'No Value':
    #            soft_multifocal_value = False
    #        if soft_color_value == 'No Value':
    #            soft_color_value = False
    #        if self.soft_color:
    #            for configurations_id in self.soft_manufacturer_id.configurations_ids:
    #                if str(configurations_id.bc) == str(soft_base_curve_value) and \
    #                   str(configurations_id.diam) == str(soft_diameter_value) and \
    #                   str(configurations_id.sphere) == str(soft_sphere_value) and \
    #                   str(configurations_id.cylinder) == str(soft_cylinder_value) and \
    #                   str(configurations_id.axis) == str(soft_axis_value) and \
    #                   str(configurations_id.add) == str(soft_add_power_value) and \
    #                   str(configurations_id.multi_focal) == str(soft_multifocal_value) and \
    #                   str(configurations_id.color) == str(soft_color_value) :
    #                    if configurations_id.upc and str(configurations_id.upc) not in soft_va:
    #                        soft_va.append(str(configurations_id.upc))
    #                    if not configurations_id.upc and 'No Value' not in soft_va:
    #                        soft_va.append('No Value')
    #            if not soft_va:
    #                soft_va.append('No Value')
    #            self.select_soft_va = ','.join(soft_va)

    @api.onchange('manufacturer_id', 'left_manufacturer_id', 'exam_date', 'rx')
    def _onchange_hard_manufacturer(self):
        if self.manufacturer_id:
            self.style = self.manufacturer_id.name
            # for configurations_id in self.manufacturer_id.product_variant_ids:
            #     self.base_curve = configurations_id.bc
            #     self.diameter = configurations_id.diam
            #     self.sphere = configurations_id.sphere
            #     self.cylinder = configurations_id.cylinder
            #     self.axis = configurations_id.axis
            #     self.style = self.manufacturer_id.name
        if self.left_manufacturer_id:
            self.style = self.left_manufacturer_id.name
            # for configurations_id in self.manufacturer_id.product_variant_ids:
            #     self.left_base_curve = configurations_id.bc
            #     self.left_diameter = configurations_id.diam
            #     self.left_sphere = configurations_id.sphere
            #     self.left_cylinder = configurations_id.cylinder
            #     self.left_axis = configurations_id.axis
            #     self.left_style = self.manufacturer_id.name

    @api.onchange('discontinue_reason')
    def onchange_discontinue_reason(self):
        if self.discontinue_reason.id:
            self.discontinue_date = fields.Date.today()
        else:
            self.discontinue_date = False

    def hard_copy_to_left(self):
        self.left_manufacturer_id = self.manufacturer_id.id
        self.left_style = self.style
        self.left_material = self.material
        self.left_base_curve = self.base_curve
        self.left_diameter = self.diameter
        self.left_sphere = self.sphere
        self.left_cylinder = self.cylinder
        self.left_axis = self.axis
        self.left_add = self.add
        self.left_seg_height = self.seg_height
        self.left_pc_radius = self.pc_radius

        self.left_pc_width = self.pc_width
        self.left_ct = self.ct
        self.left_oz = self.oz
        self.left_base_curve_2 = self.base_curve_2
        self.left_color = self.color
        self.left_sphere_2 = self.sphere_2
        self.left_cylinder_2 = self.cylinder_2
        self.left_axis_2 = self.axis_2
        self.left_add_diam_2 = self.add_diam_2
        self.left_dot = self.dot

    def soft_copy_to_left(self):
        if self.soft_manufacturer_id:
            self.soft_left_manufacturer_id = self.soft_manufacturer_id
            # self.soft_left_style = self.select_soft_style
            self.soft_left_color = self.select_soft_color
            self.soft_left_base_curve = self.select_soft_base_curve
            self.soft_left_diameter = self.select_soft_diameter
            self.soft_left_sphere = self.select_soft_sphere
            self.soft_left_cylinder = self.select_soft_cylinder
            self.soft_left_axis = self.select_soft_axis
            self.soft_left_add_power = self.select_soft_add_power
            self.soft_left_multifocal = self.select_soft_multifocal
            self.soft_left_va = self.soft_va

    def copy_to_left_lens(self):
        if self.gls_sphere:
            self.gls_left_lens_sphere = self.gls_sphere
            self.gls_left_lens_cylinder = self.gls_cylinder
            self.gls_left_lens_axis = self.gls_axis
            self.gls_left_lens_add = self.gls_add
            self.gls_left_lens_h_prism = self.gls_h_prism
            self.gls_left_h_base = self.gls_h_base
            self.gls_left_lens_v_prism = self.gls_v_prism
            self.gls_left_v_base = self.gls_v_base
            self.gls_left_pd = self.gls_pd
            self.gls_left_va = self.gls_va
            self.gls_left_near = self.gls_near
            self.gls_left_balance = self.gls_balance


    def action_convert(self):
        sphere = ''
        sphere_od = ''
        if self.gls_sphere and self.gls_cylinder:
            sphere = str("{:.2f}".format((float(self.gls_sphere)) + (float(self.gls_cylinder))))
            if (float(sphere)) < -30 or (float(sphere)) > 30:
                raise ValidationError('The addition of Sphere and Cylinder between -30.0 and 30.00')
            if sphere >= '0.0':
                self.gls_sphere = sphere
            else:
                self.gls_sphere = sphere
        if float(self.gls_cylinder):
            if float(self.gls_cylinder) > 0.0:
                gls_cylinder = ("{:.2f}".format(float(self.gls_cylinder)))
                self.gls_cylinder = '-' + gls_cylinder
            else:
                gls_cylinder = ("{:.2f}".format(- + float(self.gls_cylinder)))
                self.gls_cylinder = gls_cylinder

        if int(self.gls_axis) <= 90:
            self.gls_axis = str(90 + int(self.gls_axis))
        else:
            self.gls_axis = str(int(self.gls_axis) - 90)
        if self.gls_left_lens_sphere and self.gls_left_lens_cylinder:
            sphere_od = str("{:.2f}".format((float(self.gls_left_lens_sphere)) + (float(self.gls_left_lens_cylinder))))
            if (float(sphere_od)) < -30 or (float(sphere_od)) > 30:
                raise ValidationError('The addition of Sphere and Cylinder between -30.0 and 30.00')
            if sphere_od >= '0.0':
                self.gls_left_lens_sphere = sphere_od
            else:
                self.gls_left_lens_sphere = sphere_od
        if float(self.gls_left_lens_cylinder):
            if float(self.gls_left_lens_cylinder) > 0.0:
                gls_left_lens_cylinder = ("{:.2f}".format(float(self.gls_left_lens_cylinder)))
                self.gls_left_lens_cylinder = '-' + gls_left_lens_cylinder

            else:
                gls_left_lens_cylinder = ("{:.2f}".format(- + float(self.gls_left_lens_cylinder)))
                self.gls_left_lens_cylinder = gls_left_lens_cylinder
        if int(self.gls_left_lens_axis) <= 90:
            self.gls_left_lens_axis = str(90 + int(self.gls_left_lens_axis))
        else:
            self.gls_left_lens_axis = str(int(self.gls_left_lens_axis) - 90)

    @api.onchange('rx', 'rx_usage_id')
    def _onchange_rx_type_char(self):
        name = ''
        if self.rx:
            rx = dict(self.fields_get(["rx"], ['selection'])['rx']["selection"]).get(self.rx)
            name += rx or ''
        if self.rx_usage_id and self.rx_usage_id.name:
            name += ' (' + self.rx_usage_id.name + ') ' or ''
        self.rx_type_char = name

    @api.onchange('gls_h_prism', 'gls_left_lens_h_prism')
    def _onchange_gls_h_prism(self):
        if self.gls_h_prism and self.gls_h_prism.isdigit():
            self.gls_h_prism = str(float(self.gls_h_prism))
        if self.gls_left_lens_h_prism and self.gls_left_lens_h_prism.isdigit():
            self.gls_left_lens_h_prism = str(float(self.gls_left_lens_h_prism))

    @api.onchange('gls_v_prism', 'gls_left_lens_v_prism')
    def _onchange_gls_v_prism(self):
        if self.gls_v_prism and self.gls_v_prism.isdigit():
            self.gls_v_prism = str(float(self.gls_v_prism))
        if self.gls_left_lens_v_prism and self.gls_left_lens_v_prism.isdigit():
            self.gls_left_lens_v_prism = str(float(self.gls_left_lens_v_prism))

    @api.onchange('gls_pd', 'gls_left_pd')
    def _onchange_gls_pd(self):
        if self.gls_pd and self.gls_pd.isdigit():
            self.gls_pd = str(float(self.gls_pd))
        if self.gls_left_pd and self.gls_left_pd.isdigit():
            self.gls_left_pd = str(float(self.gls_left_pd))

    #    @api.onchange('base_curve')
    #    def _onchange_format_hard_lens(self):
    #        if self.base_curve and self.base_curve.startswith('+'):
    #                base_curve = self.base_curve.split('.')
    #                if len(base_curve) == 2:
    #                    if base_curve[1] and len(base_curve[1]) == 1:
    #                        self.base_curve = str(self.base_curve + '0')
    #        if self.base_curve and self.base_curve.startswith('-'):
    #                base_curve = self.base_curve.split('.')
    #                if len(base_curve) == 2:
    #                    if base_curve[1] and len(base_curve[1]) == 1:
    #                        self.base_curve = str(self.base_curve + '0')
    #        if self.base_curve and self.base_curve.isdigit():
    #            bc = len(self.base_curve)
    #            if bc == 1:
    #                self.base_curve = str('00' + self.base_curve)
    #            if bc == 2:
    #                self.base_curve = str('0' + self.base_curve)
    #        if self.base_curve:
    #            base_curve = self.base_curve.split('.')
    #            if len(base_curve) == 2:
    #                if base_curve[1] and len(base_curve[1]) == 1:
    #                    self.base_curve = str(self.base_curve + '0')
    #
    #    @api.onchange('diameter')
    #    def _onchange_format_hard_diameter_lens(self):
    #        if self.diameter and self.diameter.startswith('+'):
    #                diameter = self.diameter.split('.')
    #                if len(diameter) == 2:
    #                    if diameter[1] and len(diameter[1]) == 1:
    #                        self.diameter = str(self.diameter + '0')
    #        if self.diameter and self.diameter.startswith('-'):
    #                diameter = self.diameter.split('.')
    #                if len(diameter) == 2:
    #                    if diameter[1] and len(diameter[1]) == 1:
    #                        self.diameter = str(self.diameter + '0')
    #        if self.diameter and self.diameter.isdigit():
    #            dm = len(self.diameter)
    #            if dm == 1:
    #                self.diameter = str('00' + self.diameter)
    #            if dm == 2:
    #                self.diameter = str('0' + self.diameter)
    #        if self.diameter:
    #            diameter = self.diameter.split('.')
    #            if len(diameter) == 2:
    #                if diameter[1] and len(diameter[1]) == 1:
    #                    self.diameter = str(self.diameter + '0')

    #    @api.onchange('sphere')
    #    def _onchange_format_hard_sphere_lens(self):
    #        if self.sphere and self.sphere.startswith('+'):
    #            if self.sphere and len(self.sphere) == 2:
    #                self.sphere = str(self.sphere + '.00')
    #            if self.sphere and len(self.sphere) == 3:
    #                self.sphere = str(self.sphere + '.00')
    #            sphere = self.sphere.split('.')
    #            if len(sphere) == 2:
    #                if sphere[1] and len(sphere[1]) == 1:
    #                    self.sphere = str(self.sphere + '0')
    #        if self.sphere and self.sphere.startswith('-'):
    #            if self.sphere and len(self.sphere) == 2:
    #                    self.sphere = str(self.sphere + '.00')
    #            if self.sphere and len(self.sphere) == 3:
    #                    self.sphere = str(self.sphere + '.00')
    #            sphere = self.sphere.split('.')
    #            if len(sphere) == 2:
    #                if sphere[1] and len(sphere[1]) == 1:
    #                    self.sphere = str(self.sphere + '0')
    #        if self.sphere and self.sphere.isdigit():
    #            bc = len(self.sphere)
    #            if bc == 1:
    #                self.sphere = str('00' + self.sphere )
    #            if bc == 2:
    #                self.sphere = str('0' + self.sphere )
    #        if self.sphere:
    #            sphere = self.sphere.split('.')
    #            if len(sphere) == 2:
    #                if sphere[1] and len(sphere[1]) == 1:
    #                    self.sphere = str(self.sphere + '0')

    # @api.onchange('sphere',)
    # def _onchange_format_hard_sphere_lens(self):
    #     if self.sphere and self.sphere.startswith('+'):
    #             sphere = self.sphere.split('.')
    #             if len(sphere) == 2:
    #                 if sphere[1] and len(sphere[1]) == 1:
    #                     self.sphere = str(self.sphere + '0')
    #     if self.sphere and self.sphere.startswith('-'):
    #             sphere = self.sphere.split('.')
    #             if len(sphere) == 2:
    #                 if sphere[1] and len(sphere[1]) == 1:
    #                     self.sphere = str(self.sphere + '0')
    #     if self.sphere and self.sphere.isdigit():
    #         sp = len(self.sphere)
    #         if sp == 1:
    #             self.sphere = str('00' + self.sphere)
    #         if sp == 2:
    #             self.sphere = str('0' + self.sphere)
    #     if self.sphere:
    #         sphere = self.sphere.split('.')
    #         if len(sphere) == 2:
    #             if sphere[1] and len(sphere[1]) == 1:
    #                 self.sphere = str(self.sphere + '0')

    #    @api.onchange('cylinder')
    #    def _onchange_format_hard_cylinder_lens(self):
    #        if self.cylinder and self.cylinder.startswith('+'):
    #                cylinder = self.cylinder.split('.')
    #                if len(cylinder) == 2:
    #                    if cylinder[1] and len(cylinder[1]) == 1:
    #                        self.cylinder = str(self.cylinder + '0')
    #        if self.cylinder and self.cylinder.startswith('-'):
    #                cylinder = self.cylinder.split('.')
    #                if len(cylinder) == 2:
    #                    if cylinder[1] and len(cylinder[1]) == 1:
    #                        self.cylinder = str(self.cylinder + '0')
    #        if self.cylinder and self.cylinder.isdigit():
    #            cy = len(self.cylinder)
    #            if cy == 1:
    #                self.cylinder = str('00' + self.cylinder)
    #            if cy == 2:
    #                self.cylinder = str('0' + self.cylinder)
    #        if self.cylinder:
    #            cylinder = self.cylinder.split('.')
    #            if len(cylinder) == 2:
    #                if cylinder[1] and len(cylinder[1]) == 1:
    #                    self.cylinder = str(self.cylinder + '0')
    #
    #    @api.onchange('axis')
    #    def _onchange_format_hard_axis_lens(self):
    #        if self.axis and self.axis.startswith('+'):
    #                axis = self.axis.split('.')
    #                if len(axis) == 2:
    #                    if axis[1] and len(axis[1]) == 1:
    #                        self.axis = str(self.axis + '0')
    #        if self.axis and self.axis.startswith('-'):
    #                axis = self.axis.split('.')
    #                if len(axis) == 2:
    #                    if axis[1] and len(axis[1]) == 1:
    #                        self.axis = str(self.axis + '0')
    #        if self.axis and self.axis.isdigit():
    #            ax = len(self.axis)
    #            if ax == 1:
    #                self.axis = str('00' + self.axis)
    #            if ax == 2:
    #                self.axis = str('0' + self.axis)
    #        if self.axis:
    #            axis = self.axis.split('.')
    #            if len(axis) == 2:
    #                if axis[1] and len(axis[1]) == 1:
    #                    self.axis = str(self.axis + '0')

    #    @api.onchange('add')
    #    def _onchange_format_hard_add_lens(self):
    #        if  self.add and self.add.startswith('+'):
    #                add = self.add.split('.')
    #                if len(add) == 2:
    #                    if add[1] and len(add[1]) == 1:
    #                        self.add = str(self.add + '0')
    #        if  self.add and self.add.startswith('-'):
    #                add = self.add.split('.')
    #                if len(add) == 2:
    #                    if add[1] and len(add[1]) == 1:
    #                        self.add = str(self.add + '0')
    #        if self.add and self.add.isdigit():
    #            add = len(self.add)
    #            if add == 1:
    #                self.add = str('00' + self.add)
    #            if add == 2:
    #                self.add = str('0' + self.add)
    #        if self.add:
    #            add = self.add.split('.')
    #            if len(add) == 2:
    #                if add[1] and len(add[1]) == 1:
    #                    self.add = str(self.add + '0')

    #    @api.onchange('seg_height')
    #    def _onchange_format_hard_seg_height_lens(self):
    #        if self.seg_height and self.seg_height.startswith('+'):
    #                seg_height = self.seg_height.split('.')
    #                if len(seg_height) == 2:
    #                    if seg_height[1] and len(seg_height[1]) == 1:
    #                        self.seg_height = str(self.seg_height + '0')
    #        if self.seg_height and self.seg_height.startswith('-'):
    #                seg_height = self.seg_height.split('.')
    #                if len(seg_height) == 2:
    #                    if seg_height[1] and len(seg_height[1]) == 1:
    #                        self.seg_height = str(self.seg_height + '0')
    #        if self.seg_height and self.seg_height.isdigit():
    #            seg_height = len(self.seg_height)
    #            if seg_height == 1:
    #                self.seg_height = str('00' + self.seg_height)
    #            if seg_height == 2:
    #                self.seg_height = str('0' + self.seg_height)
    #        if self.seg_height:
    #            seg_height = self.seg_height.split('.')
    #            if len(seg_height) == 2:
    #                if seg_height[1] and len(seg_height[1]) == 1:
    #                    self.seg_height = str(self.seg_height + '0')

    #    @api.onchange('pc_radius')
    #    def _onchange_format_hardpc_radius_lenses(self):
    #        if self.pc_radius and self.pc_radius.startswith('+'):
    #                pc_radius = self.pc_radius.split('.')
    #                if len(pc_radius) == 2:
    #                    if pc_radius[1] and len(pc_radius[1]) == 1:
    #                        self.pc_radius = str(self.pc_radius + '0')
    #        if self.pc_radius and self.pc_radius.startswith('-'):
    #                pc_radius = self.pc_radius.split('.')
    #                if len(pc_radius) == 2:
    #                    if pc_radius[1] and len(pc_radius[1]) == 1:
    #                        self.pc_radius = str(self.pc_radius + '0')
    #        if self.pc_radius and self.pc_radius.isdigit():
    #            pc_radius = len(self.pc_radius)
    #            if pc_radius == 1:
    #                self.pc_radius = str('00' + self.pc_radius)
    #            if pc_radius == 2:
    #                self.pc_radius = str('0' + self.pc_radius)
    #        if self.pc_radius:
    #            pc_radius = self.pc_radius.split('.')
    #            if len(pc_radius) == 2:
    #                if pc_radius[1] and len(pc_radius[1]) == 1:
    #                    self.pc_radius = str(self.pc_radius + '0')

    #    @api.onchange('pc_width')
    #    def _onchange_format_hard_pc_width_lens(self):
    #        if self.pc_width and self.pc_width.startswith('+'):
    #                pc_width = self.pc_width.split('.')
    #                if len(pc_width) == 2:
    #                    if pc_width[1] and len(pc_width[1]) == 1:
    #                        self.pc_width = str(self.pc_width + '0')
    #        if self.pc_width and self.pc_width.startswith('-'):
    #                pc_width = self.pc_width.split('.')
    #                if len(pc_width) == 2:
    #                    if pc_width[1] and len(pc_width[1]) == 1:
    #                        self.pc_width = str(self.pc_width + '0')
    #        if self.pc_width and self.pc_width.isdigit():
    #            pc_width = len(self.pc_width)
    #            if pc_width == 1:
    #                self.pc_width = str('00' + self.pc_width)
    #            if pc_width == 2:
    #                self.pc_width = str('0' + self.pc_width)
    #        if self.pc_width:
    #            pc_width = self.pc_width.split('.')
    #            if len(pc_width) == 2:
    #                if pc_width[1] and len(pc_width[1]) == 1:
    #                    self.pc_width = str(self.pc_width + '0')

    #    @api.onchange('ct')
    #    def _onchange_format_hard_ct_lens(self):
    #        if self.ct and self.ct.startswith('+'):
    #                ct = self.ct.split('.')
    #                if len(ct) == 2:
    #                    if ct[1] and len(ct[1]) == 1:
    #                        self.ct = str(self.ct + '0')
    #        if self.ct and self.ct.startswith('-'):
    #                ct = self.ct.split('.')
    #                if len(ct) == 2:
    #                    if ct[1] and len(ct[1]) == 1:
    #                        self.ct = str(self.ct + '0')
    #        if self.ct and self.ct.isdigit():
    #            ct = len(self.ct)
    #            if ct == 1:
    #                self.ct = str('00' + self.ct)
    #            if ct == 2:
    #                self.ct = str('0' + self.ct)
    #        if self.ct:
    #            ct = self.ct.split('.')
    #            if len(ct) == 2:
    #                if ct[1] and len(ct[1]) == 1:
    #                    self.ct = str(self.ct + '0')

    #    @api.onchange('oz')
    #    def _onchange_format_hard_oz_lens(self):
    #        if self.oz and self.oz.startswith('+'):
    #                oz = self.oz.split('.')
    #                if len(oz) == 2:
    #                    if oz[1] and len(oz[1]) == 1:
    #                        self.oz = str(self.oz + '0')
    #        if self.oz and self.oz.startswith('-'):
    #                oz = self.oz.split('.')
    #                if len(oz) == 2:
    #                    if oz[1] and len(oz[1]) == 1:
    #                        self.oz = str(self.oz + '0')
    #        if self.oz and self.oz.isdigit():
    #            oz = len(self.oz)
    #            if oz == 1:
    #                self.oz = str('00' + self.oz)
    #            if oz == 2:
    #                self.oz = str('0' + self.oz)
    #        if self.oz:
    #            oz = self.oz.split('.')
    #            if len(oz) == 2:
    #                if oz[1] and len(oz[1]) == 1:
    #                    self.oz = str(self.oz + '0')

    #    @api.onchange('base_curve_2')
    #    def _onchange_format_hard_base_curve_2_lens(self):
    #        if self.base_curve_2 and self.base_curve_2.startswith('+'):
    #                base_curve_2 = self.base_curve_2.split('.')
    #                if len(base_curve_2) == 2:
    #                    if base_curve_2[1] and len(base_curve_2[1]) == 1:
    #                        self.base_curve_2 = str(self.base_curve_2 + '0')
    #        if self.base_curve_2 and self.base_curve_2.startswith('-'):
    #                base_curve_2 = self.base_curve_2.split('.')
    #                if len(base_curve_2) == 2:
    #                    if base_curve_2[1] and len(base_curve_2[1]) == 1:
    #                        self.base_curve_2 = str(self.base_curve_2 + '0')
    #        if self.base_curve_2 and self.base_curve_2.isdigit():
    #            base_curve_2 = len(self.base_curve_2)
    #            if base_curve_2 == 1:
    #                self.base_curve_2 = str('00' + self.base_curve_2)
    #            if base_curve_2 == 2:
    #                self.base_curve_2 = str('0' + self.base_curve_2)
    #        if self.base_curve_2:
    #            base_curve_2 = self.base_curve_2.split('.')
    #            if len(base_curve_2) == 2:
    #                if base_curve_2[1] and len(base_curve_2[1]) == 1:
    #                    self.base_curve_2 = str(self.base_curve_2 + '0')

    #    @api.onchange('sphere_2')
    #    def _onchange_format_hard_sphere_2_lens(self):
    #        if self.sphere_2 and self.sphere_2.startswith('+'):
    #                sphere_2 = self.sphere_2.split('.')
    #                if len(sphere_2) == 2:
    #                    if sphere_2[1] and len(sphere_2[1]) == 1:
    #                        self.sphere_2 = str(self.sphere_2 + '0')
    #        if self.sphere_2 and self.sphere_2.startswith('-'):
    #                sphere_2 = self.sphere_2.split('.')
    #                if len(sphere_2) == 2:
    #                    if sphere_2[1] and len(sphere_2[1]) == 1:
    #                        self.sphere_2 = str(self.sphere_2 + '0')
    #        if self.sphere_2 and self.sphere_2.isdigit():
    #            sphere_2 = len(self.sphere_2)
    #            if sphere_2 == 1:
    #                self.sphere_2 = str('00' + self.sphere_2)
    #            if sphere_2 == 2:
    #                self.sphere_2 = str('0' + self.sphere_2)
    #        if self.sphere_2:
    #            sphere_2 = self.sphere_2.split('.')
    #            if len(sphere_2) == 2:
    #                if sphere_2[1] and len(sphere_2[1]) == 1:
    #                    self.sphere_2 = str(self.sphere_2 + '0')

    #    @api.onchange('cylinder_2')
    #    def _onchange_format_hard_cylinder_2_lens(self):
    #        if self.cylinder_2 and self.cylinder_2.startswith('+'):
    #                cylinder_2 = self.cylinder_2.split('.')
    #                if len(cylinder_2) == 2:
    #                    if cylinder_2[1] and len(cylinder_2[1]) == 1:
    #                        self.cylinder_2 = str(self.cylinder_2 + '0')
    #        if self.cylinder_2 and self.cylinder_2.startswith('-'):
    #                cylinder_2 = self.cylinder_2.split('.')
    #                if len(cylinder_2) == 2:
    #                    if cylinder_2[1] and len(cylinder_2[1]) == 1:
    #                        self.cylinder_2 = str(self.cylinder_2 + '0')
    #        if self.cylinder_2 and self.cylinder_2.isdigit():
    #            cylinder_2 = len(self.cylinder_2)
    #            if cylinder_2 == 1:
    #                self.cylinder_2 = str('00' + self.cylinder_2)
    #            if cylinder_2 == 2:
    #                self.cylinder_2 = str('0' + self.cylinder_2)
    #        if self.cylinder_2:
    #            cylinder_2 = self.cylinder_2.split('.')
    #            if len(cylinder_2) == 2:
    #                if cylinder_2[1] and len(cylinder_2[1]) == 1:
    #                    self.cylinder_2 = str(self.cylinder_2 + '0')
    #
    #    @api.onchange('axis_2')
    #    def _onchange_format_hard_axis_2_lens(self):
    #        if self.axis_2 and self.axis_2.startswith('+'):
    #                axis_2 = self.axis_2.split('.')
    #                if len(axis_2) == 2:
    #                    if axis_2[1] and len(axis_2[1]) == 1:
    #                        self.axis_2 = str(self.axis_2 + '0')
    #        if self.axis_2 and self.axis_2.startswith('-'):
    #                axis_2 = self.axis_2.split('.')
    #                if len(axis_2) == 2:
    #                    if axis_2[1] and len(axis_2[1]) == 1:
    #                        self.axis_2 = str(self.axis_2 + '0')
    #        if self.axis_2 and self.axis_2.isdigit():
    #            axis_2 = len(self.axis_2)
    #            if axis_2 == 1:
    #                self.axis_2 = str('00' + self.axis_2)
    #            if axis_2 == 2:
    #                self.axis_2 = str('0' + self.axis_2)
    #        if self.axis_2:
    #            axis_2 = self.axis_2.split('.')
    #            if len(axis_2) == 2:
    #                if axis_2[1] and len(axis_2[1]) == 1:
    #                    self.axis_2 = str(self.axis_2 + '0')

    #    @api.onchange('add_diam_2')
    #    def _onchange_format_hard_add_diam_2_lens(self):
    #        if self.add_diam_2 and self.add_diam_2.startswith('+'):
    #                add_diam_2 = self.add_diam_2.split('.')
    #                if len(add_diam_2) == 2:
    #                    if add_diam_2[1] and len(add_diam_2[1]) == 1:
    #                        self.add_diam_2 = str(self.add_diam_2 + '0')
    #        if self.add_diam_2 and self.add_diam_2.startswith('-'):
    #                add_diam_2 = self.add_diam_2.split('.')
    #                if len(add_diam_2) == 2:
    #                    if add_diam_2[1] and len(add_diam_2[1]) == 1:
    #                        self.add_diam_2 = str(self.add_diam_2 + '0')
    #        if self.add_diam_2 and self.add_diam_2.isdigit():
    #            add_diam_2 = len(self.add_diam_2)
    #            if add_diam_2 == 1:
    #                self.add_diam_2 = str('00' + self.add_diam_2)
    #            if add_diam_2 == 2:
    #                self.add_diam_2 = str('0' + self.add_diam_2)
    #        if self.add_diam_2:
    #            add_diam_2 = self.add_diam_2.split('.')
    #            if len(add_diam_2) == 2:
    #                if add_diam_2[1] and len(add_diam_2[1]) == 1:
    #                    self.add_diam_2 = str(self.add_diam_2 + '0')

    """od"""

    # @api.onchange('left_base_curve')
    # def _onchange_format_left_base_curve(self):
    #     if self.left_base_curve and self.left_base_curve and self.left_base_curve.startswith('+'):
    #         left_base_curve = self.left_base_curve.split('.')
    #         if len(left_base_curve) == 2:
    #             if left_base_curve[1] and len(left_base_curve[1]) == 1:
    #                 self.left_base_curve = str(self.left_base_curve + '0')
    #     if self.left_base_curve and self.left_base_curve and self.left_base_curve.startswith('-'):
    #         left_base_curve = self.left_base_curve.split('.')
    #         if len(left_base_curve) == 2:
    #             if left_base_curve[1] and len(left_base_curve[1]) == 1:
    #                 self.left_base_curve = str(self.left_base_curve + '0')
    #     if self.left_base_curve and self.left_base_curve.isdigit():
    #         left_base_curve = len(self.left_base_curve)
    #         if left_base_curve == 1:
    #             self.left_base_curve = str('00' + self.left_base_curve)
    #         if left_base_curve == 2:
    #             self.left_base_curve = str('0' + self.left_base_curve)
    #     if self.left_base_curve:
    #         left_base_curve = self.left_base_curve.split('.')
    #         if len(left_base_curve) == 2:
    #             if left_base_curve[1] and len(left_base_curve[1]) == 1:
    #                 self.left_base_curve = str(self.left_base_curve + '0')

    # @api.onchange('left_diameter')
    # def _onchange_format_left_diameter(self):
    #     if self.left_diameter and self.left_diameter and self.left_diameter.startswith('+'):
    #         left_diameter = self.left_diameter.split('.')
    #         if len(left_diameter) == 2:
    #             if left_diameter[1] and len(left_diameter[1]) == 1:
    #                 self.left_diameter = str(self.left_diameter + '0')
    #     if self.left_diameter and self.left_diameter and self.left_diameter.startswith('-'):
    #         left_diameter = self.left_diameter.split('.')
    #         if len(left_diameter) == 2:
    #             if left_diameter[1] and len(left_diameter[1]) == 1:
    #                 self.left_diameter = str(self.left_diameter + '0')
    #     if self.left_diameter and self.left_diameter.isdigit():
    #         left_diameter = len(self.left_diameter)
    #         if left_diameter == 1:
    #             self.left_diameter = str('00' + self.left_diameter)
    #         if left_diameter == 2:
    #             self.left_diameter = str('0' + self.left_diameter)
    #     if self.left_diameter:
    #         left_diameter = self.left_diameter.split('.')
    #         if len(left_diameter) == 2:
    #             if left_diameter[1] and len(left_diameter[1]) == 1:
    #                 self.left_diameter = str(self.left_diameter + '0')

    # @api.onchange('left_sphere', )
    # def _onchange_format_left_sphere(self):
    #     if self.left_sphere and self.left_sphere.startswith('+'):
    #         left_sphere = self.left_sphere.split('.')
    #         if len(left_sphere) == 2:
    #             if left_sphere[1] and len(left_sphere[1]) == 1:
    #                 self.left_sphere = str(self.left_sphere + '0')
    #     if self.left_sphere and self.left_sphere.startswith('-'):
    #         left_sphere = self.left_sphere.split('.')
    #         if len(left_sphere) == 2:
    #             if left_sphere[1] and len(left_sphere[1]) == 1:
    #                 self.left_sphere = str(self.left_sphere + '0')
    #     if self.left_sphere and self.left_sphere.isdigit():
    #         left_sphere = len(self.left_sphere)
    #         if left_sphere == 1:
    #             self.left_sphere = str('00' + self.left_sphere)
    #         if left_sphere == 2:
    #             self.left_sphere = str('0' + self.left_sphere)
    #     if self.left_sphere:
    #         left_sphere = self.left_sphere.split('.')
    #         if len(left_sphere) == 2:
    #             if left_sphere[1] and len(left_sphere[1]) == 1:
    #                 self.left_sphere = str(self.left_sphere + '0')

    # @api.onchange('left_cylinder')
    # def _onchange_format_left_cylinder(self):
    #     if self.left_cylinder and self.left_cylinder.startswith('+'):
    #         left_cylinder = self.left_cylinder.split('.')
    #         if len(left_cylinder) == 2:
    #             if left_cylinder[1] and len(left_cylinder[1]) == 1:
    #                 self.left_cylinder = str(self.left_cylinder + '0')
    #     if self.left_cylinder and self.left_cylinder.startswith('-'):
    #         left_cylinder = self.left_cylinder.split('.')
    #         if len(left_cylinder) == 2:
    #             if left_cylinder[1] and len(left_cylinder[1]) == 1:
    #                 self.left_cylinder = str(self.left_cylinder + '0')
    #     if self.left_cylinder and self.left_cylinder.isdigit():
    #         left_cylinder = len(self.left_cylinder)
    #         if left_cylinder == 1:
    #             self.left_cylinder = str('00' + self.left_cylinder)
    #         if left_cylinder == 2:
    #             self.left_cylinder = str('0' + self.left_cylinder)
    #     if self.left_cylinder:
    #         left_cylinder = self.left_cylinder.split('.')
    #         if len(left_cylinder) == 2:
    #             if left_cylinder[1] and len(left_cylinder[1]) == 1:
    #                 self.left_cylinder = str(self.left_cylinder + '0')

    # @api.onchange('left_axis')
    # def _onchange_format_left_axis(self):
    #     if self.left_axis and self.left_axis.startswith('+'):
    #         left_axis = self.left_axis.split('.')
    #         if len(left_axis) == 2:
    #             if left_axis[1] and len(left_axis[1]) == 1:
    #                 self.left_axis = str(self.left_axis + '0')
    #     if self.left_axis and self.left_axis.startswith('-'):
    #         left_axis = self.left_axis.split('.')
    #         if len(left_axis) == 2:
    #             if left_axis[1] and len(left_axis[1]) == 1:
    #                 self.left_axis = str(self.left_axis + '0')
    #     if self.left_axis and self.left_axis.isdigit():
    #         left_axis = len(self.left_axis)
    #         if left_axis == 1:
    #             self.left_axis = str('00' + self.left_axis)
    #         if left_axis == 2:
    #             self.left_axis = str('0' + self.left_axis)
    #     if self.left_axis:
    #         left_axis = self.left_axis.split('.')
    #         if len(left_axis) == 2:
    #             if left_axis[1] and len(left_axis[1]) == 1:
    #                 self.left_axis = str(self.left_axis + '0')

    # @api.onchange('left_add')
    # def _onchange_format_left_add(self):
    #     if self.left_add and self.left_add.startswith('+'):
    #         left_add = self.left_add.split('.')
    #         if len(left_add) == 2:
    #             if left_add[1] and len(left_add[1]) == 1:
    #                 self.left_add = str(self.left_add + '0')
    #     if self.left_add and self.left_add.startswith('-'):
    #         left_add = self.left_add.split('.')
    #         if len(left_add) == 2:
    #             if left_add[1] and len(left_add[1]) == 1:
    #                 self.left_add = str(self.left_add + '0')
    #     if self.left_add and self.left_add.isdigit():
    #         left_add = len(self.left_add)
    #         if left_add == 1:
    #             self.left_add = str('00' + self.left_add)
    #         if left_add == 2:
    #             self.left_add = str('0' + self.left_add)
    #     if self.left_add:
    #         left_add = self.left_add.split('.')
    #         if len(left_add) == 2:
    #             if left_add[1] and len(left_add[1]) == 1:
    #                 self.left_add = str(self.left_add + '0')

    # @api.onchange('left_seg_height')
    # def _onchange_format_left_seg_height(self):
    #     if self.left_seg_height and self.left_seg_height.startswith('+'):
    #         left_seg_height = self.left_seg_height.split('.')
    #         if len(left_seg_height) == 2:
    #             if left_seg_height[1] and len(left_seg_height[1]) == 1:
    #                 self.left_seg_height = str(self.left_seg_height + '0')
    #     if self.left_seg_height and self.left_seg_height.startswith('-'):
    #         left_seg_height = self.left_seg_height.split('.')
    #         if len(left_seg_height) == 2:
    #             if left_seg_height[1] and len(left_seg_height[1]) == 1:
    #                 self.left_seg_height = str(self.left_seg_height + '0')
    #     if self.left_seg_height and self.left_seg_height.isdigit():
    #         left_seg_height = len(self.left_seg_height)
    #         if left_seg_height == 1:
    #             self.left_seg_height = str('00' + self.left_seg_height)
    #         if left_seg_height == 2:
    #             self.left_seg_height = str('0' + self.left_seg_height)
    #     if self.left_seg_height:
    #         left_seg_height = self.left_seg_height.split('.')
    #         if len(left_seg_height) == 2:
    #             if left_seg_height[1] and len(left_seg_height[1]) == 1:
    #                 self.left_seg_height = str(self.left_seg_height + '0')

    # @api.onchange('left_pc_radius')
    # def _onchange_format_left_pc_radius(self):
    #     if self.left_pc_radius and self.left_pc_radius.startswith('+'):
    #         left_pc_radius = self.left_pc_radius.split('.')
    #         if len(left_pc_radius) == 2:
    #             if left_pc_radius[1] and len(left_pc_radius[1]) == 1:
    #                 self.left_pc_radius = str(self.left_pc_radius + '0')
    #     if self.left_pc_radius and self.left_pc_radius.startswith('-'):
    #         left_pc_radius = self.left_pc_radius.split('.')
    #         if len(left_pc_radius) == 2:
    #             if left_pc_radius[1] and len(left_pc_radius[1]) == 1:
    #                 self.left_pc_radius = str(self.left_pc_radius + '0')
    #     if self.left_pc_radius and self.left_pc_radius.isdigit():
    #         left_pc_radius = len(self.left_pc_radius)
    #         if left_pc_radius == 1:
    #             self.left_pc_radius = str('00' + self.left_pc_radius)
    #         if left_pc_radius == 2:
    #             self.left_pc_radius = str('0' + self.left_pc_radius)
    #     if self.left_pc_radius:
    #         left_pc_radius = self.left_pc_radius.split('.')
    #         if len(left_pc_radius) == 2:
    #             if left_pc_radius[1] and len(left_pc_radius[1]) == 1:
    #                 self.left_pc_radius = str(self.left_pc_radius + '0')

    # @api.onchange('left_pc_width')
    # def _onchange_format_left_pc_width(self):
    #     if self.left_pc_width and self.left_pc_width.startswith('+'):
    #         left_pc_width = self.left_pc_width.split('.')
    #         if len(left_pc_width) == 2:
    #             if left_pc_width[1] and len(left_pc_width[1]) == 1:
    #                 self.left_pc_width = str(self.left_pc_width + '0')
    #     if self.left_pc_width and self.left_pc_width.startswith('-'):
    #         left_pc_width = self.left_pc_width.split('.')
    #         if len(left_pc_width) == 2:
    #             if left_pc_width[1] and len(left_pc_width[1]) == 1:
    #                 self.left_pc_width = str(self.left_pc_width + '0')
    #     if self.left_pc_width and self.left_pc_width.isdigit():
    #         left_pc_width = len(self.left_pc_width)
    #         if left_pc_width == 1:
    #             self.left_pc_width = str('00' + self.left_pc_width)
    #         if left_pc_width == 2:
    #             self.left_pc_width = str('0' + self.left_pc_width)
    #     if self.left_pc_width:
    #         left_pc_width = self.left_pc_width.split('.')
    #         if len(left_pc_width) == 2:
    #             if left_pc_width[1] and len(left_pc_width[1]) == 1:
    #                 self.left_pc_width = str(self.left_pc_width + '0')

    # @api.onchange('left_ct')
    # def _onchange_formatleft_ct(self):
    #     if self.left_ct and self.left_ct.startswith('+'):
    #         left_ct = self.left_ct.split('.')
    #         if len(left_ct) == 2:
    #             if left_ct[1] and len(left_ct[1]) == 1:
    #                 self.left_ct = str(self.left_ct + '0')
    #     if self.left_ct and self.left_ct.startswith('-'):
    #         left_ct = self.left_ct.split('.')
    #         if len(left_ct) == 2:
    #             if left_ct[1] and len(left_ct[1]) == 1:
    #                 self.left_ct = str(self.left_ct + '0')
    #     if self.left_ct and self.left_ct.isdigit():
    #         left_ct = len(self.left_ct)
    #         if left_ct == 1:
    #             self.left_ct = str('00' + self.left_ct)
    #         if left_ct == 2:
    #             self.left_ct = str('0' + self.left_ct)
    #     if self.left_ct:
    #         left_ct = self.left_ct.split('.')
    #         if len(left_ct) == 2:
    #             if left_ct[1] and len(left_ct[1]) == 1:
    #                 self.left_ct = str(self.left_ct + '0')

    # @api.onchange('left_oz')
    # def _onchange_format_left_oz(self):
    #     if self.left_oz and self.left_oz.startswith('+'):
    #         left_oz = self.left_oz.split('.')
    #         if len(left_oz) == 2:
    #             if left_oz[1] and len(left_oz[1]) == 1:
    #                 self.left_oz = str(self.left_oz + '0')
    #     if self.left_oz and self.left_oz.startswith('-'):
    #         left_oz = self.left_oz.split('.')
    #         if len(left_oz) == 2:
    #             if left_oz[1] and len(left_oz[1]) == 1:
    #                 self.left_oz = str(self.left_oz + '0')
    #     if self.left_oz and self.left_oz.isdigit():
    #         left_oz = len(self.left_oz)
    #         if left_oz == 1:
    #             self.left_oz = str('00' + self.left_oz)
    #         if left_oz == 2:
    #             self.left_oz = str('0' + self.left_oz)
    #     if self.left_oz:
    #         left_oz = self.left_oz.split('.')
    #         if len(left_oz) == 2:
    #             if left_oz[1] and len(left_oz[1]) == 1:
    #                 self.left_oz = str(self.left_oz + '0')

    # @api.onchange('left_base_curve_2')
    # def _onchange_format_left_base_curve_2(self):
    #     if self.left_base_curve_2 and self.left_base_curve_2.startswith('+'):
    #         left_base_curve_2 = self.left_base_curve_2.split('.')
    #         if len(left_base_curve_2) == 2:
    #             if left_base_curve_2[1] and len(left_base_curve_2[1]) == 1:
    #                 self.left_base_curve_2 = str(self.left_base_curve_2 + '0')
    #     if self.left_base_curve_2 and self.left_base_curve_2.startswith('-'):
    #         left_base_curve_2 = self.left_base_curve_2.split('.')
    #         if len(left_base_curve_2) == 2:
    #             if left_base_curve_2[1] and len(left_base_curve_2[1]) == 1:
    #                 self.left_base_curve_2 = str(self.left_base_curve_2 + '0')
    #     if self.left_base_curve_2 and self.left_base_curve_2.isdigit():
    #         left_base_curve_2 = len(self.left_base_curve_2)
    #         if left_base_curve_2 == 1:
    #             self.left_base_curve_2 = str('00' + self.left_base_curve_2)
    #         if left_base_curve_2 == 2:
    #             self.left_base_curve_2 = str('0' + self.left_base_curve_2)
    #     if self.left_base_curve_2:
    #         left_base_curve_2 = self.left_base_curve_2.split('.')
    #         if len(left_base_curve_2) == 2:
    #             if left_base_curve_2[1] and len(left_base_curve_2[1]) == 1:
    #                 self.left_base_curve_2 = str(self.left_base_curve_2 + '0')

    # @api.onchange('left_sphere_2')
    # def _onchange_format_left_sphere_2(self):
    #     if self.left_sphere_2 and self.left_sphere_2.startswith('+'):
    #         left_sphere_2 = self.left_sphere_2.split('.')
    #         if len(left_sphere_2) == 2:
    #             if left_sphere_2[1] and len(left_sphere_2[1]) == 1:
    #                 self.left_sphere_2 = str(self.left_sphere_2 + '0')
    #     if self.left_sphere_2 and self.left_sphere_2.startswith('-'):
    #         left_sphere_2 = self.left_sphere_2.split('.')
    #         if len(left_sphere_2) == 2:
    #             if left_sphere_2[1] and len(left_sphere_2[1]) == 1:
    #                 self.left_sphere_2 = str(self.left_sphere_2 + '0')
    #     if self.left_sphere_2 and self.left_sphere_2.isdigit():
    #         left_sphere_2 = len(self.left_sphere_2)
    #         if left_sphere_2 == 1:
    #             self.left_sphere_2 = str('00' + self.left_sphere_2)
    #         if left_sphere_2 == 2:
    #             self.left_sphere_2 = str('0' + self.left_sphere_2)
    #     if self.left_sphere_2:
    #         left_sphere_2 = self.left_sphere_2.split('.')
    #         if len(left_sphere_2) == 2:
    #             if left_sphere_2[1] and len(left_sphere_2[1]) == 1:
    #                 self.left_sphere_2 = str(self.left_sphere_2 + '0')

    # @api.onchange('left_cylinder_2')
    # def _onchange_format_left_cylinder_2(self):
    #     if self.left_cylinder_2 and self.left_cylinder_2.startswith('+'):
    #         left_cylinder_2 = self.left_cylinder_2.split('.')
    #         if len(left_cylinder_2) == 2:
    #             if left_cylinder_2[1] and len(left_cylinder_2[1]) == 1:
    #                 self.left_cylinder_2 = str(self.left_cylinder_2 + '0')
    #     if self.left_cylinder_2 and self.left_cylinder_2.startswith('-'):
    #         left_cylinder_2 = self.left_cylinder_2.split('.')
    #         if len(left_cylinder_2) == 2:
    #             if left_cylinder_2[1] and len(left_cylinder_2[1]) == 1:
    #                 self.left_cylinder_2 = str(self.left_cylinder_2 + '0')
    #     if self.left_cylinder_2 and self.left_cylinder_2.isdigit():
    #         left_cylinder_2 = len(self.left_cylinder_2)
    #         if left_cylinder_2 == 1:
    #             self.left_cylinder_2 = str('00' + self.left_cylinder_2)
    #         if left_cylinder_2 == 2:
    #             self.left_cylinder_2 = str('0' + self.left_cylinder_2)
    #     if self.left_cylinder_2:
    #         left_cylinder_2 = self.left_cylinder_2.split('.')
    #         if len(left_cylinder_2) == 2:
    #             if left_cylinder_2[1] and len(left_cylinder_2[1]) == 1:
    #                 self.left_cylinder_2 = str(self.left_cylinder_2 + '0')

    # @api.onchange('left_axis_2')
    # def _onchange_format_left_axis_2(self):
    #     if self.left_axis_2 and self.left_axis_2.startswith('+'):
    #         left_axis_2 = self.left_axis_2.split('.')
    #         if len(left_axis_2) == 2:
    #             if left_axis_2[1] and len(left_axis_2[1]) == 1:
    #                 self.left_axis_2 = str(self.left_axis_2 + '0')
    #     if self.left_axis_2 and self.left_axis_2.startswith('-'):
    #         left_axis_2 = self.left_axis_2.split('.')
    #         if len(left_axis_2) == 2:
    #             if left_axis_2[1] and len(left_axis_2[1]) == 1:
    #                 self.left_axis_2 = str(self.left_axis_2 + '0')
    #     if self.left_axis_2 and self.left_axis_2.isdigit():
    #         left_axis_2 = len(self.left_axis_2)
    #         if left_axis_2 == 1:
    #             self.left_axis_2 = str('00' + self.left_axis_2)
    #         if left_axis_2 == 2:
    #             self.left_axis_2 = str('0' + self.left_axis_2)
    #     if self.left_axis_2:
    #         left_axis_2 = self.left_axis_2.split('.')
    #         if len(left_axis_2) == 2:
    #             if left_axis_2[1] and len(left_axis_2[1]) == 1:
    #                 self.left_axis_2 = str(self.left_axis_2 + '0')

    # @api.onchange('left_add_diam_2')
    # def _onchange_format_left_add_diam_2(self):
    #     if self.left_add_diam_2 and self.left_add_diam_2.startswith('+'):
    #         left_add_diam_2 = self.left_add_diam_2.split('.')
    #         if len(left_add_diam_2) == 2:
    #             if left_add_diam_2[1] and len(left_add_diam_2[1]) == 1:
    #                 self.left_add_diam_2 = str(self.left_add_diam_2 + '0')
    #     if self.left_add_diam_2 and self.left_add_diam_2.startswith('-'):
    #         left_add_diam_2 = self.left_add_diam_2.split('.')
    #         if len(left_add_diam_2) == 2:
    #             if left_add_diam_2[1] and len(left_add_diam_2[1]) == 1:
    #                 self.left_add_diam_2 = str(self.left_add_diam_2 + '0')
    #     if self.left_add_diam_2 and self.left_add_diam_2.isdigit():
    #         left_add_diam_2 = len(self.left_add_diam_2)
    #         if left_add_diam_2 == 1:
    #             self.left_add_diam_2 = str('00' + self.left_add_diam_2)
    #         if left_add_diam_2 == 2:
    #             self.left_add_diam_2 = str('0' + self.left_add_diam_2)
    #     if self.left_add_diam_2:
    #         left_add_diam_2 = self.left_add_diam_2.split('.')
    #         if len(left_add_diam_2) == 2:
    #             if left_add_diam_2[1] and len(left_add_diam_2[1]) == 1:
    #                 self.left_add_diam_2 = str(self.left_add_diam_2 + '0')
