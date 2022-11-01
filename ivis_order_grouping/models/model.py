# import json
#
# from odoo import models, fields, tools, api, exceptions, _
# from odoo.exceptions import AccessError, UserError, ValidationError
# from datetime import date

# class InheritProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     def name_get(self):
#         result = []
#         for record in self:
#             if record.product_packaging_id and record.list_price and record.spec_product_type == 'contact_lens':
#                 name = str(record.product_packaging_id.name) + ' $' + str(record.list_price)
#             else:
#                 manufacturer = record.contact_lens_manufacturer_id.name if record.contact_lens_manufacturer_id else ''
#                 name = manufacturer + ' ' + record.name
#             result.append((record.id, name))
#         return result

