odoo.define('ivis_order_grouping.list_renderer', function (require) {
"use strict";

    var ListRenderer = require('web.ListRenderer');

    ListRenderer.include({
        init: function (parent, state, params) {
            this._super(parent, state, params);
            if (this.state.model == "sale.order.line.hcpcs" && 'context' in this.state && this.state.context.active_model == "account.move")
                this.hasSelectors = false;
        },
        _renderRow: function (record, index) {
            var $tr = this._super.apply(this, arguments);
            if ($tr.hasClass('text-muted') && this.arch.attrs.class == 'lab_details_tree_view')
                $tr.attr("style", 'color:#dd871a !important');
            return $tr;
        },
    })
});