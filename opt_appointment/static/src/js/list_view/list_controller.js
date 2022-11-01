odoo.define('opt_appointment.ListController', function (require) {
"use strict";

    var core = require('web.core');
    var config = require('web.config');
    var _t = core._t;
    var qweb = core.qweb;

    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function ($node) {
            if (this.modelName == "calendar.event" && this._title == "Appointment"){
                var self = this;
                this.$buttons = $(qweb.render('CalendarView.buttons', {
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
                        var domain = {};
                        if (self.model.data.domain !== undefined)
                            domain = self.model.data.domain
                        var params = {
                            'context': {},
                            'domain': domain,
                            'groupBy': [],
                            'groupsOffset': 0,
                            'offset': 0,
                            'orderedBy': undefined,
                        }
                        self.reload(params);
                    });
                });

                this.$buttons.find('.o_calendar_button_' + this.mode).addClass('active');

                if ($node) {
                    this.$buttons.appendTo($node);
                } else {
                    this.$('.o_calendar_buttons').replaceWith(this.$buttons);
                }

                var domain = {};
                if (this.model.data.domain !== undefined)
                    domain = this.model.data.domain
                var params = {
                    'context': {},
                    'domain': domain,
                    'groupBy': [],
                    'groupsOffset': 0,
                    'offset': 0,
                    'orderedBy': undefined,
                }
                this.reload(params);

            }
            else{
                this._super.apply(this, arguments);
            }
        },
        _move: function (to) {
            this.model[to]();
            var domain = {};
            if (this.model.data.domain !== undefined)
                domain = this.model.data.domain

            var params = {
                'context': {},
                'domain': domain,
                'groupBy': [],
                'groupsOffset': 0,
                'offset': 0,
                'orderedBy': undefined,
            }
            return this.reload(params);
        },
        update: function (params, options) {
            if (this.modelName == "calendar.event" && this._title == "Appointment"){
                if (!$.isEmptyObject(params) && !$.isEmptyObject(params.domain))
                    this.model.data.domain = Array.from(params.domain);
                if ($.isEmptyObject(params.domain)){
                    this.model.data.domain = Array.from(this.initialState.domain);
                    params.domain = Array.from(this.initialState.domain);
                }
                params.domain.push(["start_datetime", ">", this.model.data.start_date._d]);
                params.domain.push(["start_datetime", "<", this.model.data.end_date._d]);
                return this._super.apply(this, arguments);
            }
            else{
                return this._super.apply(this, arguments);
            }
       },

    });

});