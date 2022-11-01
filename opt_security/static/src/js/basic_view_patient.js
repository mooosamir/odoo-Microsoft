odoo.define('opt_security.BasicViewPatient', function (require) {
    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');

    BasicView.include({
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);
            var self = this;
            var model = self.controllerParams.modelName == 'res.partner' ? true : false;
            if(model) {
                session.user_has_group('opt_security.opt_patient_archive').then(function(has_group) {
                    if(!has_group)
                        self.controllerParams.archiveEnabled = false;
                });
                session.user_has_group('opt_security.opt_patient_duplicate').then(function(has_group) {
                    if(!has_group)
                        self.controllerParams.activeActions.duplicate = false;
                });
                session.user_has_group('opt_security.opt_patient_portal_access').then(function(has_group) {
                    if(!has_group && self.controllerParams.toolbarActions != undefined){
                        var action = self.controllerParams.toolbarActions.action;
                        for (var i=0; i<action.length; i++){
                            if (action[i].name == 'Grant portal access'){
                                self.controllerParams.toolbarActions.action.splice(i, 1);
                                break;
                            }
                        }
                    }
                });
                session.user_has_group('opt_security.opt_patient_send_text_message').then(function(has_group) {
                    if(!has_group && self.controllerParams.toolbarActions != undefined){
                        var action = self.controllerParams.toolbarActions.action;
                        for (var i=0; i<action.length; i++){
                            if (action[i].name == 'Send SMS Text Message'){
                                self.controllerParams.toolbarActions.action.splice(i, 1);
                                break;
                            }
                        }
                    }
                });
                session.user_has_group('opt_security.opt_patient_import').then(function(has_group) {
                    if(!has_group)
                        self.controllerParams.importEnabled = false;
                });
            }
        },
    });
});