# -*- coding: utf-8 -*-
# from odoo import http


# class OptReports(http.Controller):
#     @http.route('/opt_reports/opt_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opt_reports/opt_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opt_reports.listing', {
#             'root': '/opt_reports/opt_reports',
#             'objects': http.request.env['opt_reports.opt_reports'].search([]),
#         })

#     @http.route('/opt_reports/opt_reports/objects/<model("opt_reports.opt_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opt_reports.object', {
#             'object': obj
#         })
