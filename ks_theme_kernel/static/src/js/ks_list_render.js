odoo.define('ks_theme_backend.ksListRenderer', function(require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');

    var Ks_ListRenderer = ListRenderer.include({

//        _renderView: function() {
//            var self = this;
//            var ks_super = this._super.apply(this, arguments).then(function() {
//                if (self.optionalColumns.length) {
//                    self.$('.o_optional_columns_dropdown_toggle').remove();
//                    self.$('table thead tr').append($('<i class="ks_add_col_stick o_optional_columns_dropdown_toggle fa fa-ellipsis-v"/>'));
//                }
//            });
//            return $.when(ks_super);
//        }
    });
    return Ks_ListRenderer;
});
