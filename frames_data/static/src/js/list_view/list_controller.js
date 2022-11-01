odoo.define('frames_data.ListController', function (require) {
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
                self.$buttons.on('click', '.frames_data_import_client_action', function () {
                    self.frames_data_import_client_action(this);
                });
            return rec
        },
        frames_data_import_client_action: function (to) {
            this.do_action({
                tag: 'frames_data_import',
                target: 'current',
                type: 'ir.actions.client',
            });
        },

    });

});