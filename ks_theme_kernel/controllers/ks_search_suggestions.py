from odoo import http, _
from odoo.http import request
import json
from odoo.exceptions import ValidationError


class MenuSearchSuggestions(http.Controller):

    """ This search works on the MENU ITEMS OF THE INSTALLED APPS"""

    @http.route([
        '/get/search/suggestions/<string:query>',
    ], type='http', auth="user")
    def ks_menu_search_suggestions(self, query=''):
        if query:
            try:
                ir_ui_menu = request.env['ir.ui.menu']
                menu_ids = ir_ui_menu.sudo().load_menus(request.session.debug)['all_menu_ids']

                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                ks_result = ir_ui_menu.sudo().search_read(
                    [('display_name', 'ilike', query + '%'), ('action', '!=', None), ('id', 'in', menu_ids)],
                    fields=['display_name', 'action'])

                for res in ks_result:
                    res.update({
                        'name': res['display_name'],
                        'url': '/web#menu_id=%s&action=%s' % (
                        res['id'], res['action'] and res['action'].split(',')[1] or '')

                    })

                def sort_on_query(x):
                    if x['display_name'].lower().startswith(query):
                        return x['display_name'][:1]
                    else:
                        return x['display_name'][1:]

                sorted_res = sorted(ks_result, key=sort_on_query)
                return json.dumps({"result": sorted_res}, skipkeys=True)
            except Exception as e:
                raise ValidationError(_("Something went wrong: " + str(e)))
