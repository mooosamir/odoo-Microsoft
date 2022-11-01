odoo.define('post_sale_transactions.session_widget', function(require) {
    "use strict";

    var field_registry = require('web.field_registry');
//    Only works in debug mode
//    var Field = field_registry.get('char');
    var BasicFields = require('web.basic_fields');
    var Field = BasicFields.FieldChar;
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');

    var zif_session_widget = Field.extend({
        events: {
         'change .counted': 'counted_changed',
         'change .starting_cash': 'starting_cash_changed',
//         'click .starting_cash': 'open_starting_cashbox',
         'click .zif_set_value': '_SetValue',
        },
        template: 'zif_session_widget_main',
        init: function () {
            this._super.apply(this, arguments);
            this.dict = {};
            this.state = this.record.data['state'];
            if ((this.attrs.options.value != undefined && !['closing_control','closed', 'opening_control'].includes(this.state))
                || (this.attrs.options.value != undefined && !this.value)){
                var value = {}
                if (this.record.data[this.attrs.options.value])
                    value = JSON.parse(this.record.data[this.attrs.options.value].replaceAll('\'','\"'));
                this.dict = value;
//                this._setValue(JSON.stringify(value));
                $('.zif_set_value').eq(0).val(JSON.stringify(value));
                $('.zif_set_value').click();
            }
            else if (this.value != undefined){
                this.dict = JSON.parse(this.value);
            }
        },
        _renderReadonly: function () {
        },
        _renderEdit: function () {
            if (this.value != undefined && this.value){
                this.dict = JSON.parse(this.value);
            }
        },
        counted_changed: function(ev){
            var self = this;
            if (!isNaN(parseInt(ev.currentTarget.value))){
                var counted = parseFloat((ev.currentTarget.value));
                var expected = parseFloat($(ev.currentTarget).parent().parent().find('td.expected')[0].innerText);
                var difference = $(ev.currentTarget).parent().parent().find('span.difference')[0].innerText = counted-expected;
                var id = $(ev.currentTarget).parent().parent().attr('data-id');
                self._update_value(id, counted, difference);
            }
        },
        _update_value(id, counted, difference){
            var self = this;
            var value = JSON.parse(self.value);
            var journal_ids = value.journal_ids;
            for (var i=0; i< journal_ids.length; i++){
                if (journal_ids[i].Id == id){
                    journal_ids[i].counted = counted;
                    journal_ids[i].difference = difference;
                }
            }
            value.journal_ids = journal_ids;
            $('.zif_set_value').eq(0).val(JSON.stringify(value));
            $('.zif_set_value').click();
        },
        starting_cash_changed(ev){
            var self = this;
            var value = JSON.parse(self.value);
            value.cash_register_balance_start = ev.currentTarget.value;
            $('.zif_set_value').eq(0).val(JSON.stringify(value));
            $('.zif_set_value').click();
        },
        _SetValue:  function(){
    		this._setValue($('.zif_set_value').eq(0).val());
    		this._render();
        },
//        open_starting_cashbox: function(){
//            var self = this;
//            rpc.query({
//                model: 'sale.order.session',
//                method: 'open_starting_cashbox',
//                args: [[this.record.data.id]],
//            }).then(function(result) {
//                result['views'] = [[false, 'form']];
//                self.do_action(result);
//            });
//        },
    });
    field_registry
        .add('zif_session_widget', zif_session_widget);
    return {
        zif_session_widget: zif_session_widget
    };
});