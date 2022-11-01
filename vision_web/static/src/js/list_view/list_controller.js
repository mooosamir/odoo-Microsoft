odoo.define('vision_web.ListController', function (require) {
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
            if (self.$buttons){
                self.$buttons.on('click', '.vision_web_import_client_action', function () {
                    self.vision_web_import_client_action(this);
                });
                self.$buttons.on('click', '.vision_web_transmit_client_action', function () {
                    self.vision_web_transmit_client_action(this);
                });
            }
            return rec
       },
       vision_web_import_client_action: function (to) {
            this.do_action({
                tag: 'vision_web_import',
                target: 'new',
                type: 'ir.actions.client',
                name: 'Vision Web Import',
                display_name: 'Vision Web Import',
            });
       },
       vision_web_transmit_client_action: function (to) {
            var self = this;
            var records = [];
            var accepted_records = [];
            this.selectedRecords.forEach(function(x){
                if (x in self.model.localData){
                    records.push(self.model.localData[x].res_id)
                    if (self.model.localData[x].data.display_name && self.model.localData[x].data.display_name.includes('G'))
                        accepted_records.push(1)
                }
            })
            if (records.length !== accepted_records.length)
                this.do_warn("Error:","All selected records should have order type in ['Complete Pair', 'Lenses Only']");
            else
                this.do_action({
                    tag: 'vision_web_transmit',
                    target: 'new',
                    type: 'ir.actions.client',
                    name: 'Transmit: Vision Web',
                    display_name: 'Transmit: Vision Web',
                    context: {'ids': records}
                });
       },
    });

});