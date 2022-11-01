odoo.define('opt_appointment.DashboardModel', function (require) {
    "use strict";

    var AbstractModel = require('web.AbstractModel');
    var fieldUtils = require('web.field_utils');
    var Context = require('web.Context');
    var session = require('web.session');
    var time = require('web.time');
    var core = require('web.core');
    var _t = core._t;

    var scales = [
        'day',
        'week',
        'month'
    ];

    function dateToServer (date, self) {
        return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
    }

    var DashboardModel = AbstractModel.extend({
        init: function() {
            this._super.apply(this, arguments);
            this.end_date = null;
            var week_start = _t.database.parameters.week_start;
            // calendar uses index 0 for Sunday but Odoo stores it as 7
            this.week_start = week_start !== undefined && week_start !== false ? week_start % 7 : moment().startOf('week').day();
            this.week_stop = this.week_start + 6;
            this.filterId = false
        },
        setFilter:function(filter){
            this.filterId = filter;
        },
        calendarEventToRecord: function (event) {
            // Normalize event_end without changing fullcalendars event.
            var data = {'name': event.title};
            var start = event.start.clone();
            var end = event.end && event.end.clone();

            // Detects allDay events (86400000 = 1 day in ms)
            if (event.allDay || (end && end.diff(start) % 86400000 === 0)) {
                event.allDay = true;
            }

            // Set end date if not existing
            if (!end || end.diff(start) < 0) { // undefined or invalid end date
                if (event.allDay) {
                    end = start.clone();
                } else {
                    // in week mode or day mode, convert allday event to event
                    end = start.clone().add(2, 'h');
                }
            } else if (event.allDay) {
                // For an "allDay", FullCalendar gives the end day as the
                // next day at midnight (instead of 23h59).
                end.add(-1, 'days');
            }

            var isDateEvent = this.fields[this.mapping.date_start].type === 'date';
            var keepRecordTime = !this.mapping.all_day || (this.data.scale === 'month' && event.record && !event.record[this.mapping.all_day]);
            // An "allDay" event without the "all_day" option is not considered
            // as a 24h day. It's just a part of the day (by default: 7h-19h).
            if (event.allDay) {
                if (keepRecordTime && !isDateEvent) {
                    if (event.r_start) {
                        start.hours(event.r_start.hours())
                             .minutes(event.r_start.minutes())
                             .seconds(event.r_start.seconds())
                             .utc();
                        end.hours(event.r_end.hours())
                           .minutes(event.r_end.minutes())
                           .seconds(event.r_end.seconds())
                           .utc();
                    } else {
                        // default hours in the user's timezone
                        start.hours(7);
                        end.hours(19);
                    }
                    start.add(-this.getSession().getTZOffset(start), 'minutes');
                    end.add(-this.getSession().getTZOffset(end), 'minutes');
                }
            } else {
                start.add(-this.getSession().getTZOffset(start), 'minutes');
                end.add(-this.getSession().getTZOffset(end), 'minutes');
            }

            if (this.mapping.all_day) {
                if (event.record) {
                    data[this.mapping.all_day] =
                        (this.data.scale !== 'month' && event.allDay) ||
                        event.record[this.mapping.all_day] &&
                        end.diff(start) < 10 ||
                        false;
                } else {
                    data[this.mapping.all_day] = event.allDay;
                }
            }

            data[this.mapping.date_start] = start;
            if (this.mapping.date_stop) {
                data[this.mapping.date_stop] = end;
            }

            if (this.mapping.date_delay) {
                if (this.data.scale !== 'month' || (this.data.scale === 'month' && !event.drop)) {
                    data[this.mapping.date_delay] = (end.diff(start) <= 0 ? end.endOf('day').diff(start) : end.diff(start)) / 1000 / 3600;
                }
            }
            return data;
        },
        /**
         * @param {Object} filter
         * @returns {boolean}
         */
        changeFilter: function (filter) {
            var Filter = this.data.filters[filter.fieldName];
            if (filter.value === 'all') {
                Filter.all = filter.active;
            }
            var f = _.find(Filter.filters, function (f) {
                return f.value === filter.value;
            });
            if (f) {
                if (f.active !== filter.active) {
                    f.active = filter.active;
                } else {
                    return false;
                }
            } else if (filter.active) {
                Filter.filters.push({
                    value: filter.value,
                    active: true,
                });
            }
            return true;
        },
        /**
         * @param {OdooEvent} event
         */
        createRecord: function (event) {
            var data = this.calendarEventToRecord(event.data.data);
            for (var k in data) {
                if (data[k] && data[k]._isAMomentObject) {
                    data[k] = dateToServer(data[k],this);
                }
            }
            return this._rpc({
                    model: this.modelName,
                    method: 'create',
                    args: [data],
                    context: event.data.options.context,
                });
        },

        get: function () {
            return _.extend({}, this.data, {
                fields: this.fields
            });
        },
    /**
     * @override
     * @param {any} params
     * @returns {Promise}
     */
    load: function (params) {
        var self = this;
        this.modelName = params.modelName;
        this.fields = params.fields;
        this.fieldNames = params.fieldNames;
        this.fieldsInfo = params.fieldsInfo;
        this.mapping = params.mapping;
        this.mode = params.mode;       // one of month, week or day
        this.scales = params.scales;   // one of month, week or day

        // Check whether the date field is editable (i.e. if the events can be
        // dragged and dropped)
        this.editable = params.editable;
        this.creatable = params.creatable;

        // display more button when there are too much event on one day
        this.eventLimit = params.eventLimit;

        // fields to display color, e.g.: user_id.partner_id
        this.fieldColor = params.fieldColor;
        if (!this.preloadPromise) {
            this.preloadPromise = new Promise(function (resolve, reject) {
                Promise.all([
                    self._rpc({model: self.modelName, method: 'check_access_rights', args: ["write", false]}),
                    self._rpc({model: self.modelName, method: 'check_access_rights', args: ["create", false]}),
                    self._rpc({model: 'appointments.hours', method: 'get_appointment_hours_details', args : [[], moment(new Date()).clone().day()]
                              }).then(function (resources) {
                                    if (resources.length){
                                        if (resources[0].default_view == 'week'){
                                            self.default_view += 'Week';
                                            self.setScale('week');
                                        }
                                    }
                                })
                ]).then(function (result) {
                    var write = result[0];
                    var create = result[1];
                    self.write_right = write;
                    self.create_right = create;
                    resolve();
                }).guardedCatch(reject);
            });
        }

        this.data = {
            domain: params.domain,
            context: params.context,
            // get in arch the filter to display in the sidebar and the field to read
            filters: params.filters,
            resources : [],
        };
        this.setDate(params.initialDate);
        // Use mode attribute in xml file to specify zoom timeline (day,week,month)
        // by default month.
        this.setScale(params.mode);

        _.each(this.data.filters, function (filter) {
            if (filter.avatar_field && !filter.avatar_model) {
                filter.avatar_model = self.modelName;
            }
        });

        return this.preloadPromise.then(this._loadCalendar.bind(this));
    },

    next: function () {
        this.setDate(this.data.target_date.clone().add(1, this.data.scale));
    },

    prev: function () {
        this.setDate(this.data.target_date.clone().add(-1, this.data.scale));
    },
    redirect_month: function (month) {
        let date = new Date();
        this.setDate(moment(date.setMonth(date.getMonth() + month)));
    },

    reload: function (handle, params) {
        if (params.domain) {
            this.data.domain = params.domain;
        }
        if (params.context) {
            this.data.context = params.context;
        }
        return this._loadCalendar();
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
                    monthStartDay = this.week_start;
                } else {
                    monthStartDay = this.week_start - 7;
                }

                this.data.start_date = monthStart.day(monthStartDay).startOf('day');
                this.data.end_date = this.data.start_date.clone().add(5, 'week').day(this.week_stop).endOf('day');
                break;
            case 'week':
                var weekStart = this.data.start_date.clone().startOf('week');
                var weekStartDay = this.week_start;
                if (this.data.start_date.day() < this.week_start) {
                    weekStartDay -= 7;
                }
                this.data.start_date = this.data.start_date.clone().day(weekStartDay).startOf('day');
                this.data.end_date = this.data.end_date.clone().day(weekStartDay + 6).endOf('day');
                break;
            default:
                this.data.start_date = this.data.start_date.clone().startOf('day');
                this.data.end_date = this.data.end_date.clone().endOf('day');
        }
        var manualUtcDateStart = this.data.start_date.clone().add(-this.getSession().getTZOffset(this.data.start_date), 'minutes');
//        var formattedUtcDateStart = this.data.start_date.clone().format('YYYY-MM-DDTHH:mm:ss') + 'Z';
        var formattedUtcDateStart = manualUtcDateStart.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
        this.data.start_date = moment.utc(formattedUtcDateStart);

        var manualUtcDateEnd = this.data.end_date.clone().add(-this.getSession().getTZOffset(this.data.start_date), 'minutes');
//        var formattedUtcDateEnd = this.data.end_date.clone().format('YYYY-MM-DDTHH:mm:ss') + 'Z';
        var formattedUtcDateEnd = manualUtcDateEnd.format('YYYY-MM-DDTHH:mm:ss') + 'Z';
        this.data.end_date = moment.utc(formattedUtcDateEnd);
    },

    setScale: function (scale) {
        if (!_.contains(scales, scale)) {
            scale = "day";
        }
        this.data.scale = scale;
        this.setDate(this.data.target_date);
    },

    today: function () {
        this.setDate(moment(new Date()));
    },

    updateRecord: function (records) {
        // Cannot modify actual name yet
        var data = _.omit(this.calendarEventToRecord(records), 'name');
        var record = data["start"];
        if (record._d.toString().substr(28,1) == "+")
            data["local_start_datetime"] = record.clone().hour(record.hour() + parseInt(record._d.toString().substr(29,2))).minute(record.minute() +
                                                    parseInt(record._d.toString().substr(31,2))).format(time.getLangDatetimeFormat());
        else
            data["local_start_datetime"] = record.clone().hour(record.hour() - parseInt(record._d.toString().substr(29,2))).minute(record.minute() -
                                                    parseInt(record._d.toString().substr(31,2))).format(time.getLangDatetimeFormat());
        for (var k in data) {
            if (data[k] && data[k]._isAMomentObject) {
                data[k] = dateToServer(data[k],this);
            }
        }
        var context = new Context(this.data.context, {from_ui: true});
        return this._rpc({
            model: 'calendar.event',
            method: 'appointment_rescheduled',
            args: [[records.id], [records.id], data],
            context: context
        });
    },

    _getFilterDomain: function () {
        // List authorized values for every field
        // fields with an active 'all' filter are skipped
        var authorizedValues = {};
        var avoidValues = {};

        _.each(this.data.filters, function (filter) {
            // Skip 'all' filters because they do not affect the domain
            if (filter.all) return;

            // Loop over subfilters to complete authorizedValues
            _.each(filter.filters, function (f) {
                if (filter.write_model) {
                    if (!authorizedValues[filter.fieldName])
                        authorizedValues[filter.fieldName] = [];

                    if (f.active) {
                        authorizedValues[filter.fieldName].push(f.value);
                    }
                } else {
                    if (!f.active) {
                        if (!avoidValues[filter.fieldName])
                            avoidValues[filter.fieldName] = [];

                        avoidValues[filter.fieldName].push(f.value);
                    }
                }
            });
        });

        // Compute the domain
        var domain = [];
        for (var field in authorizedValues) {
            domain.push([field, 'in', authorizedValues[field]]);
        }
        for (var field in avoidValues) {
            if (avoidValues[field].length > 0) {
                domain.push([field, 'not in', avoidValues[field]]);
            }
        }

        return domain;
    },

    _getFullCalendarOptions: function () {
        return {
            defaultView: "agendaDay",
            header: false,
            selectable: this.creatable && this.create_right,
            selectHelper: true,
            editable: this.editable,
            droppable: true,
            navLinks: false,
            eventLimit: this.eventLimit, // allow "more" link when too many events
            snapMinutes: 15,
            longPressDelay: 500,
            eventResizableFromStart: true,
            nowIndicator: true,
//            weekNumbers: true,
//            weekNumbersWithinDays: true,
//            weekNumberTitle: _t("Week") + " ",
            allDayText: _t("All day"),
            monthNames: moment.months(),
            monthNamesShort: moment.monthsShort(),
//            dayNames: moment.weekdays(),
//            dayNamesShort: moment.weekdaysShort(),
//            firstDay: this.week_start,
            slotLabelFormat: _t.database.parameters.time_format.search("%H") != -1 ? 'H:mm': 'h(:mm)a',
        };
    },

    _getRangeDomain: function () {
        var domain = [[this.mapping.date_start, '<=', dateToServer(this.data.end_date,this)]];
        if (this.mapping.date_stop) {
            domain.push([this.mapping.date_stop, '>=', dateToServer(this.data.start_date,this)]);
        } else if (!this.mapping.date_delay) {
            domain.push([this.mapping.date_start, '>=', dateToServer(this.data.start_date,this)]);
        }
        return domain;
    },
    /**
     * @private
     * @returns {Promise}
     */
    _loadCalendar: function () {
        var self = this;
        this.data.fc_options = this._getFullCalendarOptions();

        var defs = _.map(this.data.filters, this._loadFilter.bind(this));
        return Promise.all(defs).then(function () {
            var domain = self._getRangeDomain().concat(self._getFilterDomain());
            if(self.filterId.state && self.filterId.state.length > 0){
                domain.push(['confirmation_status' , 'in', self.filterId.state])
            }
            domain.push(['appointment_type' , '=', 'appointment'])

//            if(self.filterId.company && self.filterId.company.length > 0){
//                domain.push(['company_id' , 'in', self.filterId.company])
//            }
            domain.push(['appointment_status' , 'not in', ['cancel', 'rescheduled']])
            //console.log('domain::::::::', domain)
            self.date_domain = [];
            return self._rpc({
                    model: 'calendar.event',
                    method: 'return_values',
                    context: self.data.context,
                    args : [[], domain, self.date_domain.concat(self._getRangeDomain()).concat(self._getFilterDomain()),self.filterId.employee,moment(new Date()).clone().day()]
            })
            .then(function (events) {
                self._parseServerData(events);
                self.data.data = _.map(events, self._recordToCalendarEvent.bind(self));
                return Promise.all([self._loadResource()]);
            });
        });
    },
    _loadResource : function(){
        var self = this;
        self.date_domain = []
        return this._rpc({
            model: this.modelName,
            method: 'get_appointment_booking_datas',
            args : [[], this.filterId.employee, this.filterId.status, this.filterId.company, self.date_domain.concat(self._getRangeDomain()).concat(self._getFilterDomain()),self.data.end_date._d.getDay()]
        })
        .then(function (resources) {
            var currentDate = moment(self.data.highlight_date).utc(true);
            var weekStart = currentDate.clone().startOf('isoweek');

            var days = {};
            for (var i = 0; i <= 6; i++) {
                let date = moment(weekStart).subtract(1, "days").add(i, 'days').format('YYYY-MM-DD');
                days[moment(date).format('dddd')] = moment(weekStart).subtract(1, "days").add(i, 'days').format('YYYY-MM-DD');
            }
             self.data.resources = resources[0];
             self.data.more_resources = resources[2];
             self.data.selected_company = resources[3];
             self.data.off_events = resources[4];
             self.data.on_events = resources[5];
             self.data.resourcesIds = _.pluck(resources[0], 'id') ;
             var eventList = [];
              _.each(resources[1],function(event) {
                      event['start'] = moment(days[event.day] + ' ' + event.start).format("YYYY-MM-DDTHH:mm:ss");
                      event['end'] = moment(days[event.day]+ ' ' + event.end).format("YYYY-MM-DDTHH:mm:ss");
                      eventList.push(event);
             });
             self.data.events = eventList;
             self.data.timezone = resources[6];

             return Promise.resolve();
        });
    },

    _loadFilter: function (filter) {
        if (!filter.write_model) {
            return Promise.resolve();
        }

        var field = this.fields[filter.fieldName];
        return this._rpc({
                model: filter.write_model,
                method: 'search_read',
                domain: [["user_id", "=", session.uid]],
                fields: [filter.write_field],
            })
            .then(function (res) {
                var records = _.map(res, function (record) {
                    var _value = record[filter.write_field];
                    var value = _.isArray(_value) ? _value[0] : _value;
                    var f = _.find(filter.filters, function (f) {return f.value === value;});
                    var formater = fieldUtils.format[_.contains(['many2many', 'one2many'], field.type) ? 'many2one' : field.type];
                    return {
                        'id': record.id,
                        'value': value,
                        'label': formater(_value, field),
                        'active': !f || f.active,
                    };
                });
                records.sort(function (f1,f2) {
                    return _.string.naturalCmp(f2.label, f1.label);
                });

                // add my profile
                if (field.relation === 'res.partner' || field.relation === 'res.users') {
                    var value = field.relation === 'res.partner' ? session.partner_id : session.uid;
                    var me = _.find(records, function (record) {
                        return record.value === value;
                    });
                    if (me) {
                        records.splice(records.indexOf(me), 1);
                    } else {
                        var f = _.find(filter.filters, function (f) {return f.value === value;});
                        me = {
                            'value': value,
                            'label': session.name + _t(" [Me]"),
                            'active': !f || f.active,
                        };
                    }
                    records.unshift(me);
                }
                // add all selection
                records.push({
                    'value': 'all',
                    'label': field.relation === 'res.partner' || field.relation === 'res.users' ? _t("Everybody's calendars") : _t("Everything"),
                    'active': filter.all,
                });

                filter.filters = records;
            });
    },

    _parseServerData: function (data) {
        var self = this;
        _.each(data, function(event) {
            _.each(self.fieldNames, function (fieldName) {
                event[fieldName] = self._parseServerValue(self.fields[fieldName], event[fieldName]);
            });
        });
    },

    _recordToCalendarEvent: function (evt) {
        var date_start;
        var date_stop;
        var date_delay = evt[this.mapping.date_delay] || 1.0,
            all_day = this.fields[this.mapping.date_start].type === 'date' ||
                this.mapping.all_day && evt[this.mapping.all_day] || false,
            the_title = '',
            attendees = [];

        if (!all_day) {
            date_start = evt[this.mapping.date_start].clone();
            date_stop = this.mapping.date_stop ? evt[this.mapping.date_stop].clone() : null;
        } else {
            date_start = evt[this.mapping.date_start].clone().startOf('day');
            date_stop = this.mapping.date_stop ? evt[this.mapping.date_stop].clone().startOf('day') : null;
        }

        if (!date_stop && date_delay) {
            date_stop = date_start.clone().add(date_delay,'hours');
        }

//        if (!all_day) {
//            date_start.add(this.getSession().getTZOffset(date_start), 'minutes');
//            date_stop.add(this.getSession().getTZOffset(date_stop), 'minutes');
//        }

        if (this.mapping.all_day && evt[this.mapping.all_day]) {
            date_stop.add(1, 'days');
        }
        var r = {
            'backgroundColor': evt.backgroundColor,
//            'backgroundColor': 'black',
            'record': evt,
            'start': date_start,
            'end': date_stop,
            'resourceId' : evt.employee_id[0],
            'r_start': date_start,
            'r_end': date_stop,
            'title': the_title,
            'allDay': all_day,
            'start_datetime': evt.start_datetime,
            'id': evt.id,
            'attendees':attendees,
        };

        if (this.mapping.all_day && evt[this.mapping.all_day]) {
             r.start = date_start.format('YYYY-MM-DD');
             r.end = date_stop.format('YYYY-MM-DD');
        } else if (this.data.scale === 'month' && this.fields[this.mapping.date_start].type !== 'date') {
            // In month, FullCalendar gives the end day as the
            // next day at midnight (instead of 23h59).
            r.end = date_stop.clone().add(1, 'days').startOf('day').format('YYYY-MM-DD');
            r.start = date_start.clone().format('YYYY-MM-DD');

            // allow to resize in month mode
            r.reset_allday = r.allDay;
            r.allDay = true;
        }

        return r;
    },
    reload: function (handle, params) {
        if (params.domain) {
            this.data.domain = params.domain;
        }
        if (params.context) {
            this.data.context = params.context;
        }
        return this._loadCalendar();
    },
    });

    return DashboardModel;

});
