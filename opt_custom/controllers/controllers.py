from datetime import datetime

from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from openerp.http import request


# class AuthSignupHomeExt(AuthSignupHome):

    # def get_auth_signup_qcontext(self):
    #     qcontext = super(AuthSignupHomeExt, self).get_auth_signup_qcontext()
    #     qcontext['collections'] = request.env["spec.collection.collection"].sudo().search([])
    #     qcontext['business_types'] = request.env["spec.business.type"].sudo().search([])
    #     return qcontext

    # def do_signup(self, qcontext):
    #     """ Shared helper that creates a res.partner out of a token """
    #     values = { key: qcontext.get(key) for key in ('login', 'name', 'password', 'business_type', 'collection_ids') }
    #     if not values:
    #         raise UserError(_("The form was not properly filled in."))
    #     if values.get('password') != qcontext.get('confirm_password'):
    #         raise UserError(_("Passwords do not match; please retype them."))
    #     supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
    #     lang = request.context.get('lang', '').split('_')[0]
    #     if lang in supported_lang_codes:
    #         values['lang'] = lang
    #     if values.get('business_type'):
    #         business_type_value = request.env['spec.business.type'].browse(int(values.get('business_type')))
    #         values['business_type'] = business_type_value.name
    #     else:
    #         values['business_type']=False
    #
    #     if values.get('collection_ids'):
    #         collection_ids = [int(cid) for cid in values.get('collection_ids').split(',')]
    #         values['collection_ids'] = [(6,0,collection_ids)]
    #     else:
    #         values['collection_ids']=False
    #     self._signup_with_values(qcontext.get('token'), values)
    #     request.env.cr.commit()
