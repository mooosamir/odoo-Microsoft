# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "credentials for Stripe"

    stripe_backend_secret_key = fields.Char(string="Secret Key")
    stripe_backend_publishable_key = fields.Char(string="Publishable Key")

    @api.model
    def get_values(self):
        res = super(GeneralSettings, self).get_values()

        stripe_backend_secret_key = self.env["payment.acquirer"].search([('provider', '=', 'stripe_backend')]).stripe_backend_secret_key
        stripe_backend_publishable_key = self.env["payment.acquirer"].search([('provider', '=', 'stripe_backend')]).stripe_backend_publishable_key
        res.update(
            stripe_backend_secret_key=stripe_backend_secret_key or False,
            stripe_backend_publishable_key=stripe_backend_publishable_key or False,
        )
        return res

    def set_values(self):
        super(GeneralSettings, self).set_values()
        for record in self:
            stripe = self.env["payment.acquirer"].search([('provider', '=', 'stripe_backend')])
            if stripe.id:
                stripe.stripe_backend_secret_key = record.stripe_backend_secret_key
                stripe.stripe_backend_publishable_key = record.stripe_backend_publishable_key
