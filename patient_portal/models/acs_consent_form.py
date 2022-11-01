# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AcsConsentForm(models.Model):
    _inherit = 'acs.consent.form'

    appointment_id = fields.Many2one('calendar.event')
