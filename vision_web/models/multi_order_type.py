from odoo import api, fields, models, _, exceptions


class MultiOrderTypes(models.Model):
    _inherit = "multi.order.type"

    # is_transmitted_to_vw = fields.Boolean(default=False, help="Is transmitted to vision web.")
    vw_order_id = fields.Char()
    vw_order_status = fields.Char()

    def update_order_status(self):
        response = self.env['vision.web'].order_tracking(self.id)
        if 'Status' not in response:
            return "error finding status for this order."
