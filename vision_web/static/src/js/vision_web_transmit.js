odoo.define('vision_web.vision_web_transmit', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var vision_web_transmit = AbstractAction.extend({
        template: 'vision_web_transmit_wizard',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'click #vw_cancel': 'cancel_clicked',
        },
        start: function () {
            return this._super();
        },
        init: function(parent, args) {
            var self = this;
            this._super(parent, args);
            if ('id' in this.controlPanelParams.context)
                this.data_id = this.controlPanelParams.context.id;
            if ('ids' in this.controlPanelParams.context)
                this.data_id = this.controlPanelParams.context.ids;
            self.transmit_data();
            this.controlPanelParams.context.dialog_size = 'medium';
            this.controlPanelParams.context.renderFooter = false;
        },
        cancel_clicked: function(ev){
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window_close'
            })
        },
        transmit_data: function(ev){
            var self = this;
            self._rpc({model: 'vision.web', method: 'transmit_data', args : [[], this.data_id]})
                .then(function (response) {
                    $('.response')[0].innerHTML = response;
                    $('.response')[0].style['text-align'] = '';
                });
        },
    });

    core.action_registry.add("vision_web_transmit", vision_web_transmit);
    return vision_web_transmit;
});