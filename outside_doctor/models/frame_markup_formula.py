# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from base64 import b32encode, b64encode
from os import remove, urandom
from tempfile import mkstemp
from logging import getLogger
from datetime import date,datetime


from odoo import fields, models, _
from odoo.exceptions import AccessError
from odoo.http import request


class FrameMarkupFormula(models.Model):
    _name = 'frame.markup.formula'
    _description = 'frame.markup.formula'

    name = fields.Char('Name',index=True)
    collection_id = fields.Many2many('spec.collection.collection','collection_region_rel', 'collection_id', 'collectionregion_id', string="Collection")
    w_price_min = fields.Float('Wholesale Price Min')
    w_price_max = fields.Float('Wholesale Price Max')
    multiplier = fields.Float('Multiplier')
    additional_amt = fields.Float('Additional Amount')
    next_ten = fields.Boolean('Next Ten')
    ends_with = fields.Float('Ends With')


