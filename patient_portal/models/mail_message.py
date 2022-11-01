# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    is_delete = fields.Boolean(string='is_delete')
