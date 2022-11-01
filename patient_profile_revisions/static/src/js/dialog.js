odoo.define('patient_profile_revisions.Dialog', function (require) {
"use strict";

    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var _t = core._t;

    Dialog.include({
        init: function (parent, options) {
            options['title'] = _t('Got2');
            this._super(parent, options);
        },
    });
    // static method to open simple confirm dialog
    Dialog.confirm = function (owner, message, options) {
        if (options.confirm_text == false || options.confirm_text == undefined)
            options.confirm_text = _t("OK")
        if (options.cancel_text == false || options.cancel_text == undefined)
            options.cancel_text = _t("Cancel")
        var buttons = [
            {
                text: options.confirm_text,
                classes: 'btn-primary',
                close: true,
                click: options && options.confirm_callback,
            },
            {
                text: options.cancel_text,
                close: true,
                click: options && options.cancel_callback
            }
        ];
        return new Dialog(owner, _.extend({
            size: 'medium',
            buttons: buttons,
            $content: $('<main/>', {
                role: 'alert',
                text: message,
            }),
            title: _t("Confirmation"),
            onForceClose: options && (options.onForceClose || options.cancel_callback),
        }, options)).open({shouldFocusButtons:true});
    };
    // static method to open simple alert dialog
    Dialog.alert = function (owner, message, options) {
        var buttons = [{
            text: _t("OK"),
            close: true,
            click: options && options.confirm_callback,
        }];
        return new Dialog(owner, _.extend({
            size: 'medium',
            buttons: buttons,
            $content: $('<main/>', {
                role: 'alert',
                text: message,
            }),
            title: _t("Alert"),
            onForceClose: options && (options.onForceClose || options.confirm_callback),
        }, options)).open({shouldFocusButtons:true});
    };
    /**
     * Static method to open double confirmation dialog.
     *
     * @param {Widget} owner
     * @param {string} message
     * @param {Object} [options] @see Dialog.init @see Dialog.confirm
     * @param {string} [options.securityLevel="warning"] - bootstrap color
     * @param {string} [options.securityMessage="I am sure about this"]
     * @returns {Dialog} (open() is automatically called)
     */
    Dialog.safeConfirm = function (owner, message, options) {
        var $checkbox = dom.renderCheckbox({
            text: options && options.securityMessage || _t("I am sure about this."),
        }).addClass('mb0');
        var $securityCheck = $('<div/>', {
            class: 'alert alert-' + (options && options.securityLevel || 'warning') + ' mt8 mb0',
        }).prepend($checkbox);
        var $content;
        if (options && options.$content) {
            $content = options.$content;
            delete options.$content;
        } else {
            $content = $('<div>', {
                text: message,
            });
        }
        $content = $('<main/>', {role: 'alert'}).append($content, $securityCheck);

        var buttons = [
            {
                text: _t("OK"),
                classes: 'btn-primary o_safe_confirm_button',
                close: true,
                click: options && options.confirm_callback,
                disabled: true,
            },
            {
                text: _t("Cancel"),
                close: true,
                click: options && options.cancel_callback
            }
        ];
        var dialog = new Dialog(owner, _.extend({
            size: 'medium',
            buttons: buttons,
            $content: $content,
            title: _t("Confirmation"),
            onForceClose: options && (options.onForceClose || options.cancel_callback),
        }, options));
        dialog.opened(function () {
            var $button = dialog.$footer.find('.o_safe_confirm_button');
            $securityCheck.on('click', 'input[type="checkbox"]', function (ev) {
                $button.prop('disabled', !$(ev.currentTarget).prop('checked'));
            });
        });
        return dialog.open();
    };

});