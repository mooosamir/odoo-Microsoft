from odoo import api, fields, models, _


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('stripe_backend', 'Stripe Backend')])
    stripe_backend_secret_key = fields.Char(required_if_provider='stripe_backend', groups='base.group_user')
    stripe_backend_publishable_key = fields.Char(required_if_provider='stripe_backend', groups='base.group_user')
