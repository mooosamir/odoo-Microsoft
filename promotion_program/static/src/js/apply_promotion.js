
odoo.define('promotion_program.apply_promotion', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var apply_promotion = AbstractAction.extend({
        template: 'apply_promotion_client_action',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'click .ApplyPromo': 'apply_code',
            'click .codeApplied': 'code_applied',
        },
        start: function () {
            return this._super();
        },
        init: function(parent, args) {
            var self = this;
            this._super(parent, args);
            this.data_id = this.controlPanelParams.context.id;
            self.transmit_data();
            this.controlPanelParams.context.dialog_size = 'medium';
            this.controlPanelParams.context.renderFooter = false;
        },

         code_applied: function(ev){
            var self = this;
            self._rpc({model: 'sale.order', method: 'code_applied', args : [[],$(ev.currentTarget.parentElement.parentElement.children).find('input').val(),ev.currentTarget.getAttribute('id'),ev.currentTarget.getAttribute('soid'),ev.currentTarget.getAttribute('data'),ev.currentTarget.getAttribute('amount')]})
                .then(function (promo) {
                    if (promo == '1'){
                        $(ev.currentTarget).css("background-color","green");
                         $(ev.currentTarget).attr("disabled",'disabled');
                         $("button[data-dismiss='modal']").click()




                    }
                    else if(promo == '0'){
                        alert('Wrong promo code')
                    }
                });
                },


        apply_code: function(ev){
            var self = this;
            self._rpc({model: 'sale.order', method: 'apply_code', args : [[],ev.currentTarget.getAttribute('id'),ev.currentTarget.getAttribute('data'),ev.currentTarget.getAttribute('amount'),this.data_id]})
                .then(function (promo_code) {
                    if (promo_code.promo_code) {
                        $(".main-container").css("display", "none");
                        $(".promo-code-box").css("display", "block");
                        $(".codeApplied").attr("id",promo_code.id);
                        $(".codeApplied").attr("soid",promo_code.soid);
                        $(".codeApplied").attr("data",promo_code.data);
                        $(".codeApplied").attr("amount",promo_code.amount);
                    }
                    else if (promo_code == 0){
                        alert('Promotion Already Applied')
                    }
                    else{

                         $(ev.currentTarget).css("background-color","green");
                         $(ev.currentTarget).html("Applied");
                         $(ev.currentTarget).attr("disabled",'disabled');

                    }

                });
        },
        transmit_data: function(ev){
            var self = this;
            self._rpc({model: 'sale.order', method: 'apply_promotion', args : [[], this.data_id]})
                .then(function (response) {

                    var content = (QWeb.render('apply_promotion_template', {
                        data: response ,
                    }));



                    $('.apply_promotion_client_action')[0].innerHTML += content;


//                    var heading = []
//                    for (let i = 0; i < response.length; i++) {
//                        heading.push(response[i].heading)
////                        $('.response')[0].innerHTML += '<h3>' + response[i].heading + '</h3>' + '<br>';
////                        $('.response')[0].innerHTML += '<h5>' + response[i].promo_name + '</h5>' + '<br>';
////                        $('.response')[0].style['text-align'] = 'center';
////                        $('.response-btn')[0].innerHTML += '<button id="'+ response[i].promo_id +'" class="ApplyPromo"> Apply </button>' + '<br>';
//                    }
//                    var new_heading = [...new Set(heading)]
//                     for (let i = 0; i < new_heading.length; i++) {
//                        $('.type-heading')[0].innerHTML += new_heading[i];
//                        for (let i = 0; i < response.length; i++) {
//                            if (response[i].heading === new_heading[i]){
//                                 $('.promo-title')[0].innerHTML += (response[i].promo_name);
//                                 $('.promo-btn')[0].innerHTML += '<button id="'+ response[i].promo_id +'" class="ApplyPromo"> Apply </button>' + '<br>';
//                            }
//                        }
//                        }
//
                });
        },
    });

    core.action_registry.add("apply_promotion", apply_promotion);
    return apply_promotion;
});