from odoo import api, fields, models, _

class Users(models.Model):
    _inherit = "res.users"

    company_ids = fields.Many2many('res.company', 'res_company_users_rel', 'user_id', 'cid',
                                   string='Branches', default=lambda self: self.env.company.ids)