odoo.define('ivis_order_grouping.Dialog', function (require) {
"use strict";

    var Dialog = require('web.Dialog');
    var ActionManager = require('web.ActionManager');
    var RelationalFields = require('web.relational_fields');
    var FieldMany2One = RelationalFields.FieldMany2One;
    var dialogs = require('web.view_dialogs');
    var dom = require('web.dom');

    FieldMany2One.include({
        _searchCreatePopup: function (view, ids, context, dynamicFilters) {
            var options = this._getSearchCreatePopupOptions(view, ids, context, dynamicFilters);
            if ('new_size' in options.context)
                options.new_size = options.context.new_size;
            return new dialogs.SelectCreateDialog(this, _.extend({}, this.nodeOptions, options)).open();
        },
    });

    ActionManager.include({
        _executeActionInDialog: function (action, options) {
            var self = this;
            var controller = this.controllers[action.controllerID];
            var widget = controller.widget;

            return this._startController(controller).then(function (controller) {
                var prevDialogOnClose;
                if (self.currentDialogController) {
                    prevDialogOnClose = self.currentDialogController.onClose;
                    self._closeDialog({ silent: true });
                }

                controller.onClose = prevDialogOnClose || options.on_close;
                var dialog;
                if ('new_size' in action.context)
                    dialog = new Dialog(self, _.defaults({}, options, {
                        buttons: [],
                        dialogClass: controller.className,
                        title: action.name,
                        size: action.context.dialog_size,
                        new_size: action.context.new_size,
                    }));
                else
                    dialog = new Dialog(self, _.defaults({}, options, {
                        buttons: [],
                        dialogClass: controller.className,
                        title: action.name,
                        size: action.context.dialog_size,
                    }));
                /**
                 * @param {Object} [options={}]
                 * @param {Object} [options.infos] if provided and `silent` is
                 *   unset, the `on_close` handler will pass this information,
                 *   which gives some context for closing this dialog.
                 * @param {boolean} [options.silent=false] if set, do not call the
                 *   `on_close` handler.
                 */
                dialog.on('closed', self, function (options) {
                    options = options || {};
                    self._removeAction(action.jsID);
                    self.currentDialogController = null;
                    if (options.silent !== true) {
                        controller.onClose(options.infos);
                    }
                });
                controller.dialog = dialog;

                return dialog.open().opened(function () {
                    self.currentDialogController = controller;

                    dom.append(dialog.$el, widget.$el, {
                        in_DOM: true,
                        callbacks: [{widget: dialog}, {widget: controller.widget}],
                    });
                    widget.renderButtons(dialog.$footer);
                    dialog.rebindButtonBehavior();

                    return action;
                });
            }).guardedCatch(function () {
                self._removeAction(action.jsID);
            });
        },
    });

    Dialog.include({
        init: function (parent, options) {
            this._super(parent, options);
            if ('new_size' in options)
                this.new_size = options.new_size;
            else if (options.context != undefined && 'new_size' in options.context)
                this.new_size = options.context.new_size;
            else
                this.new_size = undefined;
        },

        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.new_size != undefined && self.new_size.includes('_')){
                    var new_size = self.new_size.split('_');
                    self.$modal.find('.modal-dialog').css(new_size[0], new_size[1]);
                }
            });
        },

   });

});