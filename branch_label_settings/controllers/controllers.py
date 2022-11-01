# -*- coding: utf-8 -*-
# from odoo import http


# class BranchLabelSettings(http.Controller):
#     @http.route('/branch_label_settings/branch_label_settings/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/branch_label_settings/branch_label_settings/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('branch_label_settings.listing', {
#             'root': '/branch_label_settings/branch_label_settings',
#             'objects': http.request.env['branch_label_settings.branch_label_settings'].search([]),
#         })

#     @http.route('/branch_label_settings/branch_label_settings/objects/<model("branch_label_settings.branch_label_settings"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('branch_label_settings.object', {
#             'object': obj
#         })
