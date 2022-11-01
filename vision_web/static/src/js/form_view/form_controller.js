odoo.define('vision_web.FormController', function (require) {
"use strict";

    var core = require('web.core');
    var config = require('web.config');
    var _t = core._t;
    var qweb = core.qweb;

    var FormController = require('web.FormController');

    FormController.include({
       renderButtons: function ($node) {
            var self = this;
            var rec = this._super($node)
            if (self.$buttons)
                self.$buttons.on('click', '.vision_web_transmit_client_action', function () {
                    self.vision_web_transmit_client_action(this);
                });
            return rec
       },
       vision_web_transmit_client_action: function (to) {
            var id = 0;
            if (this.model.localData[this.handle] != undefined && 'res_id' in this.model.localData[this.handle])
                id = this.model.localData[this.handle].res_id;
            else
                id = this.initialState.data.id;
            this.do_action({
                tag: 'vision_web_transmit',
                target: 'new',
                type: 'ir.actions.client',
                name: 'Transmit: Vision Web',
                display_name: 'Transmit: Vision Web',
                context: {'id': [id]}
            });
       },

    });

});