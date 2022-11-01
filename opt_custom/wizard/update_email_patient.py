# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
import re


class UpdateEmailPatient(models.TransientModel):
    _name = "update.email.patient.profile"
    _description = "Update Email Patient Profile"

    email = fields.Char('Email')

    @api.constrains('email')
    def _check_email_address(self):
        for rec in self:
            if rec.email:
                match = re.match(
                    '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', rec.email)
                if not match:
                    raise UserError('Please Enter Valid Email')

    def action_update_email(self):
        patient = self.env['res.partner'].browse(self._context.get('active_id'))
        if patient:
            patient.email= self.email
        user = self.env['res.users'].search([('partner_id', '=', self._context.get('active_id'))])
        user.action_reset_password()