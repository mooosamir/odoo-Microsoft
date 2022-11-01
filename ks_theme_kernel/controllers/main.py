import base64
from odoo.http import Controller, request, route
from werkzeug.utils import redirect
import os
from odoo import http, tools
from odoo.addons.web.controllers.main import Home

Default_BackGround = ''
ks_current_font_id = 'font'


class Ks_BackGroundImage(Controller):

    # this is for background image of login page
    @route(['/login_page/background'], type='http', auth="none")
    def login_background(self, **post):
        user = request.env.user
        company = user.company_id
        bg_image = request.env['ir.config_parameter'].sudo().get_param('login_bg_image')
        if bg_image:
            image = base64.b64decode(bg_image)
        else:
            return redirect(Default_BackGround)
        return request.make_response(
            image, [('Content-Type', 'image')])

    # this is for background image of app drawer
    @route(['/appdrawer/background'], type='http', auth='user')
    def background(self, **post):
        user = request.env.user
        company = user.company_id
        if company.background_image:
            image = base64.b64decode(company.background_image)
        else:
            return redirect(Default_BackGround)

        return request.make_response(
            image, [('Content-Type', 'image')])

    # this is for favourite menu updation
    @route(['/update/favourite/menu'], type='json', auth='user')
    def updatefavouritemenu(self, **post):
        module_path = '/'.join((os.path.realpath(__file__)).split('/')[:-2])
        if module_path == '':
            module_path = '/'.join(os.path.realpath(__file__).split('\\')[:-2])
        ks_current_font_id = 'font'
        ks_current_color_id = 'color'
        user_id = request.env.user.id
        ks_favourite_menu = request.env['ks.favourite.menu']
        if post.get('menu_url', False):
            menu_name = post['menu_name']
            menu_url = post['menu_url']
            request._cr.execute(
                'insert into ks_favourite_menu (ks_menu_name,ks_menu_url,ks_res_user_id) values (%s,%s,%s)',
                (menu_name, menu_url, user_id))
            ks_menu_lines = request.env['ks.favourite.menu'].search([('ks_res_user_id', '=', user_id)])
            ks_current_font_view = request.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
            color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
            if ks_current_font_view:
                ks_current_font_id = ks_current_font_view[0].sudo().current_font_id
                if color_selected_option == 'user':
                    ks_current_color_id = ks_current_font_view[0].sudo().current_color_id
            if color_selected_option == 'company':
                company_id = request.env.user.company_id.id
                ks_current_color_view = request.env['ks.color.company'].search([('ks_company_id', '=', company_id)])
                if ks_current_color_view:
                    ks_current_color_id = ks_current_color_view[0].sudo().current_color_id
            values = {
                'menus': ks_menu_lines,
                'font_id': ks_current_font_id,
                'color_id': ks_current_color_id,
            }
            return request.env['ir.ui.view'].render_template("ks_theme_kernel.ks_favourite_menu_lines", values)

        elif post.get('rename', False):
            menu_name = post['menu_name']
            menu_id = post['menu_id']
            request._cr.execute('update ks_favourite_menu set ks_menu_name=%s where id = %s and ks_res_user_id = %s ',
                                (menu_name, menu_id, user_id))
        elif post.get('delete', False):
            menu_id = post['menu_id']
            request._cr.execute('Delete from ks_favourite_menu where id =%s and ks_res_user_id = %s',
                                (menu_id, user_id))
            ks_menu_lines = request.env['ks.favourite.menu'].search([('ks_res_user_id', '=', user_id)])
            ks_current_font_view = request.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
            color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
            if ks_current_font_view:
                ks_current_font_id = ks_current_font_view[0].sudo().current_font_id
                if color_selected_option == 'user':
                    ks_current_color_id = ks_current_font_view[0].sudo().current_color_id
            if color_selected_option == 'company':
                company_id = request.env.user.company_id.id
                ks_current_color_view = request.env['ks.color.company'].search([('ks_company_id', '=', company_id)])
                if ks_current_color_view:
                    ks_current_color_id = ks_current_color_view[0].sudo().current_color_id
            values = {
                'menus': ks_menu_lines,
                'font_id': ks_current_font_id,
                'color_id': ks_current_color_id,
            }
            return request.env['ir.ui.view'].render_template("ks_theme_kernel.ks_favourite_menu_lines", values)
        return False

    # this is for render the favourite menu line
    @route(['/favourite/menu/template'], type='json', auth='user')
    def favouritemenutemplate(self, **post):
        user_id = request.env.user.id
        ks_current_font_id = 'font'
        ks_current_color_id = 'color'
        ks_menu_lines = request.env['ks.favourite.menu'].search([('ks_res_user_id', '=', user_id)])
        ks_current_font_view = request.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
        color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
        if ks_current_font_view:
            ks_current_font_id = ks_current_font_view[0].sudo().current_font_id
            if color_selected_option == 'user':
                ks_current_color_id = ks_current_font_view[0].sudo().current_color_id
        if color_selected_option == 'company':
            company_id = request.env.user.company_id.id
            ks_current_color_view = request.env['ks.color.company'].search([('ks_company_id', '=', company_id)])
            if ks_current_color_view:
                ks_current_color_id = ks_current_color_view[0].sudo().current_color_id
        values = {
            'menus': ks_menu_lines,
            'font_id': ks_current_font_id,
            'color_id': ks_current_color_id,
        }
        return request.env['ir.ui.view'].render_template("ks_theme_kernel.ks_favourite_menu_lines", values)

    # this is for render the color pallete after updating
    @route(['/updatedcolor/pallete/template'], type='json', auth='user')
    def updatecolorpalletetemplate(self, **post):
        adv_access = request.env.user.user_has_groups('ks_theme_kernel.ks_theme_kernel_adv_settings')
        current_active_pallete_color = 'color'
        main_color = ''
        alternate_color = ''
        current_active_pallete_color_view = request.env['ir.ui.view'].search(
            [('key', 'like', 'ks_theme_kernel.backend_color_%'), ('active', '=', True),
             ('ks_user_id', '=', request.uid)])
        if current_active_pallete_color_view:
            current_active_pallete_color = current_active_pallete_color_view[0].sudo().name
        all_color_list = [int(i.key.split('_')[-1] or 0) for i in request.env['ir.ui.view'].search(
            [('key', 'like', 'ks_theme_kernel.backend_color_%'), ('active', 'in', [1, 0, ''])])]

        color_list = list(set(sorted(all_color_list)[1:]))
        if 0 in color_list:
            color_list.remove(0)
        new_added_main_color = []
        new_added_alternate_color = []
        for i in color_list:
            if i > 10:
                ks_color_palletes_path = "color_" + str(i)
                KsIrAttachment = request.env["ir.attachment"].sudo().search([('name', '=', ks_color_palletes_path)],
                                                                            limit=1)
                if KsIrAttachment:
                    primary_color = KsIrAttachment.index_content.split(';')[0]
                    main_color = primary_color.split('\n')[0].split(":")[1][:8]
                    alternate_color = main_color
                new_added_main_color.append(main_color)
                new_added_alternate_color.append(alternate_color)
        values = {
            'color_list': color_list,
        }
        color_pallete_html = request.env['ir.ui.view'].render_template("ks_theme_kernel.ks_color_pallete_list", values)
        return {
            'pallete_html': color_pallete_html,
            'new_added_main_color': new_added_main_color,
            'new_added_alternate_color': new_added_alternate_color,
            'current_active_color_pallete': current_active_pallete_color,
            'adv_access': adv_access
        }

    def _ks_get_attachment(self, ks_custom_url, op='='):
        assert op in ('=like', '='), 'Invalid operator'
        KsIrAttachment = request.env["ir.attachment"]
        website = request.env['website'].get_current_website()
        return KsIrAttachment.search([("url", op, ks_custom_url), ('website_id', '=', website.id)])

    # this is for deleting the selectted color palette
    @route(['/delete/color/pallete'], type='json', auth='user')
    def deletecolorpalletetemplate(self, **post):
        user_id = request.env.user.id
        company_id = request.env.user.company_id.id
        view = request.env['ir.ui.view']
        if post.get('delete_color_id', False):
            delete_color_id = post['delete_color_id']
            KsIrAttachment = request.env["ir.attachment"].sudo().search([('name', '=', delete_color_id)], limit=1)
            if KsIrAttachment:
                KsIrAttachment.sudo().unlink()
            color_key = 'ks_theme_kernel.backend_' + post['delete_color_id']
            all_views = view.search([('key', '=', color_key), ('active', 'in', [1, 0, ''])])
            for view in all_views:
                if view.active:
                    home_view = request.env['ks.home.view']
                    color_info = home_view.search(
                        [('ks_user_id', '=', user_id), ('current_color_id', '=', delete_color_id)])
                    if color_info:
                        color_info.sudo().write({
                            'current_color_id': 'color'
                        })
                    color_view = request.env['ks.color.company']
                    color_info = color_view.search(
                        [('ks_company_id', '=', company_id), ('current_color_id', '=', delete_color_id)])
                    if color_info:
                        color_info.sudo().write({
                            'current_color_id': 'color'
                        })
                    default_color_view = view.search(
                        [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                    if default_color_view:
                        default_color_view.sudo().write({
                            'active': True
                        })
                view.sudo().unlink()
        return None

    # this is for render the favourite menu lines
    @route(['/favourite/floating/template'], type='json', auth='user')
    def favouritefloatingtemplate(self, **post):
        user_id = request.env.user.id
        ks_menu_lines = request.env['ks.favourite.menu'].search([('ks_res_user_id', '=', user_id)])
        values = {
            'menus': ks_menu_lines
        }
        return request.env['ir.ui.view'].render_template("ks_theme_kernel.ks_favourite_floating_menu", values)

    # this is for active the current font for current user
    @route(['/update/font/css'], type='json', auth='user')
    def updatefontcss(self, **post):
        user_id = request.env.user.id
        view = request.env['ir.ui.view']
        all_template = view.search(
            [('key', 'like', 'ks_theme_kernel.backend_font_'), ('active', '=', True), ('ks_user_id', '=', user_id)])
        for view in all_template:
            view.sudo().write({
                'active': False
            })
        if post.get('font_id', False):
            font_id = post['font_id']
            home_view = request.env['ks.home.view']
            font_info = home_view.search([('ks_user_id', '=', user_id)])
            if font_info:
                font_info.sudo().write({
                    'current_font_id': font_id
                })
            else:
                home_view.sudo().create({
                    'current_font_id': font_id,
                    'ks_user_id': user_id
                })
            current_click_font_key = 'ks_theme_kernel.backend_' + post['font_id']
            current_view = view.search(
                [('key', '=', current_click_font_key), ('active', '=', False), ('ks_user_id', '=', user_id)])
            if not current_view:
                current_copied_view = view.search([('key', '=', current_click_font_key), ('active', '=', False),
                                                   ('ks_user_id', '=', False)])[0].sudo().copy()
                current_copied_view.sudo().write({
                    'active': True,
                    'ks_user_id': user_id
                })
            else:
                current_view[0].sudo().write({
                    'active': True,
                })
        return None

    # this is for updating active color palette for current user
    @route(['/update/colorpallete/css'], type='json', auth='user')
    def updatecolorpalletecss(self, **post):
        color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
        view = request.env['ir.ui.view']
        user_id = request.env.user.id
        company_id = request.env.user.company_id.id
        if color_selected_option == 'user':
            all_template = view.search(
                [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
            for view in all_template:
                view.sudo().write({
                    'active': False
                })
            if post.get('color_id', False):
                color_id = post['color_id']
                home_view = request.env['ks.home.view']
                color_info = home_view.search([('ks_user_id', '=', user_id)])
                if color_info:
                    color_info.sudo().write({
                        'current_color_id': color_id
                    })
                else:
                    home_view.sudo().create({
                        'current_color_id': color_id,
                        'ks_user_id': user_id
                    })
                current_click_color_key = 'ks_theme_kernel.backend_' + post['color_id']
                current_view = view.search(
                    [('key', '=', current_click_color_key), ('active', '=', False), ('ks_user_id', '=', user_id)])
                if not current_view:
                    current_copied_view = view.search([('key', '=', current_click_color_key), ('active', '=', False),
                                                       ('ks_user_id', '=', False)])[0].sudo().copy()
                    current_copied_view.sudo().write({
                        'active': True,
                        'ks_user_id': user_id
                    })
                else:
                    current_view[0].sudo().write({
                        'active': True,
                    })
            return None

        if color_selected_option == 'company':
            all_template = view.search(
                [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
            for view in all_template:
                view.sudo().write({
                    'active': False
                })
            if post.get('color_id', False):
                color_id = post['color_id']
                home_view = request.env['ks.color.company']
                color_info = home_view.search([('ks_company_id', '=', company_id)])
                if color_info:
                    color_info.sudo().write({
                        'current_color_id': color_id
                    })
                else:
                    home_view.sudo().create({
                        'current_color_id': color_id,
                        'ks_company_id': company_id
                    })
                current_click_color_key = 'ks_theme_kernel.backend_' + post['color_id']
                current_view = view.search(
                    [('key', '=', current_click_color_key), ('active', '=', False), ('ks_company_id', '=', company_id)])
                if not current_view:
                    current_copied_view = view.search([('key', '=', current_click_color_key), ('active', '=', False),
                                                       ('ks_company_id', '=', False)])[0].sudo().copy()
                    current_copied_view.sudo().write({
                        'active': True,
                        'ks_company_id': company_id
                    })
                else:
                    current_view[0].sudo().write({
                        'active': True,
                    })
            return None

    @route(['/color/mode'], type='json', auth='user')
    def colormode(self, **post):
        color_mode = post['color_mode']
        view = request.env['ir.ui.view']
        color_mode_view = request.env['ks.color.mode']
        user_id = request.env.user.id
        color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
        company_id = request.env.user.company_id.id
        if color_mode == 'light_mode':
            all_dark_template = view.search(
                [('key', 'like', 'ks_theme_kernel.backend_dark_color'), ('active', '=', True)])
            for view in all_dark_template:
                view.sudo().write({
                    'active': False
                })
            color_mode_info = color_mode_view.search([('ks_user_id', '=', user_id)])
            if color_mode_info:
                color_mode_info.sudo().write({
                    'current_color_mode': 'light'
                })
            else:
                color_mode_view.sudo().create({
                    'current_color_mode': 'light',
                    'ks_user_id': user_id
                })
            if color_selected_option == 'company':
                all_template = view.search(
                    [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                for view in all_template:
                    view.sudo().write({
                        'active': False
                    })
                current_active_color_view = request.env['ks.color.company'].search([('ks_company_id', '=', company_id)])
                if current_active_color_view:
                    current_active_color = current_active_color_view.sudo().current_color_id
                    if current_active_color:
                        active_color_key = 'ks_theme_kernel.backend_' + current_active_color
                        color_view = view.search(
                            [('key', '=', active_color_key), ('active', '=', False),
                             ('ks_company_id', '=', company_id)])
                        if color_view:
                            color_view.sudo().write({
                                'active': True
                            })
                        else:
                            defaul_color_view = view.search(
                                [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                            if defaul_color_view:
                                defaul_color_view.sudo().write({
                                    'active': True
                                })
                    else:
                        defaul_color_view = view.search(
                            [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                        if defaul_color_view:
                            defaul_color_view.sudo().write({
                                'active': True
                            })
                else:
                    defaul_color_view = view.search(
                        [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                    if defaul_color_view:
                        defaul_color_view.sudo().write({
                            'active': True
                        })

            if color_selected_option == 'user':
                all_template = view.search(
                    [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                for view in all_template:
                    view.sudo().write({
                        'active': False
                    })
                current_active_color_view = request.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
                if current_active_color_view:
                    current_active_color = current_active_color_view.sudo().current_color_id
                    if current_active_color:
                        active_color_key = 'ks_theme_kernel.backend_' + current_active_color
                        color_view = view.search(
                            [('key', '=', active_color_key), ('active', '=', False), ('ks_user_id', '=', user_id)])
                        if color_view:
                            color_view.sudo().write({
                                'active': True
                            })
                        else:
                            defaul_color_view = view.search(
                                [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                            if defaul_color_view:
                                defaul_color_view.sudo().write({
                                    'active': True
                                })
                    else:
                        defaul_color_view = view.search(
                            [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                        if defaul_color_view:
                            defaul_color_view.sudo().write({
                                'active': True
                            })
                else:
                    defaul_color_view = view.search(
                        [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                    if defaul_color_view:
                        defaul_color_view.sudo().write({
                            'active': True
                        })
        elif color_mode == 'dark_mode':
            all_template = view.search(
                [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
            for view in all_template:
                view.sudo().write({
                    'active': False
                })
            all_dark_template = view.search(
                [('key', 'like', 'ks_theme_kernel.backend_dark_color'), ('active', '=', True)])
            for view in all_dark_template:
                view.sudo().write({
                    'active': False
                })
            color_mode_info = color_mode_view.search([('ks_user_id', '=', user_id)])
            if color_mode_info:
                color_mode_info.sudo().write({
                    'current_color_mode': 'dark'
                })
            else:
                color_mode_view.sudo().create({
                    'current_color_mode': 'dark',
                    'ks_user_id': user_id
                })
            dark_color_view = view.search([('key', '=', 'ks_theme_kernel.backend_dark_color'), ('active', '=', False),
                                           ('ks_user_id', '=', user_id)])
            if dark_color_view:
                dark_color_view.sudo().write({
                    'active': True
                })
            else:
                default_dark_color_view = view.search(
                    [('key', '=', 'ks_theme_kernel.backend_dark_color'), ('active', '=', False)])
                if default_dark_color_view:
                    dark_color_view_copy = default_dark_color_view[0].sudo().copy()
                    dark_color_view_copy.sudo().write({
                        'active': True,
                        'ks_user_id': user_id
                    })
        return False


class Home(Home):

    # this is for handle the color and font at login time
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        res = super(Home, self).web_login(redirect=None, **kw)
        login_status = request.params['login_success']
        current_active_color = False
        current_active_font = False
        current_active_mode = 'light'
        if login_status:
            view = request.env['ir.ui.view']
            user_id = request.env.user.id
            company_id = request.env.user.company_id.id
            color_selected_option = request.env['ir.config_parameter'].sudo().get_param('color_options')
            all_font_template = view.search(
                [('key', 'like', 'ks_theme_kernel.backend_font_'), ('active', '=', True)])
            for view_1 in all_font_template:
                view_1.sudo().write({
                    'active': False
                })
            current_active_font_view = request.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
            if current_active_font_view:
                current_active_font = current_active_font_view.sudo().current_font_id

            if current_active_font:
                active_font_key = 'ks_theme_kernel.backend_' + current_active_font
                font_view = view.search(
                    [('key', '=', active_font_key), ('active', '=', False), ('ks_user_id', '=', user_id)])
                if font_view:
                    font_view.sudo().write({
                        'active': True
                    })
            current_active_colormode_view = request.env['ks.color.mode'].search([('ks_user_id', '=', user_id)])
            if current_active_colormode_view:
                current_active_mode = current_active_colormode_view.sudo().current_color_mode

            if current_active_mode == 'light':
                all_dark_template = view.search(
                    [('key', 'like', 'ks_theme_kernel.backend_dark_color'), ('active', '=', True)])
                for view in all_dark_template:
                    view.sudo().write({
                        'active': False
                    })
                if color_selected_option == 'user':
                    all_color_template = view.search(
                        [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                    for view_2 in all_color_template:
                        view_2.sudo().write({
                            'active': False
                        })
                    current_active_color_view = request.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
                    if current_active_color_view:
                        current_active_color = current_active_color_view.sudo().current_color_id
                        if current_active_color:
                            active_color_key = 'ks_theme_kernel.backend_' + current_active_color
                            color_view = view.search(
                                [('key', '=', active_color_key), ('active', '=', False), ('ks_user_id', '=', user_id)])
                            if color_view:
                                color_view.sudo().write({
                                    'active': True
                                })
                            else:
                                defaul_color_view = view.search(
                                    [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                                if defaul_color_view:
                                    defaul_color_view.sudo().write({
                                        'active': True
                                    })
                        else:
                            defaul_color_view = view.search(
                                [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                            if defaul_color_view:
                                defaul_color_view.sudo().write({
                                    'active': True
                                })
                    else:
                        defaul_color_view = view.search(
                            [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                        if defaul_color_view:
                            defaul_color_view.sudo().write({
                                'active': True
                            })

                if color_selected_option == 'company':
                    all_template = view.search(
                        [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                    for view in all_template:
                        view.sudo().write({
                            'active': False
                        })
                    current_active_color_view = request.env['ks.color.company'].search(
                        [('ks_company_id', '=', company_id)])
                    if current_active_color_view:
                        current_active_color = current_active_color_view.sudo().current_color_id
                        if current_active_color:
                            active_color_key = 'ks_theme_kernel.backend_' + current_active_color
                            color_view = view.search(
                                [('key', '=', active_color_key), ('active', '=', False),
                                 ('ks_company_id', '=', company_id)])
                            if color_view:
                                color_view.sudo().write({
                                    'active': True
                                })
                            else:
                                defaul_color_view = view.search(
                                    [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                                if defaul_color_view:
                                    defaul_color_view.sudo().write({
                                        'active': True
                                    })
                        else:
                            defaul_color_view = view.search(
                                [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                            if defaul_color_view:
                                defaul_color_view.sudo().write({
                                    'active': True
                                })
                    else:
                        defaul_color_view = view.search(
                            [('key', '=', 'ks_theme_kernel.backend_color_'), ('active', '=', False)])
                        if defaul_color_view:
                            defaul_color_view.sudo().write({
                                'active': True
                            })
            elif current_active_mode == 'dark':
                all_template = view.search(
                    [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                for view in all_template:
                    view.sudo().write({
                        'active': False
                    })
                all_dark_template = view.search(
                    [('key', 'like', 'ks_theme_kernel.backend_dark_color'), ('active', '=', True)])
                for view in all_dark_template:
                    view.sudo().write({
                        'active': False
                    })
                dark_color_view = view.search(
                    [('key', '=', 'ks_theme_kernel.backend_dark_color'), ('active', '=', False),
                     ('ks_user_id', '=', user_id)])
                if dark_color_view:
                    dark_color_view.sudo().write({
                        'active': True
                    })

        return res
