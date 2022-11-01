odoo.define('opt_security.BasicViewOrder', function (require) {
    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');

    BasicView.include({
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);
            var self = this;
            var model = self.controllerParams.modelName == 'sale.order' ? true : false;
            if(model) {
                session.user_has_group('opt_security.opt_order_send_cart_email').then(function(has_group) {
                    if(!has_group && self.fieldsView.toolbar.action != undefined){
                        var action = self.fieldsView.toolbar.action;
                        for (var i=0; i<action.length; i++){
                            if (action[i].name == 'Send a Cart Recovery Email'){
                                self.fieldsView.toolbar.action.splice(i, 1);
                                break;
                            }
                        }
                    }
                });
                session.user_has_group('opt_security.opt_order_export').then(function(has_group) {
                    if(!has_group){
                        self.controllerParams.activeActions.export_xlsx = false;
                    }
                });
            }
        },
    });
});