odoo.define('web_confirm_on_save.web_confirm_on_save', function (require) {
"use strict";

    var FormController = require('web.FormController');
    var AbstractView = require('web.AbstractView');
    var ViewDialogs = require('web.view_dialogs');
    var session = require('web.session');
    var Dialog = require('web.Dialog');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    AbstractView.include({
	
    	init: function (viewInfo, params) {
        	var self = this;
        	this._super.apply(this, arguments);
    	    var confirm =  this.arch.attrs.confirm ? this.arch.attrs.confirm : false;
        	var confirm_text =  this.arch.attrs.confirm_text ? this.arch.attrs.confirm_text : false;
        	var cancel_text =  this.arch.attrs.cancel_text ? this.arch.attrs.cancel_text : false;
    	    var alert =  this.arch.attrs.alert ? this.arch.attrs.alert : false;
        	self.controllerParams.activeActions.confirm = confirm;
        	self.controllerParams.activeActions.confirm_text = confirm_text;
    	    self.controllerParams.activeActions.cancel_text = cancel_text;
        	self.controllerParams.activeActions.alert = alert;
        },

    });

    FormController.include({

        _searchCreatePopup: function (view, ids, context, dynamicFilters) {
            var options = this._getSearchCreatePopupOptions(view, ids, context, dynamicFilters);
            return new ViewDialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, options)).open();
        },

        _getSearchCreatePopupOptions: function(view, ids, context, dynamicFilters) {
            var self = this;
		    var record = self.model.get(self.handle, {raw: true});
    		var records = record ? record.data : false;
    		var confirm_text = self.activeActions.confirm_text;

            var domain = [];
            domain.push(['patient', '=', true]);
            domain.push(['first_name', '=', records['first_name']]);
            domain.push(['last_name', '=', records['last_name']]);
            domain.push(['date_of_birth', '=', records['date_of_birth']]);

            return {
                buttons: {
                    text: confirm_text,
                    classes: 'btn-primary ',
                    close: true,
                    click: function() {
        			    self._disableButtons();
	            		self.saveRecord().then(self._enableButtons.bind(self)).guardedCatch(self._enableButtons.bind(self));
                    }
                },
                res_model: self.modelName,
                domain: domain,
                context: _.extend({}, self.initialState.getContext(), context || {}),
                dynamicFilters: dynamicFilters || [],
                title: _t("Duplicate: ") + 'Patient',
                initial_ids: ids,
                initial_view: view,
                disable_multiple_selection: true,
                no_create: true,
                kanban_view_ref: undefined,
                on_selected: function (records) {
                    return self._rpc({
                        "model": 'res.partner',
                        "method": "patients_list",
                        "args": [[] , records[0].id]
                    })
                    .then(function(result) {
                        self.model.localData[self.handle]._isDirty = false;
                        return self.do_action(result);
                    });
// Open in default form, not current form
//                    this.do_action({
//                        type: 'ir.actions.act_window',
//                        res_model: "res.partner",
//                        res_id: records[0].id,
//                        views: [[false, 'form']],
//                        target: 'current'
//                    });
                },
            }
        },

    	check_condition: function (modelName, record_id ,data_changed) {
            var def = this._rpc({
                "model": modelName,
                "method": "check_condition_show_dialog",
                "args": [record_id ,data_changed]
            });
            return def;
        },
	
    	checkCanBeSaved: function (recordID) {
            var fieldNames = this.renderer.canBeSaved(recordID || this.handle);
            if (fieldNames.length) {
                return false;
            }
            return true;
        },
	
    // Dialog box on save button of form only, (not form many2one)
	    _onSave: function (ev) {
    		var self = this;
	    	var modelName = self.modelName ? self.modelName : false;
		    var record = self.model.get(self.handle, {raw: true});
    		var data_changed = record ? record.data : false;
	    	var record_id = data_changed && data_changed.id ? data_changed.id : false;
		    var confirm = self.activeActions.confirm;
    		var confirm_text = self.activeActions.confirm_text;
	    	var cancel_text = self.activeActions.cancel_text;
		    var alert =  self.activeActions.alert;
    		var canBeSaved = record && record.id ? self.checkCanBeSaved(record.id) : false;
	    	function saveAndExecuteAction () {
		    	ev.stopPropagation(); // Prevent x2m lines to be auto-saved
			    self._disableButtons();
	    		self.saveRecord().then(self._enableButtons.bind(self)).guardedCatch(self._enableButtons.bind(self));
    	    }
		    function cancelAction () {
    		    if (modelName == 'res.partner'){
                    self._searchCreatePopup("search", false, {}, undefined);
                }
    	    }
	    	if(canBeSaved && modelName && (confirm || alert)){
		    	self.check_condition(modelName, record_id, data_changed).then(function(opendialog){
	            	if(!opendialog){
	        	    	saveAndExecuteAction();
    	        	}else{
	            		if(confirm){
	            		    cancelAction();
//	            			var def = new Promise(function (resolve, reject) {
//	            	            Dialog.confirm(self, confirm, {
//	        	                    confirm_callback: saveAndExecuteAction,
//        		                    cancel_callback: cancelAction,
//        		                    confirm_text: confirm_text,
//        		                    cancel_text: cancel_text,
//	            	            }).on("closed", null, resolve);
//	            	        });
    	        		}else{
        	    			var def = new Promise(function (resolve, reject) {
        		                Dialog.alert(self, alert, {
        		                    confirm_callback: saveAndExecuteAction,
        		                }).on("closed", null, resolve);
            		        });
	            			saveAndExecuteAction();
	            		}
	            	}
    	        });
	    	}else{
		    	saveAndExecuteAction();
    		}
	    },

    });

});
