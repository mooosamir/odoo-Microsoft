odoo.define('ks_theme_kernel_corrections.ControlPanelRenderer', function (require) {
"use strict";

    var ControlPanelRenderer = require('web.ControlPanelRenderer');

    ControlPanelRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            if (params.action.xml_id == 'opt_appointment.action_calendar_event_appointment'){
                this.withSearchBar = true;
            }
        },
        _renderSearchBar: function () {
            this._super.apply(this, arguments);
            if (this.action.xml_id == 'opt_appointment.action_calendar_event_appointment'){
                if ($('.o_searchview_input_container').length >= 1){
                    $('.o_searchview_input_container').remove();
                }
            }
        },
    });

});