odoo.define('opt_custom.FormRenderer', function (require) {
"use strict";

    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        autofocus: function () {
            this._super.apply(this, arguments);
            if (this.state.model == "res.partner" && this.__parentedParent.modelName == "res.partner")
                if (document.getElementsByClassName("advance_expiration_date")[0] !== undefined){
                    var rows = document.getElementsByClassName("advance_expiration_date")[0].children[0].children[0].children[1].children;
                    for (var i=0; i<rows.length; i++)
                        if (rows[i].innerText.includes("Discontinued") || rows[i].innerText.includes("Expired")){
                            rows[i].style.color = "grey";
                            rows[i].style.fontStyle = "italic";
//                            rows[i].children[2].style.fontWeight = "bold"
                        }
                }
        },

    });

});