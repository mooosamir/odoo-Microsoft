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

    var _t = core._t;
    var qweb = core.qweb;
var scales = {
    day: 'agendaDay',
    week: 'agendaWeek',
    month: 'month'
};
    var DashboardRenderer = AbstractRenderer.extend({
        template: "ResourceView",

//        events: _.extend({}, AbstractRenderer.prototype.events, {
//        }),

        init: function(parent, state, params) {
            this._super.apply(this, arguments);
            this.displayFields = params.displayFields;
            this.model = params.model;
            this.filters = [];
            this.color_map = {};
            this.hideDate = params.hideDate;
            this.hideTime = params.hideTime;
        },

        start: function () {
            this._initResourceCalendar();
            return this._super();
        },

        _renderEvents: function () {
            this.$calendar.fullCalendar('removeEvents');
            //console.log("this.state::::::::::::", this.state)
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
        destroy: function () {
            if (this.$calendar) {
                this.$calendar.fullCalendar('destroy');
            }
            this._super.apply(this, arguments);
        },
        getColor: function (key) {
            if (!key) {
                return;
            }
            if (this.color_map[key]) {
                return this.color_map[key];
            }
            // check if the key is a css color
            if (typeof key === 'string' && key.match(/^((#[A-F0-9]{3})|(#[A-F0-9]{6})|((hsl|rgb)a?\(\s*(?:(\s*\d{1,3}%?\s*),?){3}(\s*,[0-9.]{1,4})?\))|)$/i)) {
                return this.color_map[key] = key;
            }
            var index = (((_.keys(this.color_map).length + 1) * 5) % 24) + 1;
            this.color_map[key] = index;
            return index;
        },
        getLocalState: function () {
            var $fcScroller = this.$calendar.find('.fc-scroller');
            return {
                scrollPosition: $fcScroller.scrollTop(),
            };
        },
        /**
         * @override
         */
        setLocalState: function (localState) {
            if (localState.scrollPosition) {
                var $fcScroller = this.$calendar.find('.fc-scroller');
                $fcScroller.scrollTop(localState.scrollPosition);
            }
        },
        _eventRender: function (event) {
            var qweb_context = {
                event: event,
                record: event.record,
                color: this.getColor(event.color_index),
            };
            this.qweb_context = qweb_context;
            if (_.isEmpty(qweb_context.record)) {
                return '';
            } else {
                return qweb.render("calendar-box", qweb_context);
            }
        },
        _format: function (record, fieldName) {
            var field = this.state.fields[fieldName];
            if (field.type === "one2many" || field.type === "many2many") {
                return field_utils.format[field.type]({data: record[fieldName]}, field);
            } else {
                return field_utils.format[field.type](record[fieldName], field, {forceString: true});
            }
        },

        _getFullCalendarOptions : function(){
             var events = [
                { id: '2', resourceId: 'a', start: '2021-04-22T09:00:00', end: '2021-04-22T14:00:00',
                    title: 'Alexander  Hamilton', partner : 'Alexander  Hamilton (30y 2m)',
                    service: 'Lens Treatment',  appointment_status : '', confirm_status: ''},
                { id: '3', resourceId: 'b', start: '2021-04-22T12:00:00', end: '2021-04-22T16:00:00',
                    title: 'Judy Garland', partner : 'Judy Garland (70y)',
                    service: '92014 - Estb Comp Confirmed', appointment_status : '', confirm_status: ''},
                    { id: '4', resourceId: 'c', start: '2021-04-22T07:30:00', end: '2021-04-22T09:30:00',
                        title: 'Judy Garland', partner : 'Judy Garland (70y)', service: 'Frame Design',
                        appointment_status : '', confirm_status: ''},
                { id: '5', resourceId: 'd', start: '2021-09-22T10:00:00', end: '2021-09-22T15:00:00',
                    title: 'Alexander  Hamilton', partner : 'Alexander  Hamilton (30y 2m)',
                    service: 'Eye Checkup', appointment_status : '', confirm_status: ''},
            ];
            return {
                defaultView: 'agendaDay',
                groupByResource: true,
                resources: [
                    { id: 'a', title: 'Doctor A' },
                    { id: 'b', title: 'Doctor B', eventColor: 'green' },
                    { id: 'c', title: 'Doctor C', eventColor: 'orange' },
                    { id: 'd', title: 'Doctor D', eventColor: 'red' }
                ],
                events: events,
            }
        },
        _initResourceCalendar : function(){
//            var self = this;
            //console.log("EVENT::::::::::::::", this.state)
            var fc_options = $.extend({}, this._getFullCalendarOptions(), {
                eventDrop: function (event) {
                    self.trigger_up('dropRecord', event);
                },
                eventResize: function (event) {
                    self.trigger_up('updateRecord', event);
                },
                eventClick: function (eventData, ev) {
                    alert()
                },
                select: function (startDate, endDate) {
                    //console.log("START--------", startDate, endDate)
                    self.$calendar.fullCalendar('unselect');
                },
                eventRender: function (event, element, view) {
                    //console.log("event, element, view", event, element, view)
                },

            });

            this.$calendar = this.$('.o_resource_calendar_widget');
            var locale = moment.locale();
            $.fullCalendar.locale(locale);
//            this.$calendar.fullCalendar(fc_options);

            this.$calendar.fullCalendar({
                defaultView: 'agendaDay',
                defaultDate: moment().format('YYYY-MM-DD'),
                aspectRatio: 0,
                editable: true,
                timezone:'local',
                allDaySlot: false,
                eventOverlap: false,
                selectable: true,
                height:475,
                eventLimit: true,
                headerToolbar: false,
                header: false,
                resources: [
                    { id: 'a', title: 'Doctor A' },
                    { id: 'b', title: 'Doctor B', eventColor: 'green' },
                    { id: 'c', title: 'Doctor C', eventColor: 'orange' },
                    { id: 'd', title: 'Doctor D', eventColor: 'red' }
                ],
                events: [
                    { id: '2', resourceId: 'a', start: '2021-04-22T09:00:00', end: '2021-04-22T14:00:00',
                        title: 'Alexander  Hamilton', partner : 'Alexander  Hamilton (30y 2m)',
                        service: 'Lens Treatment',  appointment_status : '', confirm_status: ''},
                    { id: '3', resourceId: 'b', start: '2021-04-22T12:00:00', end: '2021-04-22T16:00:00',
                        title: 'Judy Garland', partner : 'Judy Garland (70y)',
                        service: '92014 - Estb Comp Confirmed', appointment_status : '', confirm_status: ''},
                        { id: '4', resourceId: 'c', start: '2021-04-22T07:30:00', end: '2021-04-22T09:30:00',
                            title: 'Judy Garland', partner : 'Judy Garland (70y)', service: 'Frame Design',
                            appointment_status : '', confirm_status: ''},
                    { id: '5', resourceId: 'd', start: '2021-09-22T10:00:00', end: '2021-09-22T15:00:00',
                        title: 'Alexander  Hamilton', partner : 'Alexander  Hamilton (30y 2m)',
                        service: 'Eye Checkup', appointment_status : '', confirm_status: ''},
                ],
                // ON CLICK BLANK SPACE
                select: function(arg) {
                    //console.log("Args------", arg)
                },
                eventClick: function(info) {
                    //console.log(info.event.extendedProps.partner);
                },
                dateClick: function(arg) {
                    //console.log('dateClick',arg.date, arg.resource ? arg.resource.id : '(no resource)');
                }
            });
//            ISSUE IN this.resourceCalendar.render() - IT IS FULLCALENDAR LIBRARY METHOD FOR RENDER RESOURCE VIEW
//            this.$calendar.render();
        },
         _render: function () {
            var $calendar = this.$calendar;
//            var $fc_view = $calendar.find('.fc-view');
//            var scrollPosition = $fc_view.scrollLeft();
//            $fc_view.scrollLeft(0);
//            $calendar.fullCalendar('unselect');

//            if (scales[this.state.scale] !== $calendar.data('fullCalendar').getView().type) {
//                $calendar.fullCalendar('changeView', scales[this.state.scale]);
//            }

//            if (this.target_date !== this.state.target_date.toString()) {
//                $calendar.fullCalendar('gotoDate', moment(this.state.target_date));
//                this.target_date = this.state.target_date.toString();
//            }
//
//            this.$small_calendar.datepicker("setDate", this.state.highlight_date.toDate())
//                                .find('.o_selected_range')
//                                .removeClass('o_color o_selected_range');
//            var $a;
//            switch (this.state.scale) {
//                case 'month': $a = this.$small_calendar.find('td'); break;
//                case 'week': $a = this.$small_calendar.find('tr:has(.ui-state-active)'); break;
//                case 'day': $a = this.$small_calendar.find('a.ui-state-active'); break;
//            }
//            $a.addClass('o_selected_range');
//            setTimeout(function () {
//                $a.not('.ui-state-active').addClass('o_color');
//            });
//
//            $fc_view.scrollLeft(scrollPosition);
//
//            this._unselectEvent();
//            var filterProm = this._renderFilters();
//            this._renderEvents();
//            this.$calendar.prependTo(this.$('.o_calendar_view'));

            return Promise.all([[], this._super.apply(this, arguments)]);
        },
//        _render: function() {
//            //console.log("FFFFFFFFFFF")
//            return Promise.resolve().then(() => {
                // Prevent Double Rendering on Updates
//                if (!this.timeline) {
//                    this._initResourceCalendar();
//                    $(window).trigger("resize");
//                }
//            });
//        },
    });

    return DashboardRenderer;

});
