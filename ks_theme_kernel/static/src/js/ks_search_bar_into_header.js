odoo.define('ks_theme_backend.ksControlPanelRenderer', function (require) {
    "use strict";

    var KsControlPanelRenderer = require('web.ControlPanelRenderer');
    var config = require('web.config');
    var data = require('web.data');
    var FavoriteMenu = require('web.FavoriteMenu');
    var FilterMenu = require('web.FilterMenu');
    var GroupByMenu = require('web.GroupByMenu');
    var mvc = require('web.mvc');
    var SearchBar = require('web.SearchBar');
    var TimeRangeMenu = require('web.TimeRangeMenu');

var Renderer = mvc.Renderer;


return KsControlPanelRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            if (params.action.xml_id == 'opt_appointment.action_calendar_event_appointment'){
                this.withSearchBar = true;
            }
        },
     _renderSearchBar: function () {
        // TODO: might need a reload instead of a destroy/instantiate
        var self = this;
        this._super.apply(this, arguments);
        this.displaySearchMenu = false;
        if ($('.o_searchview_input_container').length){
            if ($('.o_searchview_input_container').parents('.modal-body').length){
                $('.modal-body .o_searchview_input_container').remove();
            }
            else{
                $('.o_searchview_input_container').remove();
            }
        }
        var oldSearchBar = this.searchBar;
        this.searchBar = new SearchBar(this, {
            context: this.context,
            facets: this.state.facets,
            fields: this.state.fields,
            filterFields: this.state.filterFields,
        });
        return this.searchBar.appendTo($('.o_main_navbar')).then(function () {
            if (self.action.xml_id == 'opt_appointment.action_calendar_event_appointment'){
                if ($('.o_searchview_input_container').length >= 1){
                    $('.o_searchview_input_container').remove();
                }
            }
//             if (oldSearchBar) {
//                 oldSearchBar.destroy();
//             }
        });
    },

     _onMore: function () {
         if (!$('.ks_sidebar_position').hasClass('search-filter-open')){
            if ($('.ks_theme_layout').hasClass('ks-layout-open')){
                    $('.ks_configuration').click();
                    }
           }
         $('.ks_sidebar_position').removeClass('ks-generator-favourite-menu-opened');
         $('.ks_sidebar_position').removeClass('ks-generator-filter-menu-opened');
         $('.ks_sidebar_position').removeClass('ks-generator-groupby-menu-opened');
         if ($(this.el).parents('.modal-body').length){
              $(this.el).parentsUntil('.ks_sidebar_position').toggleClass('search-wizard-filter-open',!this.displaySearchMenu);
//            $('.ks_sidebar_position').toggleClass('search-wizard-filter-open',!this.displaySearchMenu);
         }
         else{
              $('.ks_sidebar_position').toggleClass('search-filter-open',!this.displaySearchMenu);
         }
           
        this.displaySearchMenu = !this.displaySearchMenu;
        this._setSearchMenusVisibility();
    },

 })

});

odoo.define('ks_theme_backend.ksFilterMenu', function (require) {
    "use strict";

    var KsFilterMenu = require('web.FilterMenu')
    var config = require('web.config');
    var core = require('web.core');
    var Domain = require('web.Domain');
    var DropdownMenu = require('web.DropdownMenu');
    var search_filters = require('web.search_filters');

    var _t = core._t;
    var QWeb = core.qweb;

    return KsFilterMenu.include({
        _renderGeneratorMenu: function () {
            $('.ks-filter-menu-generator').remove();
            $('.ks_sidebar_position').removeClass('ks-generator-filter-menu-opened');
                // this.$el.find('.ks-filter-menu-generator').remove();
            this._super.apply(this, arguments);
                // if (&& (!this.generatorMenuIsOpen && this.propositions.length){
            if ($('.ks-filter-menu-generator').length){
                $('.ks_sidebar_position').removeClass('ks-generator-groupby-menu-opened')
                $('.ks_sidebar_position').removeClass('ks-generator-favourite-menu-opened')
                $('.ks_sidebar_position').toggleClass('ks-generator-filter-menu-opened');
            }
        },
    })

});

odoo.define('ks_theme_backend.ksGroupByMenu', function (require) {
    "use strict";

    var KsGroupByMenu = require('web.GroupByMenu')
    var config = require('web.config');
    var core = require('web.core');
    var Domain = require('web.Domain');
    var DropdownMenu = require('web.DropdownMenu');
    var search_filters = require('web.search_filters');
    var controlPanelViewParameters = require('web.controlPanelViewParameters');

    var _t = core._t;
    var QWeb = core.qweb;

    return KsGroupByMenu.include({
        _renderGeneratorMenu: function () {
            $('.ks-groupby-menu-generator').remove();
            $('.ks_sidebar_position').removeClass('ks-generator-groupby-menu-opened');
            this._super.apply(this, arguments);
            if ($('.ks-groupby-menu-generator').length){
                $('.ks_sidebar_position').removeClass('ks-generator-favourite-menu-opened')
                $('.ks_sidebar_position').removeClass('ks-generator-filter-menu-opened')
                $('.ks_sidebar_position').toggleClass('ks-generator-groupby-menu-opened');
            }
        },
    })

});


odoo.define('ks_theme_backend.ksFavoriteSearchMenu', function (require) {
    "use strict";

    var core = require('web.core');
    var ksFavoriteSearchMenu = require('web.AddNewFavoriteMenu');
    var favoritesSubmenusRegistry = require('web.favorites_submenus_registry');
    var Widget = require('web.Widget');
    var _t = core._t;

    return ksFavoriteSearchMenu.include({

          _onMenuHeaderClick: function (ev) {
                this._super.apply(this, arguments);
                $('.ks_sidebar_position').removeClass('ks-generator-groupby-menu-opened')
                $('.ks_sidebar_position').removeClass('ks-generator-filter-menu-opened')
                $('.ks_sidebar_position').toggleClass('ks-generator-favourite-menu-opened');

          },
    })
});