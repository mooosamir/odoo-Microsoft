odoo.define('opt_custom.abstract_field_change.add_calculation_o2m', function (require) {
    "use strict";

    var BasicModel = require('web.BasicModel');
    var core = require('web.core');
    var view_dialogs = require('web.view_dialogs');
    var ListRenderer = require('web.ListRenderer');
    var viewUtils = require('web.viewUtils');

    var _t = core._t;

    BasicModel.include({
        _generateChanges: function (record, options) {
            options = options || {};
            var viewType = options.viewType || record.viewType;
            var changes;
            if ('changesOnly' in options && !options.changesOnly) {
                changes = _.extend({}, record.data, record._changes);
            } else {
                changes = _.extend({}, record._changes);
            }
            var withReadonly = options.withReadonly || false;
            var commands = this._generateX2ManyCommands(record, {
                changesOnly: 'changesOnly' in options ? options.changesOnly : true,
                withReadonly: withReadonly,
            });
            for (var fieldName in record.fields) {
                // remove readonly fields from the list of changes
                if (!withReadonly && fieldName in changes || fieldName in commands) {
                    var editionViewType = record._editionViewType[fieldName] || viewType;
                    if (this._isFieldProtected(record, fieldName, editionViewType)) {
                        delete changes[fieldName];
                        continue;
                    }
                }
                // process relational fields and handle the null case
                var type = record.fields[fieldName].type;
                var value;
                if (type === 'one2many' || type === 'many2many') {
                    if (commands[fieldName] && commands[fieldName].length) { // replace localId by commands
                        _.each(commands[fieldName], function(rec){
                            if(rec && localStorage.getItem(rec[1]) == 'new_record'){
                                rec[2]['new_record'] = true
                            }
                        })
                        changes[fieldName] = commands[fieldName];
                    } else { // no command -> no change for that field
                        delete changes[fieldName];
                    }
                } else if (type === 'many2one' && fieldName in changes) {
                    value = changes[fieldName];
                    changes[fieldName] = value ? this.localData[value].res_id : false;
                } else if (type === 'reference' && fieldName in changes) {
                    value = changes[fieldName];
                    changes[fieldName] = value ?
                        this.localData[value].model + ',' + this.localData[value].res_id :
                        false;
                } else if (type === 'char' && changes[fieldName] === '') {
                    changes[fieldName] = false;
                } else if (changes[fieldName] === null) {
                    changes[fieldName] = false;
                }
            }

            return changes;
        },
    });

    ListRenderer.include({
        _renderButton: function (record, node) {
            var self = this;
            var nodeWithoutWidth = Object.assign({}, node);
            delete nodeWithoutWidth.attrs.width;
            var $button = viewUtils.renderButtonFromNode(nodeWithoutWidth, {
                extraClass: node.attrs.icon ? 'o_icon_button' : undefined,
                textAsTitle: !!node.attrs.icon,
            });
            this._handleAttributes($button, node);
            this._registerModifiers(node, record, $button);

            if (record.res_id) {
                // TODO this should be moved to a handler
                $button.on("click", function (e) {
                    e.stopPropagation();
                    self.trigger_up('button_clicked', {
                        attrs: node.attrs,
                        record: record,
                    });
                });
                if(record.data.new_record && localStorage.getItem('auto_click') == 'no_auto_click' && $button.hasClass('force_save_button')){
                    self.trigger_up('button_clicked', {
                        attrs: node.attrs,
                        record: record,
                    });
                    localStorage.setItem('auto_click', "auto_click");
                }else if(record.data.new_record && localStorage.getItem('auto_click2') == 'no_auto_click' && $button.hasClass('force_save_button2')){
                    localStorage.setItem('auto_click2', "auto_click");
                    self.trigger_up('button_clicked', {
                        attrs: node.attrs,
                        record: record,
                    });
                }
            } else {
                if (node.attrs.options.warn) {
                    $button.on("click", function (e) {
                        e.stopPropagation();
                        self.do_warn(_t("Warning"), _t('Please click on the "save" button first.'));
                    });
                } else {
                    if($button.hasClass('force_save_dummy_button')){
                        $button.on("click", function (e) {
                            e.stopPropagation();
                            localStorage.setItem(record.ref, "new_record");
                            localStorage.setItem('auto_click', 'no_auto_click');
                            self.trigger_up('button_clicked', {
                                attrs: node.attrs,
                                record: record,
                            });
                        });
                    }
                    else if ($button.hasClass('force_save_button')) {
                        $button.on("click", function (e) {
                            e.stopPropagation();
                            self.trigger_up('button_clicked', {
                                attrs: node.attrs,
                                record: record,
                            });
                        });
                    }else if($button.hasClass('force_save_dummy_button2')){
                        $button.on("click", function (e) {
                            e.stopPropagation();
                            localStorage.setItem(record.ref, "new_record");
                            localStorage.setItem('auto_click2', 'no_auto_click');
                            self.trigger_up('button_clicked', {
                                attrs: node.attrs,
                                record: record,
                            });
                        });
                    }
                    else if($button.hasClass('force_save_button2')){
                        $button.on("click", function (e) {
                            e.stopPropagation();
                            self.trigger_up('button_clicked', {
                                attrs: node.attrs,
                                record: record,
                            });
                        });
                    }
                    else{
                        $button.prop('disabled', true);
                    }
                }
            }

            return $button;
        },
    })
    
    view_dialogs.FormViewDialog.include({
		init: function (parent, options) {
	        var self = this;
	        options = options || {};

	        this.res_id = options.res_id || null;
	        this.on_saved = options.on_saved || (function () {});
	        this.on_remove = options.on_remove || (function () {});
	        this.context = options.context;
	        this.model = options.model;
	        this.parentID = options.parentID;
	        this.recordID = options.recordID;
	        this.shouldSaveLocally = options.shouldSaveLocally;
	        this.readonly = options.readonly;
	        this.deletable = options.deletable;
	        this.disable_multiple_selection = options.disable_multiple_selection;
	        var oBtnRemove = 'o_btn_remove';

	        var multi_select = !_.isNumber(options.res_id) && !options.disable_multiple_selection;
	        var readonly = _.isNumber(options.res_id) && options.readonly;

	        if (!options.buttons) {
	            options.buttons = [{
	                text: (readonly ? _t("Close") : _t("Discard")),
	                classes: "btn-secondary o_form_button_cancel",
	                close: true,
	                click: function () {
	                    if (!readonly) {
	                        self.form_view.model.discardChanges(self.form_view.handle, {
	                            rollback: self.shouldSaveLocally,
	                        });
	                    }
	                },
	            }];

	            if (!readonly) {
	                options.buttons.unshift({
	                    text: (multi_select ? _t("Save & Close") : _t("Save")),
	                    classes: "btn-primary",
	                    click: function () {
	                        if(self.form_view && self.form_view.renderer && self.form_view.renderer.arch){
                        		var button = false
                            	_.each(self.form_view.renderer.arch.children, function(child){
                            		if (child.tag == 'button' && child.attrs.name == 'dummy_btn'){
                            			button = child.attrs
                            		}
                            	})
                            	if (button){
                            		self.form_view.renderer.trigger_up('button_clicked', {
                                        attrs: button,
                                        record: self.form_view.renderer.state,
                                    });
                            	}
	                        }
                            if (self.context.form_view_ref == "opt_custom.view_patent_profile_form" && (self.title == "Create: Patient"
                                || self.title == "Open: Patient") && self.res_model =="res.partner" && !self.Ok)
                                {
	                    	        self._save();
    	                    	}
    	                    else
                    	        self._save().then(self.close.bind(self));
	                    }
	                });

	                if (multi_select) {
	                    options.buttons.splice(1, 0, {
	                        text: _t("Save & New"),
	                        classes: "btn-primary",
	                        click: function () {
	                        	if(self.form_view && self.form_view.renderer && self.form_view.renderer.arch){
	                        		var button = false
	                            	_.each(self.form_view.renderer.arch.children, function(child){
	                            		if (child.tag == 'button' && child.attrs.name == 'dummy_btn'){
	                            			button = child.attrs
	                            		}
	                            	})
	                            	if (button){
	                            		self.form_view.renderer.trigger_up('button_clicked', {
	                                        attrs: button,
	                                        record: self.form_view.renderer.state,
	                                    })
	                            	}
	                        		setTimeout(function(){
	                        			self._save()
	                                    .then(self.form_view.createRecord.bind(self.form_view, self.parentID, self.form_view.renderer.state))
	                                    .then(function () {
	                                        if (!self.deletable) {
	                                            return;
	                                        }
	                                        self.deletable = false;
	                                        self.buttons = self.buttons.filter(function (button) {
	                                            return button.classes.split(' ').indexOf(oBtnRemove) < 0;
	                                        });
	                                        self.set_buttons(self.buttons);
	                                        self.set_title(_t("Create ") + _.str.strRight(self.title, _t("Open: ")));
	                                    });
	                                },1000)
	                        	}else{
	                        		self._save()
	                                .then(self.form_view.createRecord.bind(self.form_view, self.parentID))
	                                .then(function () {
	                                    if (!self.deletable) {
	                                        return;
	                                    }
	                                    self.deletable = false;
	                                    self.buttons = self.buttons.filter(function (button) {
	                                        return button.classes.split(' ').indexOf(oBtnRemove) < 0;
	                                    });
	                                    self.set_buttons(self.buttons);
	                                    self.set_title(_t("Create ") + _.str.strRight(self.title, _t("Open: ")));
	                                });
	                        	}
	                        },
	                    });
	                }

	                var multi = options.disable_multiple_selection;
	                if (!multi && this.deletable) {
	                    this._setRemoveButtonOption(options, oBtnRemove);
	                }
	            }
	        }
	        this._super(parent, options);
	    },
    });
});