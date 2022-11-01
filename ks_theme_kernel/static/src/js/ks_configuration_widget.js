odoo.define('ks_theme_kernel.ks_configuration_widget', function (require) {
"use strict";

var config = require('web.config');
var ajax   = require('web.ajax');
var core = require('web.core');
var dom = require('web.dom');
var Widget = require('web.Widget');
var QWeb = core.qweb;
var _t = core._t;

ajax.loadXML('/ks_theme_kernel/static/src/xml/ks_configuration.xml',QWeb)

var KsMenu = Widget.extend({
     template: 'KsThemeConfiguration',
      init: function () {
        var self = this;
        this._super.apply(this, arguments);
        },

        willStart: function () {
             this._super.apply(this, arguments);
             var ks_template_file=ajax.loadXML('/ks_theme_kernel/static/src/xml/ks_configuration.xml',QWeb)
             return $.when(ks_template_file);
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments);
         },

//      _render: function () {
//        var self = this;
//        return this._super.apply(this, arguments);
//        this.$el.append(qweb.render('ks_theme_configuration'));
//
//    },

    });
return KsMenu;
});