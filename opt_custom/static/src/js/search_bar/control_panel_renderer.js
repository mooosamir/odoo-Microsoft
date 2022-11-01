odoo.define('opt_custom.ControlPanelRenderer', function (require) {
"use strict";

    var ControlPanelRenderer = require('web.ControlPanelRenderer');

    ControlPanelRenderer.include({
        init: function (parent, state, params) {
//            if (params.action.xml_id == 'opt_custom.patient_profile_action' || params.context.form_view_ref == "opt_custom.view_patent_profile_form")
////            if (params.action.xml_id == 'opt_custom.patient_profile_action' && params.action.context.params.view_type == "list")
//                params.searchMenuTypes = [];
            this._super.apply(this, arguments);
        },
    });

});