odoo.define('post_sale_transactions.stripe_wizard', function (require) {
"use strict";
// Testing
// https://stripe.com/docs/testing#carte-bancaires
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var stripe_checkout = AbstractAction.extend({
        template: 'pst.stripe_initial',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'click .btn-primary': 'submit_clicked',
            'click .back': 'back_clicked',
            'click .return': 'return_clicked',
        },
        jsLibs: [
            'https://js.stripe.com/v3/',
        ],
        init: function(parent, args) {
            var self = this;
            this._super(parent, args);
            this.sk = '';
            if (this.controlPanelParams.context.is_outbound)
                this.controlPanelParams.context.dialog_size = 'large';
            else
                this.controlPanelParams.context.dialog_size = 'medium';
            this.controlPanelParams.context.renderHeader = false;
            this.controlPanelParams.context.renderFooter = false;
        },
        willStart: function() {
            var self = this;
            if (!this.controlPanelParams.context.is_outbound)
                return Promise.all([
                        this._super.apply(this, arguments),
                        $.ajax({
                           url : '/stripe/spk',
                           type : 'GET',
                           success : function(response) {
                                self.sk = response
                           },
                        })
    //                    self._rpc({model: 'frames.data', method: 'get_vendors', args : [[]]})
    //                        .then(function (vendors) {self.vendors = vendors;}),
                 ]);
            else
                return Promise.all([
                        this._super.apply(this, arguments),
                        $.ajax({
                           url : '/stripe/returns?id=' + self.controlPanelParams.context.multi_invoice_payment_id,
                           type : 'GET',
                           success : function(response) {
                                self.returns = response
                           },
                        })
                 ]);
        },
        start: function () {
            if (!this.controlPanelParams.context.is_outbound)
                this.render_elements();
            else{
                this.$el.find('.row')[1].style.display = 'none';
                this.$el.find('.returns')[0].style.display = '';
                this.$el.find('button[type="submit"]')[0].style.display = 'none'
                $(this.$el.find('tbody')[1]).html(this.returns);
            }
            return this._super().then(function() {
                console.log("this works, no promise is lost and the code executes in a controlled order: first super, then our code.")
            });
        },
        render_elements: function(ev){
            this.stripe = Stripe(this.sk);

            var elements = this.stripe.elements();
            // Set up Stripe.js and Elements to use in checkout form
//            var style = {
//              base: {
//                color: "#32325d",
//                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
//                fontSmoothing: "antialiased",
//                fontSize: "16px",
//                "::placeholder": {
//                  color: "#aab7c4"
//                }
//              },
//              invalid: {
//                color: "#fa755a",
//                iconColor: "#fa755a"
//              },
//            };
            this.cardElement = elements.create('card', {hidePostalCode: true});
            this.cardElement.mount(this.$el.find('#card-element')[0]);
        },
        back_clicked: function(ev){
            var self = this;
            if ("account_payment_id" in this.controlPanelParams.context){
                return self._rpc({
                    model: 'account.payment',
                    method: 'reopen_account_payment',
                    args : [[], self.controlPanelParams.context.account_payment_id]
                }).then(function (result) {return self.do_action(result)})
            }
            else if ("multi_invoice_payment_id" in this.controlPanelParams.context)
                return this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'multi.invoice.payment',
                    res_id: this.controlPanelParams.context.multi_invoice_payment_id,
                    views: [[false, 'form']],
                    target: 'new'
                })
            else
                alert("No reference found.")
        },
        return_clicked: function(ev){
            var self = this;
            var account_payment_id = $(ev.currentTarget).attr('data-id')
            $.ajax({
               url : '/stripe/return/pay',
               type : 'POST',
               headers: { 'Content-Type': 'application/json' },
               data: JSON.stringify({
                   id: self.controlPanelParams.context.multi_invoice_payment_id,
                   account_payment_id: account_payment_id,
                   csrf_token: odoo.csrf_token,
               }),
               success : function(response) {
                    if (response.result.error) {
                        $.unblockUI();
                        var html = self.error_message(response.result);
                        self.$el.find('.error_message').html(html)
                    } else {
                        $.unblockUI();
                        alert("Payment Successful refunded");
                        self.do_action({
                            type: 'ir.actions.act_window_close'
                        })
                    }
               }
            })
        },
        submit_clicked: function(ev){
            event.preventDefault()
            if (!$(ev.currentTarget).hasClass("button")){
                var self = this;
                // We don't want to let default form submission happen here,
                // which would refresh the page.
                $.blockUI({
                    'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                        '    <br /> Processing' +
                        '</h2>'
                });
                var createPaymentMethod = self.stripe.createPaymentMethod({
                  type: 'card',
                  card: self.cardElement,
    //              billing_details: {
    //                // Include any additional collected billing details.
    //                name: 'Jenny Rosen',
    //              },
                }).then(function(result){
                    if (result.error) {
                        $.unblockUI();
                        var html = self.error_message(result);
                        self.$el.find('.error_message').html(html)
                    } else {
                      $.blockUI({
                          'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                              '    <br /> Processing' +
                              '</h2>'
                      });
                      fetch('/stripe/pay', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          payment_method_id: result.paymentMethod.id,
                          csrf_token: odoo.csrf_token,
                          multi_invoice_payment_id: self.controlPanelParams.context.multi_invoice_payment_id,
                        })
                      }).then(function(result) {
                        result.json().then(function(json) {
                          self.handleServerResponse(json.result);
                        })
                      });
                    }
                })
            }
        },
        handleServerResponse: function(response) {
          var self = this;
          if (response.error) {
                $.unblockUI();
                var html = self.error_message(response);
                self.$el.find('.error_message').html(html)
          } else if (response.requires_action) {
            this.stripe.handleCardAction(
              response.payment_intent_client_secret
            ).then(function(result) {
              if (result.error) {
                    $.unblockUI();
                    var html = self.error_message(result);
                    self.$el.find('.error_message').html(html)
              } else {
                fetch('/stripe/pay', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                      payment_intent_id: result.paymentIntent.id,
                      multi_invoice_payment_id: self.controlPanelParams.context.multi_invoice_payment_id,
                  })
                }).then(function(confirmResult) {
                  $.unblockUI();
                  return confirmResult.json();
                }).then(function(response) {
                  self.handleServerResponse(response.result);
                });
              }
            });
          } else {
            $.unblockUI();
            alert("Payment Successful");
            self.do_action({
                type: 'ir.actions.act_window_close'
            })
          }
        },
        error_message: function(response){
            var html = "<p>";
            if (response.error != undefined && response.error.code == undefined)
                html += response.error +"<br/>";
            if (response.error.type != undefined)
                html += response.error.type +"<br/>";
            if (response.error.code != undefined)
                html += response.error.code +"<br/>";
            if (response.error.message != undefined)
                html += response.error.message +"<br/>";
            html += "</p>";
            this.$el.find('.error_message').html(html);
            return html;
        }
    });

    core.action_registry.add("stripe_checkout", stripe_checkout);
    return stripe_checkout;
});

