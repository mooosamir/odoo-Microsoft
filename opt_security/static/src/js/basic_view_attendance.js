odoo.define('opt_security.BasicViewAttendance', function (require) {
    "use strict";

    var session = require('web.session');
    var BasicView = require('web.BasicView');

    BasicView.include({
        init: function(viewInfo, params) {
            this._super.apply(this, arguments);
            var self = this;
            var model = self.controllerParams.modelName == 'hr.attendance' ? true : false;
            if(model) {
                session.user_has_group('opt_security.opt_attendance_import').then(function(has_group) {
                    if(!has_group){
                        self.controllerParams.importEnabled = false;
                    }
                });
                session.user_has_group('opt_security.opt_attendance_export').then(function(has_group) {
                    if(!has_group){
                        self.controllerParams.activeActions.export_xlsx = false;
                    }
                });
            }
        },
    });
});