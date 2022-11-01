# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import fields, models, api


class Role(models.Model):
    _name = 'employee.role'
    _description = 'employee.role'

    name = fields.Char('Group Name',index=True)
    groups = fields.Many2many('res.groups', string='Groups')


class ResUsers(models.Model):
    _inherit = "res.users"

    role_id = fields.Many2one('employee.role', string="Role")

    @api.onchange('role_id')
    def _onchange_role_id(self):
        for res in self:
            for role_id_group in res.role_id.groups.ids:
                if role_id_group not in res.groups_id.ids:
                    res.groups_id = [(4, role_id_group)]

