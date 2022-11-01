odoo.define('opt_appointment.ListModel', function (require) {
"use strict";

    var session = require('web.session');
    var ListModel = require('web.ListModel');
    var core = require('web.core');
    var _t = core._t;

    var scales = [
        'day',
        'week',
        'month'
    ];

    ListModel.include({
        init: function (parent, params) {
            this._super.apply(this, arguments);
//            if (params.action.xml_id == 'opt_appointment.action_calendar_event_appointment')
                this.data = {};
                this.data.scale = 'day';
                this.setDate(moment(new Date()));
            this.end_date = null;
            var week_start = _t.database.parameters.week_start;
            // calendar uses index 0 for Sunday but Odoo stores it as 7
            this.week_start = week_start !== undefined && week_start !== false ? week_start % 7 : moment().startOf('week').day();
            this.week_stop = this.week_start + 6;

        },
        /**
         * Move the current date range to the next period
         */
        next: function () {
            this.setDate(this.data.target_date.clone().add(1, this.data.scale));
        },
        /**
         * Move the current date range to the previous period
         */
        prev: function () {
            this.setDate(this.data.target_date.clone().add(-1, this.data.scale));
        },
        /**
         * Move the current date range to the period containing today
         */
        today: function () {
            this.setDate(moment(new Date()));
        },
        setScale: function (scale) {
            if (!_.contains(scales, scale)) {
                scale = "day";
            }
            this.data.scale = scale;
            this.setDate(this.data.target_date);
        },
        /**
         * @param {Moment} start. in local TZ
         */
        setDate: function (start) {
            // keep highlight/target_date in localtime
            this.data.highlight_date = this.data.target_date = start.clone();
            this.data.start_date = this.data.end_date = start;
            switch (this.data.scale) {
                case 'month':
                    var monthStart = this.data.start_date.clone().startOf('month');

                    var monthStartDay;
                    if (monthStart.day() >= this.week_start) {
                        // the month's first day is after our week start
                        // Then we are in the right week
                        monthStartDay = this.week_start;
                    } else {
                        // The month's first day is before our week start
                        // Then we should go back to the the previous week
                        monthStartDay = this.week_start - 7;
                    }

                    this.data.start_date = monthStart.day(monthStartDay).startOf('day');
                    this.data.end_date = this.data.start_date.clone().add(1, 'month').day(this.week_stop).endOf('day');
                    break;
                case 'week':
                    var weekStart = this.data.start_date.clone().startOf('week');
                    var weekStartDay = this.week_start;
                    if (this.data.start_date.day() < this.week_start) {
                        // The week's first day is after our current day
                        // Then we should go back to the previous week
                        weekStartDay -= 7;
                    }
                    this.data.start_date = this.data.start_date.clone().day(weekStartDay).startOf('day');
                    this.data.end_date = this.data.end_date.clone().day(weekStartDay + 6).endOf('day');
                    break;
                default:
                    this.data.start_date = this.data.start_date.clone().startOf('day');
                    this.data.end_date = this.data.end_date.clone().endOf('day');
            }
            // We have set start/stop datetime as definite begin/end boundaries of a period (month, week, day)
            // in local TZ (what is the begining of the week *I am* in ?)
            // The following code:
            // - converts those to UTC using our homemade method (testable)
            // - sets the moment UTC flag to true, to ensure compatibility with third party libs
            var manualUtcDateStart = this.data.start_date.clone().add(-this.getSession().getTZOffset(this.data.start_date), 'minutes');
            var formattedUtcDateStart = manualUtcDateStart.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
            this.data.start_date = moment.utc(formattedUtcDateStart);

            var manualUtcDateEnd = this.data.end_date.clone().add(-this.getSession().getTZOffset(this.data.start_date), 'minutes');
            var formattedUtcDateEnd = manualUtcDateEnd.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
            this.data.end_date = moment.utc(formattedUtcDateEnd);
        },

    });

});