odoo.define('opt_appointment.DashboardRenderer', function (require) {
    "use strict";
    var AbstractRenderer = require('web.AbstractRenderer');
    var config = require('web.config');
    var core = require("web.core");
    var time = require("web.time");
    var utils = require("web.utils");
    var session = require("web.session");
    var QWeb = require("web.QWeb");
    var field_utils = require("web.field_utils");
    var Widget = require('web.Widget');
    var CalendarPopover = require('opt_appointment.ResourcePopover');
    var Dialog = require('web.Dialog');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var relational_fields = require('web.relational_fields');
    var Widget = require('web.Widget');
    var _t = core._t;
    var qweb = core.qweb;

    var scales = {
        day: 'agendaDay',
        week: 'agendaWeek',
        month: 'month'
    };
    var DashboardRenderer = AbstractRenderer.extend({
        template: "ResourceView",
        custom_events: _.extend({}, AbstractRenderer.prototype.custom_events || {}, {
            edit_event: '_onEditEvent',
            delete_event: '_onDeleteEvent',
        }),
        config: {
            CalendarPopover: CalendarPopover,
        },
        init: function(parent, state, params) {
            var self = this;
            this._super.apply(this, arguments);
            this.displayFields = params.displayFields;
            this.model = params.model;
            this.filters = [];
            this.color_map = {};
            this.hideDate = params.hideDate;
            this.hideTime = params.hideTime;
            this.start_date = '00:00'
            this.end_date = '24:00';
            this.duration = '00:15:00';
            this.default_view = 'agenda';
            this.hiddenDays = [];
            $(window).resize(function(){
              self._set_dynamic_width();
            });
        },
        start: function () {
            var self = this;
            var self_again = this;
            var self_super = self._super();
            return self._rpc({
                model: 'appointments.hours',
                method: 'get_appointment_hours_details',
                args : [[], moment(new Date()).clone().day()]
            }).then(function (resources) {
                if (resources.length){
                    if (resources[0].default_view == 'week'){
                        self.default_view += 'Week';
//                        self.__parentedParent.model.setScale('week');
                    }
                    else
                        self.default_view += 'Day';
                    if (!resources[0].permanent_closed){
                        var time_1 = 0;
                        var time_2 = 0;
                        var hour_1 = 0;
                        var hour_2 = 0;
                        var minute_1 = 0;
                        var minute_2 = 0;
                        if (resources[0].opening_time.substr(6) == "PM")
                            time_1 = 12;
                        if (resources[0].closing_time.substr(6) == "PM")
                            time_2 = 12;
                        self.start_date = (parseInt(resources[0].opening_time.substr(0,2)) + time_1 - hour_1).toString() + ':' + (minute_1).toString();
                        self.end_date = (parseInt(resources[0].closing_time.substr(0,2)) + time_2 + hour_2).toString() + ':' + (minute_2).toString();
                        self.duration = '00:' + resources[0].duration_block;
                    }
                    if (resources[0].hide_saturday)
                        self.hiddenDays.push(6)
                    if (resources[0].hide_sunday)
                        self.hiddenDays.push(0)
                }
                self._initCalendarMini();
                self._initResourceCalendar();
                return self_again;
            });
        },

        _renderFiltersOneByOne: function (filterIndex) {
            filterIndex = filterIndex || 0;
            var arrFilters = _.toArray(this.state.filters);
            var prom;
            if (filterIndex < arrFilters.length) {
                var options = arrFilters[filterIndex];
                if (!_.find(options.filters, function (f) {return f.display == null || f.display;})) {
                    return this._renderFiltersOneByOne(filterIndex + 1);
                }

                var self = this;
                options.getColor = this.getColor.bind(this);
                options.fields = this.state.fields;
                var filter = new SidebarFilter(self, options);
                prom = filter.appendTo(this.$sidebar).then(function () {
                    // Show filter popover
                    if (options.avatar_field) {
                        _.each(options.filters, function (filter) {
                            if (filter.value !== 'all') {
                                var selector = _.str.sprintf('.o_calendar_filter_item[data-value=%s]', filter.value);
                                self.$sidebar.find(selector).popover({
                                    animation: false,
                                    trigger: 'hover',
                                    html: true,
                                    placement: 'top',
                                    title: filter.label,
                                    delay: {show: 300, hide: 0},
                                    content: function () {
                                        return $('<img>', {
                                            src: _.str.sprintf('/web/image/%s/%s/%s', options.avatar_model, filter.value, options.avatar_field),
                                            class: 'mx-auto',
                                        });
                                    },
                                });
                            }
                        });
                    }
                    return self._renderFiltersOneByOne(filterIndex + 1);
                });
                this.filters.push(filter);
            }
            return Promise.resolve(prom);
        },

        _getPopoverContext: function (eventData) {
            var context = {
                hideDate: this.hideDate,
                hideTime: this.hideTime,
                eventTime: {},
                eventDate: {},
                fields: this.state.fields,
                displayFields: this.displayFields,
                event: eventData,
                modelName: this.model,
            };

            var start = moment(eventData.r_start || eventData.start) //.tz(eventData.event_tz);
            var end = moment(eventData.r_end || eventData.end) //.tz(eventData.event_tz);
            var isSameDayEvent = start.clone().add(1, 'minute').isSame(end.clone().subtract(1, 'minute'), 'day');

            // Do not display timing if the event occur across multiple days. Otherwise use user's timing preferences
            if (!this.hideTime && !eventData.record.allday && isSameDayEvent) {
                // Fetch user's preferences
                var dbTimeFormat = _t.database.parameters.time_format.search('%H') != -1 ? 'HH:mm': 'hh:mm a';

                context.eventTime.time = start.clone().format(dbTimeFormat) + ' - ' + end.clone().format(dbTimeFormat);

                // Calculate duration and format text
                var durationHours = moment.duration(end.diff(start)).hours();
                var durationHoursKey = (durationHours === 1) ? 'h' : 'hh';
                var durationMinutes = moment.duration(end.diff(start)).minutes();
                var durationMinutesKey = (durationMinutes === 1) ? 'm' : 'mm';

                var localeData = moment.localeData(); // i18n for 'hours' and "minutes" strings
                context.eventTime.duration = (durationHours > 0 ? localeData.relativeTime(durationHours, true, durationHoursKey) : '')
                        + (durationHours > 0 && durationMinutes > 0 ? ', ' : '')
                        + (durationMinutes > 0 ? localeData.relativeTime(durationMinutes, true, durationMinutesKey) : '');
            }

            if (!this.hideDate) {
                if (eventData.record.allday && isSameDayEvent) {
                    context.eventDate.duration = _t("All day");
                } else if (eventData.record.allday && !isSameDayEvent) {
                    var daysLocaleData = moment.localeData();
                    var days = moment.duration(end.diff(start)).days();
                    context.eventDate.duration = daysLocaleData.relativeTime(days, true, 'dd');
                }

                if (eventData.allDay) {
                    // cancel correction done in _recordToCalendarEvent
                    end.subtract(1, 'day');
                }
                if (!isSameDayEvent && start.isSame(end, 'month')) {
                    // Simplify date-range if an event occurs into the same month (eg. '4-5 August 2019')
                    context.eventDate.date = start.clone().format('MMMM D') + '-' + end.clone().format('D, YYYY');
                } else {
                    context.eventDate.date = isSameDayEvent ? start.clone().format('dddd, LL') : start.clone().format('LL') + ' - ' + end.clone().format('LL');
                }
            }
            return context;
        },

        _onEditEvent: function (event) {
            this._unselectEvent();
            this.trigger_up('openEvent', {
                _id: event.data.id,
                title: event.data.title,
            });
        },

        _renderEvents: function () {
//            this.$calendar.fullCalendar('removeResource');
            this.$calendar.fullCalendar('removeEvents');
//            //console.log("DDDD::::::::::", this.state.resources)
//            this.$calendar.fullCalendar('addResource',  this.state.resources);
//            this.$calendar.fullCalendar('refetchResources')
            this.$calendar.fullCalendar('addEventSource', _.extend(this.state.events, this.state.data));
            this.$calendar.fullCalendar('refetchEvents')
            this.$calendar.fullCalendar('refetchResources');
            this.$calendar.fullCalendar("reinitView");
                var doctor_header = document.getElementsByClassName("fc-resource-cell")
                for (var i=0; i<doctor_header.length;i++)
                    for (var j=0; j<this.state.resources.length;j++)
                        if (doctor_header[i].dataset.resourceId == this.state.resources[j].id.toString())
                            doctor_header[i].style.backgroundColor = this.state.resources[j].eventColor;
//            if (parseInt(this.duration.split(':')[1]) == 30){
//                var all = document.getElementsByClassName('fc-widget-content');
//                    for (var i = 0; i < all.length; i++) {
//                        all[i].classList.add("abc");
//                }
//            }
        },
        on_attach_callback: function () {
            if (config.device.isMobile) {
                this.$el.height($(window).height() - this.$el.offset().top);
            }
            var scrollTop = false;
            if (scrollTop) {
                this.$calendar.fullCalendar('reinitView');
            } else {
                this.$calendar.fullCalendar('render');
            }
            this._renderEvents();
        },
        _formatDate : function(eventData){
            var start = moment(eventData.r_start || eventData.start);
            var end = moment(eventData.r_end || eventData.end);
            var isSameDayEvent = start.clone().add(1, 'minute').isSame(end.clone().subtract(1, 'minute'), 'day');

            var dbTimeFormat = _t.database.parameters.time_format.search('%H') != -1 ? 'HH:mm': 'hh:mm a';

            eventData['time_duration'] = start.clone().format(dbTimeFormat) + ' - ' + end.clone().format(dbTimeFormat);
            return eventData;
        },
        destroy: function () {
            if (this.$calendar) {
                this.$calendar.fullCalendar('destroy');
            }
            this._super.apply(this, arguments);
        },
        _getFullCalendarOptions : function(){
            var resources = this.state.resources;
            var self = this;
                return {
                    hiddenDays: this.hiddenDays,
                    defaultView: this.default_view,
                    groupByResource: true,
                    slotDuration: this.duration,
                    minTime: this.start_date,
                    maxTime: this.end_date,
                    slotLabelInterval: this.duration,
                    allDaySlot: false,
                    views: {
                        week: {
                            columnHeaderFormat: 'ddd M/D',
                        }
                    },
                    eventBackgroundColor: 'red',

                    defaultDate: moment().format('YYYY-MM-DD'),
                    aspectRatio: 0,
                    height: 'auto',
                    editable: true,
//                    allDaySlot: true,
                    eventOverlap: true,
                    slotEventOverlap: false,
//                    slotLabelFormat: _t.database.parameters.time_format.search("%H") != -1 ? 'HH:mm a': 'h(:mm)a',
                    selectable: true,
                    handleWindowResize: true,
                    eventLimit: true,
                    headerToolbar: false,
                    header: false,
                    resources: function(callback){
                        var filteredResources = [];
                        filteredResources = resources.filter(function(x) {
                            return self.state.resourcesIds.indexOf(x.id) !== -1;
                        });
                        callback(filteredResources || self.state.resources);
                    },
                    events: _.extend(self.state.events, self.state.data),
                }
         },
        _eventRender: function (event) {
//            this._formatDate(event)
            var qweb_context = {
                event: this._formatDate(event),
                record: event.record,
            };
            this.qweb_context = qweb_context;
            if (_.isEmpty(qweb_context.record)) {
                return qweb.render("BackgroundResourceEventBox", qweb_context);
//                return '';
            } else {
                return qweb.render("ResourceEventBox", qweb_context);
            }
        },
        _unselectEvent: function () {
            this.$('.fc-event').removeClass('o_cw_custom_highlight');
            this.$('.o_cw_popover').popover('dispose');
        },
        _renderEventPopover: function (eventData, $eventElement) {
            var self = this;

            // Initialize popover widget
            var calendarPopover = new self.config.CalendarPopover(self, self._getPopoverContext(eventData));
            calendarPopover.eventStart = calendarPopover.eventTime.time.slice(0,9);
            calendarPopover.eventEnd = calendarPopover.eventTime.time.slice(11);
            calendarPopover.appendTo($('<div>')).then(() => {
                $eventElement.popover(
                    self._getPopoverParams(eventData)
                ).on('shown.bs.popover', function () {
                    self._onPopoverShown($(this), calendarPopover);
                }).popover('show');
            });
        },
        _getPopoverParams: function (eventData) {
            return {
                animation: false,
                delay: {
                    show: 50,
                    hide: 100
                },
                trigger: 'manual',
                html: true,
                title: eventData.record.display_name,
                template: qweb.render('ResourceView.event.popover.placeholder', {color: 'red'}),
                container: eventData.allDay ? '.fc-view' : '.fc-scroller',
            }
        },
        _initCalendarMini: function () {
            var self = this;
            this.$small_calendar = this.$(".datepicker");
            this.$small_calendar.datepicker();
        },
        _onPopoverShown: function ($popoverElement, calendarPopover) {
            var $popover = $($popoverElement.data('bs.popover').tip);
            $popover.find('.o_cw_popover_close').on('click', this._unselectEvent.bind(this));
            $popover.find('.o_cw_body').replaceWith(calendarPopover.$el);
        },

        async _renderView() {
            this.$('.o_resource_calendar_widget')[0].prepend(this.$calendar);
            if (this._isInDOM) {
                this._renderCalendar();
            }
            await this._renderFilters();
        },
        _initResourceCalendar : function(){
            var self = this;
            this.$calendar = this.$('.o_resource_calendar_widget');
            var locale = moment.locale();

            var fc_options = $.extend(this._getFullCalendarOptions(), {
                eventDrop: function (event) {
                    self.trigger_up('dropRecord', event);
                },
                eventResize: function (event) {
                    self.trigger_up('updateRecord', event);
                },
                eventMouseover : function( evt, jsEvent, view){
                    if (evt.record.rendering != 'background'){
                        jsEvent.preventDefault();
                        jsEvent.stopPropagation();
                        self._unselectEvent();
                        //console.log("EVENTS::::::::::", evt)
                        $(self.$calendar).find(_.str.sprintf('[data-event-id=%s]', evt.id)).addClass('o_cw_custom_highlight');
                        self._renderEventPopover(evt, $(jsEvent.currentTarget));
//                    fc-time-grid-event
                    }
                },
                eventMouseout : function( evt, jsEvent, view){
                    if (evt.record.rendering != 'background'){
                        self._unselectEvent();
                        //console.log("EVENTS::::::::::", evt)
                        $(self.$calendar).find(_.str.sprintf('[data-event-id=%s]', evt.id)).removeClass('o_cw_custom_highlight');
                    }
//                    fc-time-grid-event
                },
                eventClick: function (evt, jsEvent) {
                    if (evt.record.rendering != 'background'){
                        jsEvent.preventDefault();
                        jsEvent.stopPropagation();
                        self._unselectEvent();
                        //console.log("EVENTS::::::::::", evt)
                        $(self.$calendar).find(_.str.sprintf('[data-event-id=%s]', evt.id)).addClass('o_cw_custom_highlight');
                        self._renderEventPopover(evt, $(jsEvent.currentTarget));
                    }
                },

                select: function (startDate, endDate, jsEvent, view, resource) {
                    var end = 0;
                    var abc;
                    abc = startDate.clone();
                    abc._d.setDate(startDate._d.getDate());
                    if (abc._d.toString().substr(28,1) == "+")
                        abc._d.setHours(abc._d.getHours() - parseInt(abc._d.toString().substr(29,2)),
                                        abc._d.getMinutes() - parseInt(abc._d.toString().substr(31,2)));
                    else
                        abc._d.setHours(abc._d.getHours() + parseInt(abc._d.toString().substr(29,2)),
                                        abc._d.getMinutes() + parseInt(abc._d.toString().substr(31,2)));
                    if (self.state.off_events){
                        for (var i=0; i<self.state.off_events.length; i++){
                            if (abc._d.toString().substr(0,3) == self.state.off_events[i].day){
                                var startDateCheck = startDate.clone();
                                startDateCheck._d.setDate(abc._d.getDate());
                                var endDateCheck = startDate.clone();
                                endDateCheck._d.setDate(abc._d.getDate());
                                startDateCheck._d.setHours(parseInt(self.state.off_events[i].start.substr(0,2)),parseInt(self.state.off_events[i].start.substr(3,2)))
                                endDateCheck._d.setHours(parseInt(self.state.off_events[i].end.substr(0,2)),parseInt(self.state.off_events[i].end.substr(3,2)))
                                startDateCheck = startDateCheck._d
                                endDateCheck = endDateCheck._d
                                if ( abc._d >= startDateCheck && abc._d < endDateCheck && self.state.off_events[i].resourceIds.includes(parseInt(resource.id))){
                                    end = 0;
                                    if (self.state.on_events){
                                        for (var j=0; j<self.state.on_events.length; j++){
                                            if (abc._d.toString().substr(0,3) == self.state.on_events[j].day){
                                                var startDateCheck = startDate.clone();
                                                startDateCheck._d.setDate(abc._d.getDate());
                                                var endDateCheck = startDate.clone();
                                                endDateCheck._d.setDate(abc._d.getDate());
                                                startDateCheck._d.setHours(parseInt(self.state.on_events[j].start.substr(0,2)),parseInt(self.state.on_events[j].start.substr(3,2)))
                                                endDateCheck._d.setHours(parseInt(self.state.on_events[j].end.substr(0,2)),parseInt(self.state.on_events[j].end.substr(3,2)))
                                                startDateCheck = startDateCheck._d
                                                endDateCheck = endDateCheck._d
                                                if ( abc._d >= startDateCheck && abc._d < endDateCheck && self.state.on_events[j].resourceIds.includes(parseInt(resource.id))){
                                                    end = 1;
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    break;
                                }
                                else
                                    end = 1;
                            }
                        }
                    }
                    if(end){
                        var events = self._getEvents(resource.id);
                        if(events){
                            for(const evt of events){
                                if(evt && evt.start >= startDate && evt.end <= startDate){
                                    //console.log("DATA::::::::::", evt);
                                }
                            }
                        }
                        if (self.$('.o_cw_popover').length) {
                            self._unselectEvent();
                        } else {
                            var data = {start: startDate, end: endDate, resource_id: Number(resource.id)};
                            if (self.state.context.default_name) {
                                data.title = self.state.context.default_name;
                            }
                            self.trigger_up('openCreate', data);
                        }
                        self.$calendar.fullCalendar('unselect');
                    }
                },
                eventRender: function (event, element, view) {
                    self.isSwipeEnabled = false;
                    var $render = $(self._eventRender(event));
                    if (_.isEmpty(event.record)){
                        element.find('.fc-content').html($render.html());
                        element.html($render.html());
                        if ($render.children()[0].innerText == "allow"){
                            element.html('');
                            element[0].style.border = '1px solid #ddd';
                        }
                        else if ($render.children()[0].innerText != "")
                            element[0].style.zIndex = 1;
                        else
                            element[0].style.zIndex = 0;
                    }
                    else{
                        element.find('.fc-content').html($render.html());
                        element.addClass($render.attr('class'));
                        element.attr('data-event-id', event.id);
                        // Add background if doesn't exist
                        if (!element.find('.fc-bg').length) {
                            element.find('.fc-content').after($('<div/>', {class: 'fc-bg'}));
                        }
                        // On double click, edit the event
                        element.on('dblclick', function () {
                            self.trigger_up('edit_event', {id: event.id});
                        });
                    }
                },
                viewRender: function (view) {
                    // compute mode from view.name which is either 'month', 'agendaWeek' or 'agendaDay'
                    var mode = view.name === 'month' ? 'month' : (view.name === 'agendaWeek' ? 'week' : 'day');
                    self.trigger_up('viewUpdated', {
                        mode: mode,
                        title: view.title,
                    });
                },
//               views: {
//                    day: {
//                        columnFormat: 'LL'
//                    },
//                    week: {
//                        columnFormat: 'ddd D'
//                    },
//                    month: {
//                        columnFormat: config.device.isMobile ? 'ddd' : 'dddd'
//                    }
//            },
            height: 'parent',
            unselectAuto: false,
            isRTL: _t.database.parameters.direction === "rtl",
//            locale: locale,
            });
             $('.fc-bgevent').on('click', function(){
                alert()
            })
//            $.fullCalendar.locale(locale);
            this.$calendar.fullCalendar(fc_options);

        },
        _getEvents : function(id){
            return _.map(this.$calendar.fullCalendar( 'getResourceEvents', id), function(event){
                if(event.rendering == "background"){
                    return event;
                }
            });
        },
        _render: function () {
            var $calendar = this.$calendar;
            if ($calendar){
                var $fc_view = $calendar.find('.fc-view');
                var scrollPosition = $fc_view.scrollLeft();
                $fc_view.scrollLeft(0);
                $calendar.fullCalendar('unselect');//
                if (scales[this.state.scale] !== $calendar.data('fullCalendar').getView().type) {
                    $calendar.fullCalendar('changeView', scales[this.state.scale]);
                }

                if (this.target_date !== this.state.target_date.toString()) {
                    $calendar.fullCalendar('gotoDate', moment(this.state.target_date));
                    this.target_date = this.state.target_date.toString();
                }

                $fc_view.scrollLeft(scrollPosition);

                this._unselectEvent();
//                var filterProm = this._renderFilters();
                this._renderEvents();
                this.$calendar.prependTo(this.$('.o_resource_calendar'));
            }
            this._set_dynamic_width();
            return Promise.all([[], this._super.apply(this, arguments)]);
        },
        _set_dynamic_width: function () {
            for (var i of $('.fc table')){
                i.style.width = 'max-content';
            }
            for (var i of $('.fc table')){
                i.style.width = 'max-content';
                if ($('.o_control_panel')[0].clientWidth <  $('.fc table')[0].clientWidth)
                    i.style.width = $('.fc table')[0].clientWidth + "px";
                else
                    i.style.width = '';
            }
        },
    });

    return DashboardRenderer;

});
