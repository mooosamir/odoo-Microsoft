# -*- coding: utf-8 -*-

from odoo import fields, models



class BarcodeWizardReport(models.TransientModel):
    _name = 'barcode.wizard.report'

    name = fields.Char(string='Barcode Name')