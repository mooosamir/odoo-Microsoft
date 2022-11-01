
from odoo import models, fields


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    diagnosis_lines = fields.One2many('sale.diagnosis.setup', 'move_id')
    is_insurance = fields.Boolean(string='is_insurance', related="partner_id.is_insurance")

    def action_view_hcpcs_lines(self):
        view = {
            'name': "HCPCS",
            'res_model': 'sale.order.line.hcpcs',
            'view_mode': 'tree',
            # 'domain': [('order_line_id', 'in', self.invoice_line_ids.sale_line_ids.ids)],
            'domain': [('sale_order_line_wizard_id', 'in', self.invoice_line_ids.sale_line_ids.lab_details_id.ids)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
        if self.is_insurance:
            view['view_id'] = self.env.ref('ivis_order_grouping.sale_order_line_hcpcs_form_insurance').id,
        else:
            view['view_id'] = self.env.ref('ivis_order_grouping.sale_order_line_hcpcs_form_patient').id,
        return view