odoo.define('opt_appointment.DashboardView', function (require) {
    "use strict";

    var AbstractView = require('web.AbstractView');
    var core = require('web.core');
    var config = require('web.config');
    var ResourceViewModel = require('opt_appointment.ResourceViewModel');
    var ResourceViewRenderer = require('opt_appointment.ResourceViewRenderer');
    var ResourceViewController = require('opt_appointment.ResourceViewController');

    var _lt = core._lt;

    var ResourceView = AbstractView.extend({
        display_name: _lt('Schedule Events'),
        icon: 'fa fa-calendar-plus-o',
        jsLibs: ['/opt_appointment/static/src/lib/fullcalendar.js',
                '/opt_appointment/static/src/lib/scheduler.js',
                ],//'/opt_appointment/static/src/lib/main.min.js'
        cssLibs: ['/opt_appointment/static/src/css/fullcalendar.css',
                    '/opt_appointment/static/src/css/scheduler.css',
                    ],//'/opt_appointment/static/src/css/main.min.css'
        config: _.extend({}, AbstractView.prototype.config, {
            Model: ResourceViewModel,
            Renderer: ResourceViewRenderer,
            Controller: ResourceViewController,
        }),
        viewType: 'dashboard',
        searchMenuTypes: ['filter', 'favorite'],
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            var arch = this.arch;
            var fields = this.fields;
            var attrs = arch.attrs;
        },
    });

    return ResourceView;

});
