
from odoo import models, fields


class DispensingNotes(models.Model):
    _name = "dispensing.notes"
    _description = "Dispensing Notes"

    name = fields.Char(string="Dispensing Notes")
