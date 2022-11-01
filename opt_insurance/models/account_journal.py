# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    insurance = fields.Boolean(string="Insurance")
