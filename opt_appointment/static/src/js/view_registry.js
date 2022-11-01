odoo.define('web.view_registry2', function (require) {
    "use strict";

    var view_registry = require('web.view_registry');
    var DashboardView = require('opt_appointment.DashboardView');
    view_registry.add('dashboard', DashboardView);

});
