odoo.define('char_datetime_widget.widget', function(require) {
    "use strict";

    var field_registry = require('web.field_registry');
    var BasicFields = require('web.basic_fields');
    var datepicker = require('web.datepicker');
    var Field = field_registry.get('char');
    var FieldDate = BasicFields.FieldDate;
    var core = require('web.core');
    var time = require('web.time');
    var _lt = core._lt;
    var _t = core._t;

    var DateTimeWidget = FieldDate.extend({
        description: _lt("Date & Time"),
        supportedFieldTypes: ['char'],

        init: function () {
            this._super.apply(this, arguments);
            if (this.record.data[this.nodeOptions.field] && this.record.res_id == undefined){
                var record = this.record.data[this.nodeOptions.field];
                if (record._d.toString().substr(28,1) == "+")
                    var record_value = record.clone().hour(record.hour() + parseInt(record._d.toString().substr(29,2))).minute(record.minute() +
                                                    parseInt(record._d.toString().substr(31,2)));
                else
                    var record_value = record.clone().hour(record.hour() - parseInt(record._d.toString().substr(29,2))).minute(record.minute() -
                                                    parseInt(record._d.toString().substr(31,2)));
                this._setValue(record_value.format(time.getLangDatetimeFormat()));
                this.value = record_value;
            }
            else{
                if (this.value){
                    this._setValue(moment(this.value, time.getLangDatetimeFormat()).format(time.getLangDatetimeFormat()))
                    this.value = moment(this.value, time.getLangDatetimeFormat());
                }
            }
            this.datepickerOptions.defaultDate = this.value;
            this.datepickerOptions.format = time.getLangDatetimeFormat();
        },
        _getValue: function () {
            var value = this.datewidget.getValue();
            this._setValue(value.format(time.getLangDatetimeFormat()));
            return false;
        },
        _isSameValue: function (value) {
            if (value === false) {
                return this.value === false;
            }
            return value == this.value;
        },
        _makeDatePicker: function () {
            return new datepicker.DateTimeWidget(this, this.datepickerOptions);
        },
        _renderEdit: function () {
            var value = this.value;
            this.datewidget.setValue(value);
            this.$input = this.datewidget.$input;
        },
    });
    field_registry
        .add('char_datetime_widget', DateTimeWidget);
    return {
        DateTimeWidget: DateTimeWidget
    };
});