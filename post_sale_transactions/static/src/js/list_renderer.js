odoo.define('post_sale_transactions.ListRenderer', function (require) {
"use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        _onSortColumn: function (ev) {
            if (!(this.__parentedParent.model == 'sale.order'))
                return this._super.apply(this, arguments);
        },
   });

});