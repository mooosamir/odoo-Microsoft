odoo.define('opt_appointment.DashboardController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    var config = require('web.config');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    var DashboardController = AbstractController.extend({
        renderButtons: function ($node) {
            var self = this;
            this.$buttons = $(QWeb.render('ResourceView.buttons', {
                isMobile: config.device.isMobile,
            }));
            this.$buttons.on('click', 'button.o_calendar_button_new', function () {
                self.trigger_up('switch_view', {view_type: 'form'});
            });

            _.each(['prev', 'today', 'next'], function (action) {
                self.$buttons.on('click', '.o_calendar_button_' + action, function () {
                    self._move(action);
                });
            });
            _.each(['day', 'week', 'month'], function (scale) {
                self.$buttons.on('click', '.o_calendar_button_' + scale, function () {
                    self.model.setScale(scale);
                    self.reload();
                });
            });

            this.$buttons.find('.o_calendar_button_' + this.mode).addClass('active');

            if ($node) {
                this.$buttons.appendTo($node);
            } else {
                this.$('.o_calendar_buttons').replaceWith(this.$buttons);
            }
        },
    });

    return DashboardController;

});
