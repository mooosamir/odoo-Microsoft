from odoo import http
from odoo.http import request
import os
import base64


class ThemeBackendCustomization(http.Controller):

    def _color_create_attach_and_view(self, ks_custom_url, datas, ks_scss_path, key, name):
        ks_ir_attachment = request.env["ir.attachment"]
        _create_attach = {
            'name': name,
            'type': "binary",
            'mimetype': "text/scss",
            'datas': datas,
            'store_fname': ks_scss_path.split("/")[-1],
            'url': ks_custom_url,
        }
        ks_ir_attachment.sudo().create(_create_attach)
        _KsIrUiView = request.env["ir.ui.view"]
        assets = request.env['ir.ui.view'].sudo().search([('key', '=', 'web.assets_backend')], limit=1)

        create_view = {
            'name': name,
            'key': key,
            'mode': "extension",
            'priority': 8,
            'active': False,
            'inherit_id': assets.id,
            'arch': """
                      <data>
                          <xpath expr="." position="inside">
                             <link rel="stylesheet" type="text/scss" href="%(new_url)s"/>
                          </xpath>
                      </data>
                  """ % {
                'new_url': ks_custom_url,
            }
        }
        _KsIrUiView.sudo().create(create_view)

    def _ks_custom_scss_file_url(self, url, bundle):
        parts = url.rsplit(".", 1)
        return "%s.custom.%s.%s" % (parts[0], bundle, parts[1])

    # this is for updating new file for new color palette
    @http.route([
        '/write/updated/backendtheme/color',
    ], type='http', auth="user")
    def KsWriteUpdatedScss(self, **kw):
        if kw.get('headerbgcolor', False):
            all_color_list = [int(i.key.split('_')[-1] or 0) for i in request.env['ir.ui.view'].sudo().search(
                [('key', 'like', 'ks_theme_kernel.backend_color_%'),('active', 'in', [1, 0, ''])])]

            count = max(all_color_list)
            count += 1
            ks_scss_path = "/static/src/scss/themes/color_" + str(count) + ".scss"
            data = "$sidebar-width:90px;$page-bg-color:#ececef;$badge-bg:#e75e40;$sidebar-icon-color:#7c7c7c;$dark-gray:#dfdfe6;$light-gray:#f7f7f7;$ks-theme-radius:4px;$sidebar-text-color:#000;$invert:0;$icons-opacity:0.7;$drawer-bg:$primary;$app-name-color:$primary;$search-bg:$sidebar-bg-color;$secondary-color:#5a5d7c;$user-info-bg:#fff;$menu-level-bg:#fafafa;$kanban-bg:#dedee3;$text-muted:#4f4f4f;$btn-outlined-color:$primary;$input-bg:#ececef;$table-border-color:#dee2e6;$table-text-color:#232323;$table-text-muted:#7c7e80;$table-hover-color:#dcdce7;$table-row-focus:#fafafa;$chekbox-color:#4c4c4c;$notification-bg:#f8f9fa;$primary-on-light:$primary;$searchbar-bg-color:#fff;$searchbar-border-color:#ccc;$primary-and-grey:#e9ecef;$label-color:$primary-light;$text-white-gray:#3a3a3a;$nav-active:#fff;$placeholder-text:#7e7e7e;$btn-primary:$primary;$ks-dis-sidebar:#212529;$ks-message-body:#fff;$ks-message-search:#fff;$ks-search-input:#000;"
            data = kw['headerbgcolor'] + '\n' + kw['headertextcolor'] + '\n' + kw['buttonbgcolor'] + '\n' + kw[
                'buttontextcolor'] + '\n' + kw['headingbgcolor'] + '\n' + kw['headingtextcolor'] + data
            bundle_xmlid = 'web.assets_common'
            ks_custom_url = self._ks_custom_scss_file_url(ks_scss_path, bundle_xmlid)
            ks_custom_url = '/' + 'ks_theme_kernel' + ks_custom_url
            datas = base64.b64encode(
                ("%s\n" % (data)).encode("utf-8"))
            if datas:
                self._color_create_attach_and_view(ks_custom_url, datas, ks_scss_path,
                                                   'ks_theme_kernel.backend_color_' + str(count), 'color_' + str(count))

    def createQwebIfNotAvialable(self, key, file_name, name):
        global qweb
        color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
        if color_selected_option == 'user':
            qweb = request.env['ir.ui.view'].sudo().search([('key', '=', key), ('ks_user_id', '=', request.env.user.id)])
        if color_selected_option == 'company':
            qweb = request.env['ir.ui.view'].sudo().search(
                [('key', '=', key), ('ks_company_id', '=', request.env.user.company_id.id)])
        if qweb:
            return
        else:
            assets = request.env['ir.ui.view'].sudo().search([('key', '=', 'web.assets_backend')], limit=1)
            view_arch = '''<data priority="111"  inherit_id="web.assets_backend" active="False">
                          <xpath expr="." position="inside">
                          <link rel="stylesheet" type="text/css" href="/ks_theme_kernel/static/src/scss/themes/%s.scss"/> 
                          </xpath>
                          </data>''' % (file_name)

            res = request.env['ir.ui.view'].sudo().create({
                'name': file_name,
                'key': key,
                'priority': 111,
                'active': False,
                'type': 'qweb',
                'arch_db': view_arch,
                'inherit_id': assets.id,
                'xml_id': key,

            })

        return res

    @http.route([
        '/get/updated/backendtheme/color',
    ], type='http', auth="user")
    def KsGetUpdatedScss(self, **kw):
        if kw.get('header_bg_scss_path', False):
            module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            if module_path == '':
                module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
            ks_scss_path = module_path + "/static/src/scss/themes/default_color.scss"
            exists = os.path.isfile(ks_scss_path)
            if exists:
                f = open(ks_scss_path, 'r')
                header_bgcolor = f.read()
                return header_bgcolor.split('\n')[0].split(":")[1][:8]
            return "#FAB446"
        elif kw.get('header_text_scss_path', False):
            module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            if module_path == '':
                module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
            ks_scss_path = module_path + "/static/src/scss/themes/default_color.scss"
            exists = os.path.isfile(ks_scss_path)
            if exists:
                f = open(ks_scss_path, 'r')
                header_textcolor = f.read()
                return header_textcolor.split('\n')[1].split(":")[1][:8]
            return "#FAB446"
        elif kw.get('button_bg_scss_path', False):
            module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            if module_path == '':
                module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
            ks_scss_path = module_path + "/static/src/scss/themes/default_color.scss"
            exists = os.path.isfile(ks_scss_path)
            if exists:
                f = open(ks_scss_path, 'r')
                header_textcolor = f.read()
                return header_textcolor.split('\n')[2].split(":")[1][:8]
            return "#FAB446"
        elif kw.get('button_text_scss_path', False):
            module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            if module_path == '':
                module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
            ks_scss_path = module_path + "/static/src/scss/themes/default_color.scss"
            exists = os.path.isfile(ks_scss_path)
            if exists:
                f = open(ks_scss_path, 'r')
                header_textcolor = f.read()
                return header_textcolor.split('\n')[3].split(":")[1][:8]
            return "#FAB446"
        elif kw.get('heading_bg_scss_path', False):
            module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            if module_path == '':
                module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
            ks_scss_path = module_path + "/static/src/scss/themes/default_color.scss"
            exists = os.path.isfile(ks_scss_path)
            if exists:
                f = open(ks_scss_path, 'r')
                header_textcolor = f.read()
                return header_textcolor.split('\n')[4].split(":")[1][:8]
            return "#FAB446"
        elif kw.get('heading_text_scss_path', False):
            module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
            if module_path == '':
                module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
            ks_scss_path = module_path + "/static/src/scss/themes/default_color.scss"
            exists = os.path.isfile(ks_scss_path)
            if exists:
                f = open(ks_scss_path, 'r')
                header_textcolor = f.read()
                return header_textcolor.split('\n')[5].split(":")[1][:8]
            return "#FAB446"

    # @http.route(['/color/reset'], type='json', auth="user")
    # def colorreset(self):
    #     module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
    #     path = module_path + '/static/src/css/ks_theme_kernel_color.scss'
    #     f = open(path, 'r+')
    #     data = f.read()
    #     values = {
    #         'headerbgcolor': data.split('\n')[0],
    #         'headertxtcolor': data.split('\n')[1],
    #         'buttonbgcolor': data.split('\n')[2],
    #         'buttontxtcolor': data.split('\n')[3],
    #         'headingbgcolor': data.split('\n')[4],
    #         'headingtxtcolor': data.split('\n')[5],
    #     }
    #     return values
