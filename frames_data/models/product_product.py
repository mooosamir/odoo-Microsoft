from odoo import models, fields, api, exceptions
from string import digits


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _rec_name = 'name'

    def name_get(self):
        response = []
        for data in self:
            if data.product_tmpl_id.categ_id.name == 'Frames':
                color_id = (str(data.color_id.name).replace('(','').replace(')','').translate(str.maketrans('', '', digits)) if data.color_id.id else "")
                response.append((data.id, str(data.name) + " " + color_id +  (" (" + str(data.color_code_id.name) + ") " if data.color_code_id.id else "") + (str(data.eye) + "-" if data.eye else "") + (str(data.bridge) + "-" if data.bridge else "") + (str(data.temple) if data.temple else "")))
            else:
                response.append(super(ProductProduct, data).name_get()[0])

        return response