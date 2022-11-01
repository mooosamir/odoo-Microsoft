# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    active = fields.Boolean(default=True, groups='opt_security.opt_patient_archive')