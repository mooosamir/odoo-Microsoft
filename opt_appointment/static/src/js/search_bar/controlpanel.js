odoo.define('opt_appointment.ControlPanelRenderer', function (require) {
"use strict";

    var ControlPanelRenderer = require('web.ControlPanelRenderer');

    ControlPanelRenderer.include({
        init: function (parent, state, params) {
            if (params.action.xml_id == 'opt_appointment.action_calendar_event_appointment'){
                for(var i=0; i<params.searchMenuTypes.length; i++){
                    if(params.searchMenuTypes[i] == "favorite"){
                        params.searchMenuTypes.splice(i);
                        break;
                    }
                }
                params.withSearchBar = false;
            }
            this._super.apply(this, arguments);
        },
        _renderBreadcrumbs: function () {
            var self = this;
            var breadcrumbsDescriptors = this._breadcrumbs.concat({title: this._title});
            var breadcrumbs = breadcrumbsDescriptors.map(function (bc, index) {
                return self._renderBreadcrumbsItem(bc, index, breadcrumbsDescriptors.length);
            });
            if (self.action.xml_id == 'opt_appointment.action_calendar_event_appointment')
                breadcrumbs[0][0].style.maxWidth = "fit-content";
            this.$('.breadcrumb').html(breadcrumbs);
        },
    });

});