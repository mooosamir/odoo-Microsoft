odoo.define('ks_theme_kernel.FormController', function (require) {
"use strict";
var FormController = require('web.FormController');
var FormRenderer = require('web.FormRenderer');

FormRenderer.include({
    events: _.extend({}, FormRenderer.prototype.events, {
        'dblclick .o_form_sheet_bg': '_onFormviewDblClick',
    }),
    _onFormviewDblClick: function (ev) {
        var $target = $(ev.target);
        // Ignore in case of modal or chatter (Commnted as added o_form_sheet_bg)
         //if ($target.parents('.modal').length || $target.parents('.o_chatter').length || $target.is('.o_chatter')) {
         //    return;
         //}
         //else
         if(this.mode == 'readonly' && !$target.is('.o_form_label, .o_field_widget')){
            this.trigger_up('ks_edit_mode');
        }
    },
});

FormController.include({
    custom_events: _.extend({}, FormController.prototype.custom_events, {
        ks_edit_mode: '_onEditMode',
    }),
    _onEditMode: function (ev) {
        if (this.is_action_enabled('edit')) {
            this._setMode('edit');
        }
    },
});
});