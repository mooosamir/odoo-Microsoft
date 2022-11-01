# -*- coding: utf-8 -*-
from odoo import http


class TwilioWebHooks(http.Controller):
    @http.route('/twilio_response/', auth='none', cors='*', csrf=False, method=['POST'])
    def index(self, **kw):
        print("Hello, world")

#     @http.route('/twillo_all/twillo_all/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('twillo_all.listing', {
#             'root': '/twillo_all/twillo_all',
#             'objects': http.request.env['twillo_all.twillo_all'].search([]),
#         })

#     @http.route('/twillo_all/twillo_all/objects/<model("twillo_all.twillo_all"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('twillo_all.object', {
#             'object': obj
#         })
