odoo.define("post_sale_transactions.sale_order_many2many_tags_link", function(require){
"use strict";

var relational_fields = require('web.relational_fields');
var dialogs = require('web.view_dialogs');
var core = require('web.core');
var qweb = core.qweb;
var _t = core._t;

relational_fields.FormFieldMany2ManyTags.include({
    events: _.extend({}, relational_fields.FieldMany2ManyTags.prototype.events, {
        'click :not(.dropdown-toggle):not(.o_input_dropdown):not(.o_input):not(:has(.o_input)):not(.o_delete):not(:has(.o_delete))': '_onClickLink',
    }),

    /**
     * @private
     * @param {jQuery} element
     */
    _getBadgeId: function(element){
            if ($(element).hasClass('badge')) return $(element).data('id');
            return $(element).closest('.badge').data('id');
    },

    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.hasDropdown = !!this.colorField;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClickLink: function (ev) {
        ev.preventDefault();
        if (this.nodeOptions.force_color || ev.shiftKey ) {
            return;
        }
        var self = this;
        var recordId = this._getBadgeId(ev.target);
        if (self.field.relation == 'sale.order')
            return this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'sale.order',
                res_id: recordId,
                views: [[false, 'form']],
                target: 'current'
            })
    },
});

return {
    FieldMany2ManyTags: relational_fields.FieldMany2ManyTags
}

});