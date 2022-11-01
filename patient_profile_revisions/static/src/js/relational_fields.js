odoo.define('patient_profile_revisions.relational_fields', function (require) {
"use strict";

    var RelationalFields = require('web.relational_fields');
    var FieldMany2One = RelationalFields.FieldMany2One;
    var ViewDialogs = require('web.view_dialogs');
    var dialogs = require('web.view_dialogs');
    var dom = require('web.dom');

    FieldMany2One.include({
        _searchCreatePopupCustom: function (view, ids, context, dynamicFilters, buttons, no_create, on_selected) {
            var self = this;
            var options = this._getSearchCreatePopupOptions(view, ids, context, dynamicFilters);
            if (self.record._domains != undefined)
                if (self.attrs.context.includes("opt_custom.view_patent_profile_form") && self.string == "Patient" && self.search_required){
                    options.domain = self.record._domains['patient_id'];
                    options.buttons = buttons;
                    options.no_create = no_create;
                    options.on_selected = on_selected;
                    options.title = 'Duplicate: Patient';
                }
           return new ViewDialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, options)).open();
        },
        _onFieldChanged: function (event) {
            var self = this;
            if (self.name == "soft_manufacturer_id" && self.mode == "edit" && self.model == "spec.contact.lenses" && self.formatType == "many2one" && self.viewType == "form"){
//                return self._rpc({
//                    "model": 'spec.contact.lenses',
//                    "method": "show_manufacturer_options_wizard",
//                    "args": [[] , event.data.changes[Object.keys(event.data.changes)[0]].id]
//                })
//                .then(function(result) {
                self.__parentedParent.is_custom_parent = true;
                self.__parentedParent.custom_context = 'soft_manufacturer_id';
                return new ViewDialogs.SelectCreateDialog(self, {
                    res_model: 'manufacturer.options.wizard',
                    context: {
                        'default_product_template_id': event.data.changes[Object.keys(event.data.changes)[0]].id,
                        'form_view_ref': 'patient_profile_revisions.manufacturer_options_wizard_form',
                    },
                    title: "Manufacturer & Brand",
                    initial_view: "form",
                }).open();
//                });
             }
            if (self.name == "soft_left_manufacturer_id" && self.mode == "edit" && self.model == "spec.contact.lenses" && self.formatType == "many2one" && self.viewType == "form"){
//                return self._rpc({
//                    "model": 'spec.contact.lenses',
//                    "method": "show_manufacturer_options_wizard",
//                    "args": [[] , event.data.changes[Object.keys(event.data.changes)[0]].id]
//                })
//                .then(function(result) {
                self.__parentedParent.is_custom_parent = true;
                self.__parentedParent.custom_context = 'soft_left_manufacturer_id';
                return new ViewDialogs.SelectCreateDialog(self, {
                    res_model: 'manufacturer.options.wizard',
                    context: {
                        'default_product_template_id': event.data.changes[Object.keys(event.data.changes)[0]].id,
                        'form_view_ref': 'patient_profile_revisions.manufacturer_options_wizard_form',
                    },
                    title: "Manufacturer & Brand",
                    initial_view: "form",
                }).open();
//                });
             }

            this.lastChangeEvent = event;
        },
   });

});