odoo.define('opt_security.ListControllerInventory', function (require) {
    "use strict";

    var Sidebar = require('web.Sidebar');
    var ListController = require('web.ListController');
    var session = require('web.session');

    ListController.include({
        renderSidebar: function($node) {
            var self = this;
            this._super.apply(this, arguments);
            var model = self.modelName == 'stock.picking' ? true : false;
            if(model && self.sidebar != undefined) {
                session.user_has_group('opt_security.opt_inventory_import_export').then(function(has_group) {
                    if(!has_group && self.sidebar.items.other != undefined){
                        var action = self.sidebar.items.other;
                        for (var i=0; i<action.length; i++)
                            if (action[i].label == 'Export'){
                                self.sidebar.items.other.splice(i, 1);
                                break;
                            }
                    }
                    if(!has_group && self.sidebar.options.actions.other != undefined){
                        var action = self.sidebar.options.actions.other;
                        for (var i=0; i<action.length; i++)
                            if (action[i].label == 'Export'){
                                self.sidebar.options.actions.other.splice(i, 1);
                                break;
                            }
                    }
                    if(!has_group && self.toolbarActions.other != undefined){
                        var action = self.toolbarActions.other;
                        for (var i=0; i<action.length; i++)
                            if (action[i].label == 'Export'){
                                self.toolbarActions.other.splice(i, 1);
                                break;
                            }
                    }
                });
            }
        },
    });
});