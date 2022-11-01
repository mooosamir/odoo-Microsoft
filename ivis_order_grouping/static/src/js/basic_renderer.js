odoo.define('post_sale_transactions.BasicRenderer', function (require) {
"use strict";

    var BasicRenderer = require('web.BasicRenderer');

    //line 51 & 52
    //section_and_note_backend view & delete buttons on sale.order.line.

    BasicRenderer.include({
        _renderFieldWidget: function (node, record, options) {
            options = options || {};
            var fieldName = node.attrs.name;
            // Register the node-associated modifiers
            var mode = options.mode || this.mode;
            var modifiers = this._registerModifiers(node, record, null, options);
            // Initialize and register the widget
            // Readonly status is known as the modifiers have just been registered
            var Widget = record.fieldsInfo[this.viewType][fieldName].Widget;
            var widget = new Widget(this, fieldName, record, {
                mode: modifiers.readonly ? 'readonly' : mode,
                viewType: this.viewType,
            });

            // Register the widget so that it can easily be found again
            if (this.allFieldWidgets[record.id] === undefined) {
                this.allFieldWidgets[record.id] = [];
            }
            this.allFieldWidgets[record.id].push(widget);

            widget.__node = node; // TODO get rid of this if possible one day

            // Prepare widget rendering and save the related promise
            var def = widget._widgetRenderAndInsert(function () {});
            var $el = $('<div>');

            this.defs.push(def);

            // Update the modifiers registration by associating the widget and by
            // giving the modifiers options now (as the potential callback is
            // associated to new widget)
            var self = this;
            def.then(function () {
                // when the caller of renderFieldWidget uses something like
                // this.renderFieldWidget(...).addClass(...), the class is added on
                // the temporary div and not on the actual element that will be
                // rendered. As we do not return a promise and some callers cannot
                // wait for this.defs, we copy those classnames to the final element.
                if (widget.$el != undefined){
                    var a = $('<div>');
                    widget.$el.addClass($el.attr('class'));
                    if (widget.attrs.name == 'name' && widget.attrs.widget == 'section_and_note_text' && widget.model == 'sale.order.line' && widget.field.type =='text' && widget.field.string == 'Description' && widget.record.data.display_type == 'line_section')
                        widget.$el[0].insertAdjacentHTML('beforeend', '<td class="o_data_cell o_field_cell o_list_text" tabindex="-1" colspan="1"><span style="margin-left: 20px;"><i class="fa fa-eye so_view_record"></i><i class="fa fa-trash so_delete_order_type" style="padding-left: 20px"></i><i class="fa fa-money so_apply_discount" style="padding-left: 20px"></i></span></td>');
                    $el.replaceWith(widget.$el);
                    self._registerModifiers(node, record, widget, {
                        callback: function (element, modifiers, record) {
                            element.$el.toggleClass('o_field_empty', !!(
                                record.data.id &&
                                (modifiers.readonly || mode === 'readonly') &&
                                !element.widget.isSet()
                            ));
                        },
                        keepBaseMode: !!options.keepBaseMode,
                        mode: mode,
                    });
                    self._postProcessField(widget, node);
                }
            });

            return $el;
        },
   });

});