odoo.define('opt_appointment.SearchBar', function (require) {
"use strict";

    var SearchBar = require('web.SearchBar');

    SearchBar.include({
        init: function (parent, params) {
            this.parent = parent;
            this._super.apply(this, arguments);
        },

    });

});