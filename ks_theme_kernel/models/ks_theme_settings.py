from odoo import api, fields, models


class ThemeSettings(models.Model):
    _name = 'theme.setting'
    _description = 'This is for Background Image of Home Screen of backend theme'

    name = fields.Char(string='Name', default='BG Image')
    background_image = fields.Binary(string="App Drawer Background Image",
                                     help='This is for Background Image Of App Drawer', store=True)


class ResCompanySettings(models.Model):
    _inherit = 'res.company'

    background_image = fields.Binary(string="App Drawer Background Image",
                                     help='This is for Background Image Of Dashboard',
                                     attachment=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', ondelete='cascade')
    background_image = fields.Binary(related='company_id.background_image', string="App Drawer Background Image",
                                     readonly=False, store=True)

    menu_options = fields.Selection([('Vertical', 'Vertical Menu'), ('Horizontal', 'Horizontal Menu')],
                                    string="Menu Selection Options", default='Horizontal')
    color_options = fields.Selection([('user', 'User Specific'), ('company', 'Company Specific')],
                                     string="Color Selection Options", default='user')

    login_bg_image = fields.Binary(string="Log In Page Background Image",
                                   readonly=False, store=True)
    show_company_logo = fields.Boolean(string='Show Company Logo', store = True,
                                       help="To display Default Company logo on header.")
    dummy_field = fields.Html('to load wysiwyg assets')

    # @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        config_param = self.env['ir.config_parameter']
        config_param.sudo().set_param('menu_options', self.menu_options)
        config_param.sudo().set_param('color_options', self.color_options)
        config_param.sudo().set_param('background_image', self.background_image)
        config_param.sudo().set_param('login_bg_image', self.login_bg_image)
        config_param.sudo().set_param('show_company_logo', self.show_company_logo)
        company_id = self.company_id.id
        user_id = self.env.user.id
        view = self.env['ir.ui.view']
        current_color_mode = 'light'
        color_selected_option = self.env['ir.config_parameter'].sudo().get_param('color_options')
        current_color_mode_view = self.env['ks.color.mode'].search([('ks_user_id', '=', user_id)])
        if current_color_mode_view:
            current_color_mode = current_color_mode_view[0].sudo().current_color_mode
        if current_color_mode == 'light':
            if color_selected_option == 'company':
                all_template = view.search(
                    [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                for view in all_template:
                    view.sudo().write({
                        'active': False
                    })
                current_active_color_view = self.env['ks.color.company'].search([('ks_company_id', '=', company_id)])
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
                current_active_color_view = self.env['ks.home.view'].search([('ks_user_id', '=', user_id)])
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

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter']
        menu_options = params.sudo().get_param('menu_options')
        color_options = params.sudo().get_param('color_options')
        background_image = params.sudo().get_param('background_image')
        login_bg_image = params.sudo().get_param('login_bg_image')
        show_company_logo = params.sudo().get_param('show_company_logo')
        if not menu_options:
            menu_options = 'Horizontal'
            params.sudo().set_param('menu_options', menu_options)
        if not color_options:
            color_options = 'user'
            params.sudo().set_param('color_options', color_options)
        res.update({
            'menu_options': menu_options,
            'color_options': color_options,
            'background_image': background_image,
            'login_bg_image': login_bg_image,
            'show_company_logo': show_company_logo,
        })
        return res


class KsHomeScreenView(models.Model):
    _name = 'ks.home.view'
    _description = 'This is for user specific color palette of kernel backend theme'

    current_font_id = fields.Char(string="Current Active Font Id")
    current_color_id = fields.Char(string="Current Active Color Id")
    ks_user_id = fields.Many2one("res.users")

    def ks_get_value(self):
        user_id = self.env.user.id
        access = self.user_has_groups('ks_theme_kernel.ks_theme_kernel_settings')
        adv_access = self.user_has_groups('ks_theme_kernel.ks_theme_kernel_adv_settings')
        menu_options = self.env['ir.config_parameter'].sudo().get_param('menu_options')
        show_company_logo = self.env['ir.config_parameter'].sudo().get_param('show_company_logo')
        color_mode_view = self.env['ks.color.mode'].search([('ks_user_id', '=', user_id)])
        if color_mode_view:
            color_modes = color_mode_view[0].sudo().current_color_mode
        else:
            color_modes = 'light'
        return [menu_options, access, color_modes, show_company_logo, adv_access]


class KsColorCompanySpecific(models.Model):
    _name = 'ks.color.company'
    _description = 'This is for company specific color palette of kernel backend theme'

    current_font_id = fields.Char(string="Current Active Font Id")
    current_color_id = fields.Char(string="Current Active Color Id")
    ks_company_id = fields.Many2one("res.company")


class KsColorMode(models.Model):
    _name = 'ks.color.mode'
    _description = 'This is for user specific dark of kernel backend theme'

    current_color_mode = fields.Char(string="Current Active Color Mode")
    ks_user_id = fields.Many2one("res.users")


class KsFavouriteMenu(models.Model):
    _name = 'ks.favourite.menu'
    _description = 'This for store the name and url of favourite menu with respect to user'

    ks_menu_name = fields.Char(string="Menu Name")
    ks_menu_url = fields.Char(string="Menu Url")
    ks_res_user_id = fields.Many2one("res.users")


class KsIrUiView(models.Model):
    _inherit = 'ir.ui.view'

    ks_user_id = fields.Many2one("res.users")
    ks_company_id = fields.Many2one("res.company")


class KsResUser(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        res = super(KsResUser, self).write(vals)
        user_id = self[0].id
        if vals.get('company_id', False):
            company_id = vals['company_id']
            view = self.env['ir.ui.view']
            current_color_mode = 'light'
            color_selected_option = self.env['ir.config_parameter'].sudo().get_param('color_options')
            current_color_mode_view = self.env['ks.color.mode'].search([('ks_user_id', '=', user_id)])
            if current_color_mode_view:
                current_color_mode = current_color_mode_view[0].sudo().current_color_mode
            if current_color_mode == 'light':
                if color_selected_option == 'company':
                    all_template = view.search(
                        [('key', 'like', 'ks_theme_kernel.backend_color_'), ('active', '=', True)])
                    for view in all_template:
                        view.sudo().write({
                            'active': False
                        })
                    current_active_color_view = self.env['ks.color.company'].search(
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

        return res
