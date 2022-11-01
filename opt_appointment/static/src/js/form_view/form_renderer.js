odoo.define('opt_appointment.FormRenderer', function (require) {
"use strict";

    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        autofocus: function () {
            this._super.apply(this, arguments);
            if (this.state.model == "res.partner" && this.__parentedParent.modelName == "res.partner")
                if (document.getElementsByClassName("modal-title")[1] !== undefined)
                    if (document.getElementsByClassName("modal-title")[1].innerText == "Create: Patient"){
                        document.getElementsByClassName("modal-title")[1].parentElement.parentElement.style.minWidth = "120%";
                        document.getElementsByClassName("modal-title")[1].parentElement.parentElement.style.right = '10%';
                    }
        },

    });

});