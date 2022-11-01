odoo.define('patient_engagement.two_way_texting_systray', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;


    var NotificationMenu = Widget.extend({
        name: 'twilio_notifications_menu',
        template:'systray.twilio.NotificationsMenu',
        events: {
            'click .twilio_notification': '_OpenClientAction',
        },
        start: function () {
            this.counter = 0;
            var mailBus = this.call('mail_service', 'getMailBus');
            mailBus.on('twilio_notification_updated', this, this._updateCounter);
//            this.call('mail_service', 'getMailBus').trigger('twilio_notification_updated', {message_received: 1});
//            this.call('mail_service', 'getMailBus').trigger('twilio_notification_updated', {message_seen: 1});
            this._getCounter();
            return this._super();
        },
        _updateCounter: function (data) {
            if (data) {
                if (data.message_received) {
                    this.counter += data.message_received;
                }
                if (data.message_seen) {
                    this.counter -= data.message_seen;
                    if (this.counter < 0)
                        this.counter = 0;
                }
                this.$('.o_notification_counter').text(this.counter);
            }
        },
        _OpenClientAction: function () {
            this.do_action({
                tag: 'two_way_texting_twilio',
                target: 'fullscreen',
                type: 'ir.actions.client',
            });
        },
        _getCounter: function (data) {
            var self = this;
            return self._rpc({
                model: 'messaging.history',
                method: 'systray_get_notifications',
                args: [[]],
            }).then(function (data) {
                self.$('.o_notification_counter').text(data);
            });
        },

    });

    SystrayMenu.Items.push(NotificationMenu);

    return NotificationMenu;

});
