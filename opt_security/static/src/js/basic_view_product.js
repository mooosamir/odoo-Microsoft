odoo.define('opt_security.BasicViewProduct', function (require) {
    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');

    BasicView.include({
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);
            var self = this;
            var model = self.controllerParams.modelName == 'product.product' || self.controllerParams.modelName == 'product.template' ? true : false;
            if(model) {
                session.user_has_group('opt_security.opt_products_import_export').then(function(has_group) {
                    if(!has_group){
                        self.controllerParams.importEnabled = false;
                        self.controllerParams.activeActions.export_xlsx = false;
                    }
                });
                session.user_has_group('opt_security.opt_products_archive').then(function(has_group) {
                    if(!has_group)
                        self.controllerParams.archiveEnabled = false;
                });
                session.user_has_group('opt_security.opt_products_duplicate').then(function(has_group) {
                    if(!has_group)
                        self.controllerParams.activeActions.duplicate = false;
                });
                session.user_has_group('opt_security.opt_products_synchronize').then(function(has_group) {
                    if(!has_group && self.fieldsView.toolbar.action != undefined){
                        var action = self.fieldsView.toolbar.action;
                        for (var i=0; i<action.length; i++){
                            if (action[i].name == 'synchronize'){
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