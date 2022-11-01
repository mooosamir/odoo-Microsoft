from odoo import api, fields, models, tools, _


class View(models.Model):
    _inherit = 'ir.ui.view'
    _description = 'View'

    type = fields.Selection(selection_add=[
       ('dashboard', _('Dashboard'))
    ])

class IrActionsActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'
    _description = 'Action Window View'

    view_mode = fields.Selection(selection_add=[
       ('dashboard', _('Dashboard'))
    ])
