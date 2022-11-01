odoo.define('patient_profile_revisions.view_dialogs', function (require) {
"use strict";

    var ViewDialogs = require('web.view_dialogs');
    var FormViewDialog = ViewDialogs.FormViewDialog;
    var SelectCreateDialog = ViewDialogs.SelectCreateDialog;

    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var dom = require('web.dom');
    var rpc = require('web.rpc');
    var _t = core._t;

    FormViewDialog.include({
        _save: function () {
            var self = this;

            if (self.context.form_view_ref == "opt_custom.view_patent_profile_form"
                && self.res_model =="res.partner" && !self.Ok){
            		var confirm = self.form_view.activeActions.confirm;
		    		var confirm_text = self.form_view.activeActions.confirm_text;
    				var cancel_text = self.form_view.activeActions.cancel_text;
    				var modelName = self.form_view.modelName ? self.form_view.modelName : false;
		    		var record = self.form_view.model.get(self.form_view.handle, {raw: true})
	    			var data_changed = record ? record.data : false;
    				var record_id = data_changed && data_changed.id ? data_changed.id : false;
    				var search_required = self.__parentedParent.__parentedParent;

            		function saveAndExecuteAction () {
            		    self.Ok = true;
            		    self.buttons[0].click.call(self, '');
            	    }
            		function cancelAction () {
                        search_required.search_required = true;
//                        if (!this.__closed) {
//                            this.__closed = true;
//                            this.trigger('closed', undefined);
//                        }
                        if (!self.__closed) {
//                            self.__closed = true;
                            var records = self.form_view.model.get(self.form_view.handle, {raw: true}).data;
                            var domain = [];
                            domain.push(['patient', '=', true]);
                            domain.push(['first_name', '=', records['first_name']]);
                            domain.push(['last_name', '=', records['last_name']]);
                            domain.push(['date_of_birth', '=', records['date_of_birth']]);
                            search_required.record._domains = {'patient_id' : domain};
//                            self.trigger('closed', undefined);
                            var buttons = {
                                text: confirm_text,
                                classes: 'btn-primary ',
                                close: true,
                                click: saveAndExecuteAction,
                            }
                            var on_selected = function (records) {
                                search_required.reinitialize(records[0]);
                                if (!self.__closed) {
                                    self.__closed = true;
                                    self.trigger('closed', undefined);
                                }
                            }
                            search_required._searchCreatePopupCustom("search", false, {}, undefined, buttons,true, on_selected);
                        }
            	    }

                    self.form_view.check_condition(modelName, record_id, data_changed).then(function(opendialog){
        	        	if(!opendialog){
	                		saveAndExecuteAction();
	        	        }else{
    	        	        if(confirm){
    	        	            cancelAction();
        	        	    }
        	        	    else
    	                		saveAndExecuteAction();
        	        	}
    	        	});
            }
            else{
                return this._super.apply(this, arguments);
            }
        },

    });

    SelectCreateDialog.include({
        _prepareButtons: function () {
            this._super.apply(this, arguments);
            if (this.buttons && 'text' in this.buttons && this.buttons.text == 'continue adding the new patient profile') {
                this.__buttons.unshift(this.buttons);
            }
        },
    });
});