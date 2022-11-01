odoo.define('opt_appointment.appointment', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var view_dialogs = require('web.view_dialogs');
    var core = require('web.core');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var dialogs = require('web.view_dialogs');
    var CalendarPopover = require('web.CalendarPopover');
   var config = require('web.config');
   var QWeb = core.qweb;
    var _t = core._t;

    var BookAppointment = AbstractAction.extend({
        hasControlPanel: true,
        contentTemplate: 'BookAppointment',
        cssLibs: ['/opt_appointment/static/src/css/main.min.css'],
        jsLibs: ['/opt_appointment/static/src/lib/main.min.js'],
        init: function (parent, params) {
            this._super.apply(this, arguments);
            var self = this;
            this.action_manager = parent;
            this.params = params;
            this.calendar = false;
        },
        events: {
            'click .o_calendar_button_day'   : '_calendar_button_day',
            'click .o_calendar_button_week'  : '_calendar_button_week',
            'click .o_calendar_button_month' : '_calendar_button_month',
            'click .o_calendar_button_months_add' : '_calendar_button_months_add',
            'click .o_calendar_button_nav_day' : '_calendar_button_nav_day',
        },
        willStart: function () {
            var self = this;
            var def = this._rpc({
                model: 'calendar.event',
                method: 'get_form_id',
            }).then(function (result) {
                self.form_id = result;
            });
            self.date_domain = []
            this._rpc({
                model: 'calendar.event',
                method: 'get_appointment_booking_datas',
                args : [[], self.date_domain]
            }).then(function (result) {
                //console.log(result[1], 'result')
                self.resource = result[0]
                self.eventData = result[1]
//                self.form_id = result;
            });
            return Promise.all([this._super.apply(this, arguments), def]);
        },
        start: async function () {
            this._super.apply(this, arguments);
            this.set("title", this.title);
        },
        _calendar_button_nav_day : function(ev){
            let dataKey = $(ev.currentTarget).data('key');
            if(dataKey === 'next'){
                this.calendar.next()
            }else if(dataKey === 'prev'){
                this.calendar.prev()
            }else{
                this.calendar.today()
            }
        },
        _calendar_button_months_add : function(ev){
            this._render_by_month(Number($(ev.currentTarget).data('month') || 1));
        },
        _calendar_button_day : function(ev){
            $(ev.currentTarget).addClass('active').siblings().removeClass('active');
            this._render_calendar("resourceTimeGridDay");
        },
        _calendar_button_week : function(ev){
            $(ev.currentTarget).addClass('active').siblings().removeClass('active');
            this._render_calendar("resourceTimeGridWeek");
        },
        _calendar_button_month : function(ev){
            $(ev.currentTarget).addClass('active').siblings().removeClass('active');
            this._render_calendar("resourceDayGridMonth")
        },
        _render_calendar : function(view){
            this.calendar.changeView(view);
            this.calendar.render();
        },
        _render_by_month : function(month){
            var date = new Date;
            date.setMonth(date.getMonth() + month);
            this.calendar.gotoDate(date);
        },
        renderElement: function () {
            var self = this;
            this._super.apply(this, arguments);
            var resource = self.eventData;
            setTimeout(function(){
                $( "#select_date" ).datepicker({
                    showOn: "button",
                    buttonText: "<i class='fa fa-calendar'></i>",
                    onSelect: function(dateText, inst) {
                        var date = new Date(dateText);
                        self.calendar.destroy();
                        self.calendar.gotoDate(date);
                        self.calendar.render();
                    }
                })
                var calendarEl = document.getElementById('calendar');
                self.calendar = new FullCalendar.Calendar(calendarEl, {
                    schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
                    initialView: 'resourceTimeGridTwoDay',
                    initialDate: new Date(),
                    editable: true,
                    selectable: true,
                    headerToolbar: {
                        left: '',
                        center: 'title',
                        right: ''
                    },
                    views: {
                        resourceTimeGridTwoDay: {
                        type: 'resourceTimeGrid',
                        duration: { days: 1 },
                        buttonText: '2 days',
                        }
                    },
                    resources: self.resource,
                    events: self.eventData,
                    // ON CLICK BLANK SPACE
                    select: function(arg) {
                         let previousOpen = new dialogs.FormViewDialog(self, {
                            res_model: 'calendar.event',
                            title: 'ADD Event',
                            view_id: self.form_id || false,
                            disable_multiple_selection: true,
                            on_saved: function (record) {
                                //console.log("record.data>>>>>", record.data)
                                const {id, patient_id, service_type, start, stop} = record.data;
                                let event = {start: moment(start).format('YYYY-MM-DDTHH:mm:ssZ'),
                                             end : moment(stop).format('YYYY-MM-DDTHH:mm:ssZ'),
                                             title : patient_id.data.display_name + ' ' + service_type.data.display_name,
                                             resourceId: arg.resource.id,
                                             id : id,
                                             service: [service_type.data.id, service_type.data.display_name],
                                             partner: [patient_id.data.id, patient_id.data.display_name]
                                             }
                                self.calendar.addEvent(event);
                                self.calendar.render();
                            },
                        });
                        previousOpen.open();
                    },
                    eventClick: function(info) {
                        //console.log(info.event.extendedProps.partner);
                        let event_obj = {partner : info.event.extendedProps.partner,
                                         service : info.event.extendedProps.service,
                                         start   : moment(info.event.start).format('HH:mm A'),
                                         end     : moment(info.event.end).format('HH:mm A')};
                        $(info.el).popover({
                            html : true,
                            placement: 'right',
                            content: function(e) {
                                let html = QWeb.render('CalenderPopover', {event : event_obj})
                                return html;
                            }
                        });
//                        self._renderEventPopover(info.event, $(info.el));

//                        alert('Event: ' + info.event.title);
//                        alert('Coordinates: ' + info.jsEvent.pageX + ',' + info.jsEvent.pageY);
//                        alert('View: ' + info.view.type);
//
//                        // change the border color just for fun
//                        info.el.style.borderColor = 'red';
                    },
                    dateClick: function(arg) {
                        //console.log('dateClick',arg.date, arg.resource ? arg.resource.id : '(no resource)');
                    }
                  });
                  self.calendar.render();
                  self.calendar.setOption('contentHeight', 400);

            }, 10)
        },
    });

    core.action_registry.add('tag_appointment_book', BookAppointment);

    return {
        BookAppointment : BookAppointment,
    };
});
