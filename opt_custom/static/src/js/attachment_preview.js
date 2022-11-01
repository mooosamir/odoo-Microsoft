odoo.define('opt_custom.attachmentPreview', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var DocumentViewer = require('mail.DocumentViewer');
    var datepicker = require('web.datepicker');
    var dialogs = require('web.view_dialogs');
    var field_registry = require('web.field_registry');
    var FormController = require('web.FormController');
    var field_utils = require('web.field_utils');
    var relational_fields = require('web.relational_fields');
    var FormRenderer = require('web.FormRenderer');

    var _t = core._t;

    var ListRenderer = require('web.ListRenderer');
    
    var pyUtils = require('web.py_utils');
    
    var session = require('web.session');
    var time = require('web.time');

    var _t = core._t;

    var FIELD_CLASSES = {
            char: 'o_list_char',
            float: 'o_list_number',
            integer: 'o_list_number',
            monetary: 'o_list_number',
            text: 'o_list_text',
            many2one: 'o_list_many2one',
        }
    
    ListRenderer.include({
        _renderBodyCell: function (record, node, colIndex, options) {
            var tdClassName = 'o_data_cell';
            if (node.tag === 'button') {
                tdClassName += ' o_list_button';
            } else if (node.tag === 'field') {
                tdClassName += ' o_field_cell';
                var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
                if (typeClass) {
                    tdClassName += (' ' + typeClass);
                }
                if (node.attrs.widget) {
                    tdClassName += (' o_' + node.attrs.widget + '_cell');
                }
            }
            if (node.attrs.editOnly) {
                tdClassName += ' oe_edit_only';
            }
            if (node.attrs.readOnly) {
                tdClassName += ' oe_read_only';
            }
            var $td = $('<td>', { class: tdClassName, tabindex: -1 });

            // We register modifiers on the <td> element so that it gets the correct
            // modifiers classes (for styling)
            var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
            // If the invisible modifiers is true, the <td> element is left empty.
            // Indeed, if the modifiers was to change the whole cell would be
            // rerendered anyway.
            if (modifiers.invisible && !(options && options.renderInvisible)) {
                return $td;
            }

            if (node.tag === 'button') {
                return $td.append(this._renderButton(record, node));
            } else if (node.tag === 'widget') {
                return $td.append(this._renderWidget(record, node));
            }
            if (node.attrs.widget || (options && options.renderWidgets)) {
                var $el = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
                return $td.append($el);
            }
            this._handleAttributes($td, node);
            var name = node.attrs.name;
            var field = this.state.fields[name];
            var value = record.data[name];
            var formatter = field_utils.format[field.type];
            var formatOptions = {
                escape: true,
                data: record.data,
                isPassword: 'password' in node.attrs,
            };
            var temp = {}
            if (!_.isObject(node.attrs.options)) {
                 temp = node.attrs.options ? pyUtils.py_eval(node.attrs.options) : {};
            }
            if (field.type == 'datetime' && temp && temp.custom_time_format) {
                formatOptions['custom_time_format'] = temp.custom_time_format
            }
            var formattedValue = formatter(value, field, formatOptions);
            var title = '';
            if (field.type !== 'boolean') {
                title = formatter(value, field, _.extend(formatOptions, {escape: false}));
            }
            return $td.html(formattedValue).attr('title', title);
        },
    });

    function formatDateTime(value, field, options) {
        if (value === false) {
            return "";
        }
        if (!options || !('timezone' in options) || options.timezone) {
            value = value.clone().add(session.getTZOffset(value), 'minutes');
        }
        if(options && options.custom_time_format){
            var datePattern = time.getLangDateFormat();
            return value.format(datePattern + " " + options.custom_time_format);
        }
        
        return value.format(time.getLangDatetimeFormat());
    }

    function parseDateTime(value, field, options) {
        if (!value) {
            return false;
        }
        var datePattern = time.getLangDateFormat(),
            timePattern = time.getLangTimeFormat();
        if(options && options.custom_time_format){
            timePattern = options.custom_time_format
        }
        var datePatternWoZero = datePattern.replace('MM','M').replace('DD','D'),
            timePatternWoZero = timePattern.replace('HH','H').replace('mm','m').replace('ss','s');
        var pattern1 = datePattern + ' ' + timePattern;
        var pattern2 = datePatternWoZero + ' ' + timePatternWoZero;
        var datetime;
        if (options && options.isUTC) {
            // phatomjs crash if we don't use this format
            datetime = moment.utc(value.replace(' ', 'T') + 'Z');
        } else {
            datetime = moment.utc(value, [pattern1, pattern2, moment.ISO_8601]);
            if (options && options.timezone) {
                datetime.add(-session.getTZOffset(datetime), 'minutes');
            }
        }
        if (datetime.isValid()) {
            if (datetime.year() === 0) {
                datetime.year(moment.utc().year());
            }
            if (datetime.year() >= 1900) {
                datetime.toJSON = function () {
                    return this.clone().locale('en').format('YYYY-MM-DD HH:mm:ss');
                };
                return datetime;
            }
        }
        throw new Error(_.str.sprintf(core._t("'%s' is not a correct datetime"), value));
    }

 
    field_utils.format['datetime'] = formatDateTime;
    field_utils.parse['datetime'] = parseDateTime;
    
    datepicker.DateTimeWidget.include({
        init: function (parent, options) {
            this._super.apply(this, arguments);
            var time_formate = time.getLangDatetimeFormat()
            if(this.__parentedParent &&
                    this.__parentedParent.nodeOptions &&
                   this.__parentedParent.nodeOptions.custom_time_format){
                time_formate = time.getLangDateFormat() + ' ' + this.__parentedParent.nodeOptions.custom_time_format
           }
            var format = this.type_of_date === 'datetime' ? time_formate : time.getLangDateFormat();
            this.options['format'] = format
        },
        
        _formatClient: function (v) {
            if(this.__parentedParent &&
                     this.__parentedParent.nodeOptions &&
                    this.__parentedParent.nodeOptions.custom_time_format){
                return field_utils.format[this.type_of_date](v, null, {timezone: false, custom_time_format: this.__parentedParent.nodeOptions.custom_time_format});
            }else{
                return field_utils.format[this.type_of_date](v, null, {timezone: false});
            }
            
        },
        /**
         * @private
         * @param {string|false} v
         * @returns {Moment}
         */
        _parseClient: function (v) {
            if(this.__parentedParent &&
                    this.__parentedParent.nodeOptions &&
                    this.__parentedParent.nodeOptions.custom_time_format){
                return field_utils.parse[this.type_of_date](v, null, {timezone: false, custom_time_format: this.__parentedParent.nodeOptions.custom_time_format});
            }else{
                return field_utils.parse[this.type_of_date](v, null, {timezone: false});
            }
            
        },
    });

    FormRenderer.include({
        _renderTagNotebook: function (node) {
            var self = this;
            var $headers = $('<ul class="nav nav-tabs">');
            if (self.state && self.state.context && self.state.context.default_patient){
                var $pages = $('<div class="tab-content col-10">');
            }else{
                var $pages = $('<div class="tab-content">');
            }
            // renderedTabs is used to aggregate the generated $headers and $pages
            // alongside their node, so that their modifiers can be registered once
            // all tabs have been rendered, to ensure that the first visible tab
            // is correctly activated
            var renderedTabs = _.map(node.children, function (child, index) {
                var pageID = _.uniqueId('notebook_page_');
                var $header = self._renderTabHeader(child, pageID);
                var $page = self._renderTabPage(child, pageID);
                self._handleAttributes($header, child);
                $headers.append($header);
                $pages.append($page);
                return {
                    $header: $header,
                    $page: $page,
                    node: child,
                };
            });
            // register the modifiers for each tab
            _.each(renderedTabs, function (tab) {
                self._registerModifiers(tab.node, self.state, tab.$header, {
                    callback: function (element, modifiers) {
                        // if the active tab is invisible, activate the first visible tab instead
                        var $link = element.$el.find('.nav-link');
                        if (modifiers.invisible && $link.hasClass('active')) {
                            $link.removeClass('active');
                            tab.$page.removeClass('active');
                            self.inactiveNotebooks.push(renderedTabs);
                        }
                    },
                });
            });
            this._activateFirstVisibleTab(renderedTabs);
            if (self.state && self.state.context && self.state.context.default_patient){
                var $notebookHeaders = $('<div class="o_notebook_headers col-2 notebook_page_vertical">').append($headers);
                var $notebook = $('<div class="o_notebook row">')
                .data('name', node.attrs.name || '_default_')
                .append($notebookHeaders, $pages);
            }else{
                var $notebookHeaders = $('<div class="o_notebook_headers">').append($headers);
                var $notebook = $('<div class="o_notebook">')
                .data('name', node.attrs.name || '_default_')
                .append($notebookHeaders, $pages);
            }
            this._registerModifiers(node, this.state, $notebook);
            this._handleAttributes($notebook, node);
            return $notebook;
        },
    });

    var AttachmentPreviewMultiFiles = relational_fields.FieldMany2ManyBinaryMultiFiles.extend({
        template_files: "AttachmentPreviewMultiFiles",
        events: {
            'click #preview': '_onAttachPreiview',
        },
        _onAttachPreiview:function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            if(this.value && this.value.data && this.value.data[0] && this.value.data[0].data && this.value.data[0].data.id){
                this.attachmentIDs =  _.pluck(this.value.data, 'data');
                var activeAttachmentID = this.value.data[0].data.id;
                if (activeAttachmentID) {
                    var attachmentViewer = new DocumentViewer(this, this.attachmentIDs, activeAttachmentID);
                    attachmentViewer.appendTo($('body'));
                }
            }
        },
    });
    field_registry.add("attachment_preview",AttachmentPreviewMultiFiles);

    basic_fields.FieldChar.include({
        _renderReadonly: function () {
            this.$el.text(this._formatValue(this.value));
            var self = this
            if(this.attrs && this.attrs.widget == 'select_filter' ){
                var field_name = this.name;
                if(field_name.indexOf('select_') != -1 && field_name.split('select_')[1]){
                    var related_field_name = field_name.split('select_')[1];
                    if(self.record && self.record.data && related_field_name && self.record.data[related_field_name]){
                        var temp = self.record.data[related_field_name]
                        if (temp == 'No Value'){
                            temp = ""
                        }
                        self.$el.text(self._formatValue(temp));
                    }
                }
            }else{
                this._super.apply(this, arguments);
            }
        },
        _renderEdit: function () {
            var def = this._super.apply(this, arguments);
            var self = this
            if(this.attrs && this.attrs.widget == 'select_filter' ){
               // $("." + this.name + "_selection_custom").remove();
                if(this.$el && this.$el[0]){
                    $(this.$el[0]).hide()
                }
                if(this.$el && this.$el[1]){
                    $(this.$el[1]).html("")
                    $(this.$el[1]).html(this._renderSelection2())
                }else{
                    this.$el = this.$el.add($(this._renderSelection()));
                }
                $(this.$el[1]).off('click').click(function(){
                    if(! $(this).val()){
                        var field_name = self.name;
                        if(field_name.indexOf('select_') != -1 && field_name.split('select_')[1]){
                            var related_field_name = field_name.split('select_')[1];
                            if(self.record && self.record.data && related_field_name && _.has(self.record.data,related_field_name)){
                                $("input[name='" + related_field_name + "']").val('No Value')
                                $("input[name='" + related_field_name + "']").trigger('change');
                            }
                        }
                    }
                })
                $(this.$el[1]).off('change').on('change',function(){
               //     this.$input.off('change').on('change',function(){
                    var field_name = self.name;
                    if(field_name.indexOf('select_') != -1 && field_name.split('select_')[1]){
                        var related_field_name = field_name.split('select_')[1];
                        if(self.record && self.record.data && related_field_name && _.has(self.record.data,related_field_name)){
                            $("input[name='" + related_field_name + "']").val($(this).val())
                            $("input[name='" + related_field_name + "']").trigger('change');
                        }
//                        if(self.record && self.record.fieldsInfo 
//                                && self.record.viewType
//                                &&  _.has(self.record.fieldsInfo['form'],related_field_name)){
//                            $("input[name='" + related_field_name + "']").val($(this).val())
//                            $("input[name='" + related_field_name + "']").trigger('change');
//                        }
                    }
                });
            }
            return def;
        },
        _renderSelection: function () {
            var temp = "<option class='blank_opt'></option>"
            var self = this;
            var field_name = self.name;
            var select_value = false
            if(field_name.indexOf('select_') != -1 && field_name.split('select_')[1]){
                var related_field_name = field_name.split('select_')[1];
                if(self.record && self.record.data && related_field_name && self.record.data[related_field_name]){
                    select_value = self.record.data[related_field_name];
                }
//                if(self.record && self.record.fieldsInfo 
//                        && self.record.viewType
//                        &&  _.has(self.record.fieldsInfo['form'],related_field_name)){
//                    if(self.record.data[related_field_name]){
//                        select_value = self.record.data[related_field_name]
//                    }
//                }
            }
            if(this.value){
                _.each(this.value.split(","),function(vt){
                    if(vt != '@@@@@@@@@@@@@@@' && vt != 'No Value'){
                        if(select_value == vt){
                            temp = temp +  "<option selected='selected'>" + vt + "</option>";
                        }else{
                            temp = temp + "<option>" + vt + "</option>";
                        }
                    }
                });
                return '<select class="o_input ' + this.name + '_selection_custom ">' + temp + "</select>"
            }
            return '<select class="o_input ' + this.name + '_selection_custom ">' + temp + "</select>"
        },
        _renderSelection2: function () {
            var temp = "<option class='blank_opt'></option>"
            if(this.value){
                _.each(this.value.split(","),function(vt){
                    if(vt != '@@@@@@@@@@@@@@@' && vt != 'No Value'){
                        temp = temp + "<option>" + vt + "</option>";
                    }
                });
                return temp
            }
            return temp
        },
    });

    FormController.include({
        _onOpenOne2ManyRecord: async function (ev) {
            ev.stopPropagation();
            var data = ev.data;
            var record;
            if (data.id) {
                record = this.model.get(data.id, {raw: true});
            }
            // Sync with the mutex to wait for potential onchanges
            await this.model.mutex.getUnlockedDef();
            var self = this;
            var o2mDialog = new dialogs.FormViewDialog(this, {
                context: data.context,
                domain: data.domain,
                fields_view: data.fields_view,
                model: this.model,
                on_saved: data.on_saved,
                on_remove: data.on_remove,
                parentID: data.parentID,
                readonly: data.readonly,
                deletable: record ? data.deletable : false,
                recordID: record && record.id,
                res_id: record && record.res_id,
                res_model: data.field.relation,
                shouldSaveLocally: true,
                title: (record ? _t("Open: ") : _t("Create ")) + (ev.target.string || data.field.string),
            })
            if(data.fields_view && data.fields_view.arch && data.fields_view.arch.attrs.increase_dialog_size == '1'){
                o2mDialog.opened(function () {
                    o2mDialog.$modal.find('.modal-dialog').css('max-width', '95%');
                });
            }
            if(data.fields_view && data.fields_view.arch && data.fields_view.arch.attrs.dialog_size_1180px == '1'){
                o2mDialog.opened(function () {
                    o2mDialog.$modal.find('.modal-dialog').css('max-width', '1180px');
                });
            }
            o2mDialog.open()
        },
    });

});
