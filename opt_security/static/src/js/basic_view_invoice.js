odoo.define('opt_security.BasicViewInvoice', function (require) {
    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');

    BasicView.include({
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);
            var self = this;
            var model = self.controllerParams.modelName == 'account.move' ? true : false;
            if(model) {
                session.user_has_group('opt_security.opt_invoices_generate_payment_link').then(function(has_group) {
                    if(!has_group && self.fieldsView.toolbar.action != undefined){
                        var action = self.fieldsView.toolbar.action;
                        for (var i=0; i<action.length; i++){
                            if (action[i].name == 'Generate a Payment Link'){
                                self.fieldsView.toolbar.action.splice(i, 1);
                                break;
                            }
                        }
                    }
                });
                session.user_has_group('opt_security.opt_invoices_share').then(function(has_group) {
                    if(!has_group && self.fieldsView.toolbar.action != undefined){
                        var action = self.fieldsView.toolbar.action;
                        for (var i=0; i<action.length; i++){
                            if (action[i].name == 'Share'){
                                self.fieldsView.toolbar.action.splice(i, 1);
                                break;
                            }
                        }
                    }
                });
            }
        },
    });
});