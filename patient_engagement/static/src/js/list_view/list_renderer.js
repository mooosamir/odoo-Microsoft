odoo.define('patient_engagement.list_renderer', function (require) {
"use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _renderRow: function (record, index) {
            var $tr = this._super.apply(this, arguments);
            if (this.arch.attrs.class == 'messaging_history_tree_view'){
                var line = '<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier status" tabindex="-1" title="' + $tr.find('.status')[0].innerHTML + '">';
                var status = $tr.find('.status')[0].innerHTML.split(',');
                var html = '';
                for (var s in status){
                    if (status[s]=='Successful')
                        html += "<span style='color:#1d521d;padding-right: 5px;'>Successful</span>"
                    else if (status[s]=='Failed')
                        html += "<span style='color:#9b6a12;padding-right: 5px;'>Failed</span>"
                    else if (status[s]=='Error')
                        html += "<span style='color:#5a1e1e;padding-right: 5px;'>Error</span>"
                }
                line += html + '</td>';

                var o_list_record_remove = $tr.find('td.status')
                if (o_list_record_remove.length == 1)
                    $tr[0].removeChild(o_list_record_remove[0]);
                $tr[0].insertAdjacentHTML('beforeend', line);
            }
            return $tr;
        },
    })
});