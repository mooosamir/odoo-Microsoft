# -*- coding: utf-8 -*-
from odoo import api, fields, models


class MenuIconWizard(models.TransientModel):
    _name = 'ks.menu.icon'
    _description = 'Apps Icon Selection'

    ks_menu_items = fields.Many2one('ir.ui.menu', string = "App Menu", domain="[('parent_id', '=', False)]", required=True)
    ks_icon_type = fields.Selection([
        ('custom_image', 'Custom Image'),
        ('font_awesome', 'Font Awesome'),
        ('search_icons', 'Search Icons'),
        ('special_icons', 'Special Icons')
    ], string='Type', required=True, default='custom_image',
        help="Select the icon type.")
    ks_custom_image = fields.Binary('Custom Image')
    ks_font_awesome = fields.Char('Font Awesome')
    ks_search_icons = fields.Binary('Search Icons')
    ks_special_icons = fields.Binary('Special Icons')

    def save_menu_icon(self):
        if self.ks_icon_type == 'font_awesome':
            icon_data = {
                'web_icon_data': False,
                'web_icon': self.env['ks.menu.icon.singleton'].search([]).ks_font_awesome,
            }
        elif self.ks_icon_type == 'search_icons':
            icon_data = {
                'web_icon_data': self.env['ks.menu.icon.singleton'].search([]).ks_attachment,
            }
        elif self.ks_icon_type == 'special_icons':
            icon_data = {
                'web_icon_data': self.env['ks.menu.icon.singleton'].search([]).ks_attachment,
            }
        else:
            icon_data = {
                'web_icon_data': self.ks_custom_image,
            }
        self.ks_menu_items.sudo().write(icon_data)


class Singleton(models.Model):
    _name = 'ks.menu.icon.singleton'
    _description = 'ks.menu.icon.singleton'

    ks_attachment = fields.Binary('DummyAttchment', attachment=True)
    ks_font_awesome = fields.Char('DummyFontawesome')

    @api.model
    def create(self, values):
        self.env['ks.menu.icon.singleton'].search([]).unlink()
        if 'ks_attachment' in values:
            values['ks_attachment'] = values['ks_attachment'].split(',')[-1]
        if 'ks_font_awesome' in values:
            values['ks_font_awesome'] = values['ks_font_awesome']
        return super(Singleton, self).create(values)