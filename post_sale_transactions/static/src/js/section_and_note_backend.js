odoo.define('post_sale_transactions.section_and_note_backend', function (require) {
"use strict";

    var SectionAndNoteListRenderer = require('account.section_and_note_backend');

    SectionAndNoteListRenderer.include({
        _renderBodyCell: function (record, node, index, options) {
            var $cell = this._super.apply(this, arguments);
            var isSection = record.data.display_type === 'line_section';
            var isNote = record.data.display_type === 'line_note';

            if (record.model == 'sale.order.line' && record.viewType == 'list'){
                if ((isSection || isNote) && node.attrs.widget === "section_and_note_text") {
                    $cell[0].style.setProperty('padding-left', '0px', 'important');
                    return $cell;
                }
                if ((isSection || isNote) && node.attrs.widget === "o_column_sortable") {
                    $cell[0].classList.remove("o_column_sortable");
                    return $cell;
                }
            }
            return $cell;
        },
   });

});