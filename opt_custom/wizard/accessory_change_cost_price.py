# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import ValidationError


class AccessoryChangeCostPrice(models.TransientModel):
    """Accessory Change Cost Price"""
    _name = "spec.accessorry.change.cost.price"
    _description = "Asseory Cost Price change"

    currency_id = fields.Many2one('res.currency', string="currency", readonly="1",
    					default=lambda self: self.env.user.company_id.currency_id)
    new_price = fields.Monetary(string="Cost")

    def action_change_price(self):
        """Method to Change Accessory Cost Price."""
        active_id = self._context.get('active_id')
        accessory_id = self.env['product.template'].browse(active_id)

        if self.new_price <= 0:
                raise ValidationError("Price shouble not be 0 or negative!")
        else:
            accessory_id.cost_price = self.new_price



class MailComposer(models.TransientModel):
    """ Generic message composition wizard. You may inherit from this wizard
        at model and view levels to provide specific features.

        The behavior of the wizard depends on the composition_mode field:
        - 'comment': post on a record. The wizard is pre-populated via ``get_record_data``
        - 'mass_mail': wizard in mass mailing mode where the mail details can
            contain template placeholders that will be merged with actual data
            before being sent to each recipient.
    """
    _inherit = 'mail.compose.message'
    _description = 'Email composition wizard'


    def action_send_mail(self):
        self.send_mail()
        if self.env.context.get('mark_rfq_as_sent'):
            purchase_recs = self.env['purchase.order'].search([('id', 'in', self.env.context.get('active_ids'))])
            for rec in purchase_recs:
                pickings = rec.picking_ids
                for pick in pickings:
                    if pick.state != 'done':
                        wiz_act = pick.button_validate()
                        wiz = self.env[wiz_act['res_model']].browse(wiz_act['res_id'])
                        wiz.process()
                    
                rec.write({'state': 'sent'})
        return {'type': 'ir.actions.act_window_close', 'infos': 'mail_sent'}
