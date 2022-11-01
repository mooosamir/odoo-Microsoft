# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Service(models.Model):
    _inherit = "product.template"

    ser_pro_code_id = fields.Many2one('spec.procedure.code', string='Procedure')
    ser_modifier_id = fields.Many2one('spec.lens.modifier', string='Modifier')
    duration = fields.Integer("Appointment Duration (mins)")
    appointment_checkbox = fields.Boolean("Appointment")
    color = fields.Char(string="color")
    online_checkbox = fields.Boolean("Online")
    recall_type = fields.Many2one("spec.recall.type", string="Recall Type")
    prd_categ_name = fields.Char(related="categ_id.name")

    @api.constrains('duration')
    def val_duration(self):
        for rec in self:
            if rec.duration <= 0:
                raise ValidationError("Duration can't be negative or Null!")
