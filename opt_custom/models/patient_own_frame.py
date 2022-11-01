# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, tools
from odoo.exceptions import UserError


class PatientOwnFrame(models.Model):
    _name = "patient.own.frame"
    _description = "patient.own.frame"
    _order = "create_date DESC"

    model_number = fields.Char(string='Model Number')
    color = fields.Char(string='Color #')
    a = fields.Float(string='A')
    b = fields.Float(string='B')
    dbl = fields.Float(string='DBL')
    ed = fields.Float(string='ED')
    bridge = fields.Char(string='Bridge')
    temple = fields.Char(string='Temple')
    edge_id = fields.Many2one('spec.edge.type', string='Edge Type')
    brand_id = fields.Many2one(
        'spec.brand.brand', string='Brand', domain="[('brand_type', '=', 'frame')]")

    def add_from_frame(self):
        self.ensure_one()
        _list = self.env.ref('opt_custom.patients_own_frame_tree', False)
        return {
            'name': _('Add from previous Frame'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'view_type': 'list',
            'view_mode': 'list',
            'target': 'new',
            'view_id': [(_list and _list.id)],
            'views': [(_list and _list.id, 'list')],
        }
