odoo.define('ks_theme_backend.ksMenu', function (require) {
"use strict";

    var KsAppsMenu = require('web.AppsMenu');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var SystrayMenu = require('web.SystrayMenu');
    var UserMenu = require('web.UserMenu');
    var Widget = require('web.Widget');
    var KsMenu = require('web.Menu');
    var WebClient = require('web.WebClient');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var QWeb = core.qweb;
    var self;

    return KsMenu.include({
        willStart: function () {
            this._super.apply(this, arguments);
            var self = this;
            self.ks_theme_settings = false;
            self.ks_company_logo = false;
            self.ks_horizontal_menu = false;
            var def = this._rpc({
                model : 'ks.home.view',
                method : 'ks_get_value',
                args : [[]],
            }).then(function(ks_plane){
                if(ks_plane[1]){
                    self.ks_theme_settings = true;
                }
                if(ks_plane[3]){
                    self.ks_company_logo = true;
                }
                if(ks_plane[0] == 'Horizontal'){
                    self.ks_horizontal_menu = true;
                }
            });
            return $.when(def);
        },

        init: function (parent, menu_data) {
            self = this;
            var res = self._super.apply(this, arguments);
            self.ks_plane = rpc.query({
                model : 'ks.home.view',
                method : 'ks_get_value',
                args : [[]],
            }).then(function(ks_plane){
                if(ks_plane[0] == 'Vertical'){
                    $('.ks_sidebar_position').addClass('ks-vertical-menu-selected');
                    $('.o_main_navbar .o_menu_brand').addClass('d-none');
                    $('.o_main_navbar .o_menu_sections').addClass('d-none');
                }
                else{
                    $('.ks_sidebar_position').removeClass('ks-vertical-menu-selected');
                }
            });
            self.comp_id = session.company_id;
            self.company_name = session.user_companies.current_company[1];
        },

        start: function () {
            var self = this;
            //  this._super.apply(this, arguments);
            this.$menu_apps = $('.o_menu_apps');
            if ($('.sidebar-sub-menu').length){
                this.$menu_brand_placeholder = $('.o_menu_brand');
                this.$section_placeholder = $('.o_menu_sections');
            }
            else{
                this.$menu_brand_placeholder = this.$('.o_menu_brand');
                this.$section_placeholder = this.$('.o_menu_sections');
            }

            // Navbar's menus event handlers
            var on_secondary_menu_click = function (ev) {
                ev.preventDefault();
                var menu_id = $(ev.currentTarget).data('menu');
                var action_id = $(ev.currentTarget).data('action-id');
                self._on_secondary_menu_click(menu_id, action_id);
            };
            var menu_ids = _.keys(this.$menu_sections);
            var primary_menu_id, $section;
            for (var i = 0; i < menu_ids.length; i++) {
                primary_menu_id = menu_ids[i];
                $section = this.$menu_sections[primary_menu_id];
                $section.on('click', 'a[data-menu]', self, on_secondary_menu_click.bind(this));
            }

            // Apps Menu
            this._appsMenu = new KsAppsMenu(self, this.menu_data);
            var appsMenuProm = this._appsMenu.appendTo(this.$menu_apps);

            // Systray Menu
            this.systray_menu = new SystrayMenu(this);

//            this.systray_menu.widgets.forEach(function (item, index, object) {
//                if (item.template == 'mail.systray.ActivityMenu')
//                    object.splice(index, 1);
//            });
//            this.systray_menu.__parentedChildren.forEach(function (item, index, object) {
//                if (item.template == 'mail.systray.ActivityMenu')
//                    object.splice(index, 1);
//            });

            var systrayMenuProm = this.systray_menu.attachTo($('.o_menu_systray')).then(function() {
                $('.o_menu_systray').find('.o_mail_systray_dropdown').parent().remove();

//                $('#sidebar').prepend($('li.o_switch_company_menu'))
//                $('#sidebar .o_user_menu').prepend($('li.o_switch_company_menu'))
//                ks-menu-systray o_menu_systray
                var company_view_li = document.createElement("li")
                company_view_li.classList.add('o_user_company_menu')
                var company_view = document.createElement("ul")
                company_view.classList.add('ks-menu-systray')
                company_view.classList.add('o_menu_systray')
                company_view.append($('li.o_switch_company_menu')[0])
                company_view_li.append(company_view)
                $('#sidebar').prepend(company_view_li)

                $('.ks-menu-systray .o_user_menu').remove();
                var bHeight = $('.app-sidebar-menu-bottom').outerHeight();
                var uHeight = $('.o_user_menu').outerHeight();
                $('.app-sidebar-menu').attr('style','max-height:calc(100% - '+ (bHeight + uHeight) + 'px)');
                $('.o_action_manager').append('<div class="ks_searchfilter_overlay ks_resize_window"></div>');
            });
            this._userMenu = new UserMenu(self);
            var userMenuProm = this._userMenu.prependTo($('.app-sidebar-menu'));
            return Promise.all([appsMenuProm, systrayMenuProm]);
        },
    })
});

odoo.define('ks_theme_backend.KsAppMenu', function (require) {
"use strict";

    var KsAppsMenu = require('web.AppsMenu');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var SystrayMenu = require('web.SystrayMenu');
    var UserMenu = require('web.UserMenu');
    var Widget = require('web.Widget');
    var WebClient = require('web.WebClient');
//    var Menu = require('web.Menu');

var QWeb = core.qweb;

return KsAppsMenu.include({
    template: 'AppsMenu',
    events: _.extend({
            "keydown .ks-search-input input": "_ks_search_values_movement",
            "input .ks-search-input input": "_ks_searchMenuListTime",
            "click .ks-menu-search-value": "_ks_searchValuesSelecter",
            "shown.bs.dropdown": "_onkssearchFocus",
            "hidden.bs.dropdown": "_kssearchResetvalues",
            "hide.bs.dropdown": "_kshideAppsMenuList",
        }, KsAppsMenu.prototype.events),

    init: function (parent, menuData) {
            this._super.apply(this, arguments);
            for (let n in this._apps) {
                this._apps[n].web_icon_data =
                    menuData.children[n].web_icon_data;
                this._apps[n].web_icon = menuData.children[n].web_icon;
            }

            this._ks_fuzzysearchableMenus = _.reduce(
                menuData.children,
                ks_GetReducedMenuData,
                {}
            );
            this._search_def = false;
        },

    start: function () {
            this.$search_container = this.$(".ks-search-container");
            this.$search_input = this.$(".ks-search-input input");
            this.$search_results = this.$(".ks-search-values");
            return this._super.apply(this, arguments);
        },

    _onAppsMenuItemClicked: function (ev) {
            this._super.apply(this, arguments);
            ev.preventDefault();
            $('.ks-app-loader').removeClass('d-none');
            setTimeout(function(){
                    $('.ks-main-app-dropdown ').addClass('show');

                },0)
            setTimeout(function(){
                    $('.ks-main-app-dropdown ').removeClass('show');
                    $('.ks-app-loader').addClass('d-none');
                },4000)
        },

    _ksmenuDetail: function (key) {
            var original = this._ks_fuzzysearchableMenus[key];
            return _.extend({
                action_id: parseInt(original.action.split(',')[1], 10),
            }, original);
        },

    _onkssearchFocus: function () {
            if (!config.device.isMobile) {
                this.$search_input.focus();
            }
        },
     _ks_searchMenuListTime: function () {
            this._ks_search_def = new Promise((resolve) => {
                setTimeout(resolve, 50);
            });
            this._ks_search_def.then(this._ks_search_MenusList.bind(this));
        },

    _kssearchResetvalues: function () {
            this.$search_container.removeClass("ks-find-values");
            this.$search_results.empty();
            this.$search_input.val("");
        },
     _ks_search_MenusList: function () {
            const query = this.$search_input.val();
            if (query === "") {
                this.$search_container.removeClass("ks-find-values");
                this.$search_results.empty();
                return;
            }
            var values = fuzzy.filter(
                  query,
                _.keys(this._ks_fuzzysearchableMenus),
                {
                    pre: "<b>",
                    post: "</b>",
                }
            );
            this.$search_container.toggleClass(
                "ks-find-values",
                Boolean(values.length)
            );
            this.$search_results.html(QWeb.render("ks_theme_backend.ks_menu_items_value",
                    { ks_values: values,
                      ks_menus: this,
                    }));
        },

     _ks_searchValuesSelecter: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            const $current_value = $(ev.currentTarget),
                text = $current_value.text().trim(),
                data = $current_value.data(),
                suffix = ~text.indexOf("/") ? "/" : "";
            this.trigger_up("menu_clicked", {
                action_id: data.actionId,
                id: data.menuId,
                previous_menu_id: data.parentId,
            });

            const ksapp = _.find(this._apps, function (_ksapp) {
                return text.indexOf(_ksapp.name + suffix) === 0;
            });
            core.bus.trigger("change_menu_section", ksapp.menuID);
            setTimeout(function() {
                         $('.ks-menu-apps').click();

					}, 2050);


        },

    _ks_search_values_movement: function (ev) {
            var all = this.$search_results.find(".ks-menu-search-value"),
                pre_focused = all.filter(".active") || $(all[0]);
            var offset = all.index(pre_focused),
                key = ev.key;
            if (!all.length) {
                return;
            }
            if (key === "Tab") {
                ev.preventDefault();
                key = ev.shiftKey ? "ArrowUp" : "ArrowDown";
            }
            switch (key) {
            case "Enter":
                pre_focused.click();
                break;
            case "ArrowUp":
                offset--;
                break;
            case "ArrowDown":
                offset++;
                break;
            default:
                return;
            }
            if (offset < 0) {
                offset = all.length + offset;
            } else if (offset >= all.length) {
                offset -= all.length;
            }

            const new_focused = $(all[offset]);
            pre_focused.removeClass("active");
            new_focused.addClass("active");
            this.$search_results.scrollTo(new_focused, {
                offset: {
                    top: this.$search_results.height() * -0.5,
                },
            });
        },

    _kshideAppsMenuList: function (ev) {
            return  !this.$('input').is(':focus');
        },

     })


    function ks_GetReducedMenuData (memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, ks_GetReducedMenuData, memo);
        }
        return memo;
    }
});