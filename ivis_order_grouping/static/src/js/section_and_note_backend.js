odoo.define('ivis_order_grouping.section_and_note_backend', function (require) {
"use strict";

    var SectionAndNoteListRenderer = require('account.section_and_note_backend');
    var ListRenderer = require('web.ListRenderer');
    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var fieldRegistry = require('web.field_registry');
    var rpc = require('web.rpc');

    var SectionAndNoteListRenderer = SectionAndNoteListRenderer.extend({
        events: _.extend({}, SectionAndNoteListRenderer.prototype.events,{
            'click .so_view_record': '_viewRecord',
            'click .so_delete_order_type': '_deleteOrderType',
            'click .so_apply_discount': '_applyDiscount',
        }),
        _renderBodyCell: function (record, node, index, options) {
            var $cell = this._super.apply(this, arguments);
            var isSection = record.data.display_type === 'line_section';
            var isNote = record.data.display_type === 'line_note';

            if (record.model == 'sale.order.line' && record.viewType == 'list' && isSection && node.attrs.name == "name" && !isNaN(parseInt($cell.attr('colspan')))){
//                $cell.attr('colspan', parseInt($cell.attr('colspan')) - 1 );
                $cell[0].classList.add("applied");
                $cell[0].classList.add("section_and_note_highlight");
            }
            return $cell;
        },
        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);
//            var o_section_and_note_text_cell = $row.find('td.o_data_cell.o_field_cell.o_list_text.o_section_and_note_text_cell.applied')
//            var o_list_record_remove = $row.find('td.o_list_record_remove')
//            if (record.model == 'sale.order.line' && record.viewType == 'list'){
//                if (o_section_and_note_text_cell.length == 1){
////                    $row[0].insertAdjacentHTML('beforeend', '<td class="o_data_cell o_field_cell o_list_text" tabindex="-1" colspan="1"><div><i class="fa fa-eye so_view_record" style=display: block;text-align: -webkit-right;'></i></div></td>');
//                    $row[0].insertAdjacentHTML('beforeend', '<td class="o_data_cell o_field_cell o_list_text" tabindex="-1" colspan="1"><div><i class="fa fa-eye so_view_record"></i><i class="fa fa-trash so_delete_order_type" style="padding-left: 20px"></i></div></td>');
////                    $row[0].insertAdjacentHTML('beforeend', '<td class="o_data_cell o_field_cell o_list_text" tabindex="-1" colspan="4"><div></div></td>');
//                }
//                if (o_list_record_remove.length == 1)
//                    $row[0].removeChild(o_list_record_remove[0]);
//            }
            return $row;
        },
        _onRowClicked: function (ev) {
            if (!(this.__parentedParent.model == 'sale.order' && $(ev.currentTarget).hasClass('o_is_line_section') && this.__parentedParent.attrs.name == 'order_line'))
                return this._super.apply(this, arguments);
        },
        _viewRecord: function(ev){
            if (this.__parentedParent && 'attrs' in this.__parentedParent){
                if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click')) {
                    var id = $(ev.currentTarget).parent().parent().parent().parent().data('id');
                    if (id)
                        for (var child in this.__parentedChildren)
                            if(id == this.__parentedChildren[child].dataPointID){
                                if (this.__parentedChildren[parseInt(child)].record.data.lab_details_id)
                                    this.do_action({
                                        type: 'ir.actions.act_window',
                                        view_mode: 'form',
                                        views: [[false, 'form']],
                                        target: 'new',
                                        res_id: this.__parentedChildren[parseInt(child)].record.data.lab_details_id.data.id,
                                        res_model: 'multi.order.type',
                                        context: {'new_size': 'max-width_1150px'},
                                    });
                                break;
                            }
                }
            }
        },
        _deleteOrderType: function (ev) {
            var self = this;
            var found = false;
            if (this.__parentedParent && 'attrs' in this.__parentedParent){
                if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click')) {
                    var id = $(ev.currentTarget).parent().parent().parent().parent().data('id');
                    if (id){
                        for (var child in this.__parentedChildren){
                            if(id == this.__parentedChildren[child].dataPointID)
                                if (this.__parentedChildren[parseInt(child)].record.data.lab_details_id){
                                    found = true;
                                    break;
                                }
                        }
                        if (found){
                            rpc.query({
                                model: 'sale.order',
                                method: 'delete_sale_order_line',
                                args: [[], this.__parentedChildren[parseInt(child)].record.data.lab_details_id.data.id, this.__parentedChildren[parseInt(child)].record.data.id],
                            }).then(function (response) {
                                if (response == "1")
                                    self.do_action({
                                        type: 'ir.actions.act_window',
                                        view_mode: 'form',
                                        views: [[false, 'form']],
                                        res_id: self.__parentedParent.record.res_id,
                                        res_model: 'sale.order',
                                    });
                            });
                        }
                    }
                }
            }
        },
        _applyDiscount: function (ev) {
            var self = this;
            var found = false;
            if (this.__parentedParent && 'attrs' in this.__parentedParent){
                if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click')) {
                    var id = $(ev.currentTarget).parent().parent().parent().parent().data('id');
                    if (id){
                        for (var child in this.__parentedChildren){
                            if(id == this.__parentedChildren[child].dataPointID)
                                if (this.__parentedChildren[parseInt(child)].record.data.lab_details_id){
                                    found = true;
                                    break;
                                }
                        }
                        if (found){
                            return rpc.query({
                                model: 'sale.order.line',
                                method: 'apply_discount',
                                args: [this.__parentedChildren[parseInt(child)].record.data.id],
                            }).then(function (response) {
                                return self.do_action(response);
                            });
                        }
                    }
                }
            }
        },
    });

    var SectionAndNoteFieldOne2Many = FieldOne2Many.extend({
        /**
         * We want to use our custom renderer for the list.
         *
         * @override
         */
        _getRenderer: function () {
            if (this.view.arch.tag === 'tree') {
                return SectionAndNoteListRenderer;
            }
            return this._super.apply(this, arguments);
        },
    });

    fieldRegistry.add('section_and_note_one2many', SectionAndNoteFieldOne2Many);

    return SectionAndNoteListRenderer;
});