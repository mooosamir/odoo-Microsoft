odoo.define('contact_lens_import.ListController', function (require) {
"use strict";

    var core = require('web.core');
    var config = require('web.config');
    var _t = core._t;
    var qweb = core.qweb;

    var ListController = require('web.ListController');

    ListController.include({
       renderButtons: function ($node) {
            var self = this;
            var rec = this._super($node)
            if (self.$buttons)
                self.$buttons.on('click', '.contact_lens_import_client_action', function () {
                    self.contact_lens_import_client_action(this);
                });
            return rec
       },
       contact_lens_import_client_action: function (to) {
            this.do_action({
                tag: 'contact_lens_import',
                target: 'new',
                type: 'ir.actions.client',
                name: 'Contact Lens Import',
                display_name: 'Contact Lens Import',
            });
       },

    });

});