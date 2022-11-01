odoo.define('opt_insurance.FormRenderer', function (require) {
"use strict";

    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        autofocus: function () {
            this._super.apply(this, arguments);
            if (this.state.model == "res.partner" && this.__parentedParent.modelName == "res.partner")
                if (document.getElementsByClassName("name_with_termination_date")[0] !== undefined){
                    var rows = document.getElementsByClassName("name_with_termination_date")[0].children[0].children[0].children[1].children;
                    for (var i=0; i<rows.length; i++)
                        if (rows[i].innerText.includes("Termed")){
                            rows[i].style.color = "grey";
                            rows[i].style.fontStyle = "italic";
                        }
                }
        },

    });

});