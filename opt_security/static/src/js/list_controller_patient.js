odoo.define('opt_security.ListControllerPatient', function (require) {
    "use strict";

    var Sidebar = require('web.Sidebar');
    var ListController = require('web.ListController');
    var session = require('web.session');

    ListController.include({
        renderSidebar: function($node) {
            var self = this;
            this._super.apply(this, arguments);
            var model = self.modelName == 'res.partner' ? true : false;
            if(model && self.sidebar != undefined) {
                session.user_has_group('opt_security.opt_patient_merge_patients').then(function(has_group) {
                    if(!has_group && self.sidebar.items.other != undefined){
                        var action = self.sidebar.items.other;
                        for (var i=0; i<action.length; i++)
                            if (action[i].label == 'Merge'){
                                self.sidebar.items.other.splice(i, 1);
                                break;
                            }
                    }
                    if(!has_group && self.sidebar.options.actions.action != undefined){
                        var action = self.sidebar.options.actions.action;
                        for (var i=0; i<action.length; i++)
                            if (action[i].name == 'Merge'){
                                self.sidebar.options.actions.action.splice(i, 1);
                                break;
                            }
                    }
                });
            }
        },
    });
});