odoo.define('acs_consent_form.signature_form', function (require) {
'use strict';

    var core = require('web.core');
    var signature_form = require('portal.signature_form').SignatureForm;
    var qweb = core.qweb;

    var _t = core._t;

    /**
     * This widget is a signature request form. It uses
     * @see NameAndSignature for the input fields, adds a submit
     * button, and handles the RPC to save the result.
     */
    signature_form.include({
        /**
         * Handles click on the submit button.
         *
         * This will get the current name and signature and validate them.
         * If they are valid, they are sent to the server, and the reponse is
         * handled. If they are invalid, it will display the errors to the user.
         *
         * @private
         * @param {Event} ev
         * @returns {Deferred}
         */
        _onClickSignSubmit: function (ev) {
            var self = this;
            ev.preventDefault();

            if (!this.nameAndSignature.validateSignature()) {
                return;
            }

            var name = this.nameAndSignature.getName();
            var signature = this.nameAndSignature.getSignatureImage()[1];

            return this._rpc({
                route: this.callUrl,
                params: _.extend(this.rpcParams, {
                    'name': name,
                    'signature': signature,
                }),
            }).then(function (data) {
                if (data.error) {
                    self.$('.o_portal_sign_error_msg').remove();
                    self.$controls.prepend(qweb.render('portal.portal_signature_error', {widget: data}));
                } else if (data.success) {
                    var $success = qweb.render('portal.portal_signature_success', {widget: data});
                    self.$el.empty().append($success);
                }
                if (data.force_refresh) {
                    if (data.history_back) {
                        history.back();
                    }else if (data.redirect_url) {
                        window.location = data.redirect_url;
                    } else {
                        window.location.reload();
                    }
                    // no resolve if we reload the page
                    return new Promise(function () { });
                }
            });
        },


    });
});