odoo.define('opt_appointment.DashboardController', function (require) {
    "use strict";

    var AbstractController = require('web.AbstractController');
    var config = require('web.config');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    var Dialog = require('web.Dialog');
    var dialogs = require('web.view_dialogs');
    var qweb = core.qweb;

    function dateToServer (date,self) {
        return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
//        return date.clone().hour(date._i[3]).minute(date._i[4]).utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
//        return date.clone().hour(date._i[3]).minute(date._i[4]).add(-self.getSession().getTZOffset(date), 'minutes').utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
//        return date.clone().utc().utcOffset(self.model.data.timezone).locale('en').format('YYYY-MM-DD HH:mm:ss')
//        return date.clone().utc().add(+self.getSession().getTZOffset(date), 'minutes').locale('en').format('YYYY-MM-DD HH:mm:ss')

//		     var abc;
//		     var xyz;
//		     var diff;
//                    abc = date.clone();
//                    abc._d.setDate(date._d.getDate());
//                    if (abc._d.toString().substr(28,1) == "+")
//                        abc._d.setHours(abc._d.getHours() - parseInt(abc._d.toString().substr(29,2)),
//                                        abc._d.getMinutes() - parseInt(abc._d.toString().substr(31,2)));
//                    else
//                        abc._d.setHours(abc._d.getHours() + parseInt(abc._d.toString().substr(29,2)),
//                                        abc._d.getMinutes() + parseInt(abc._d.toString().substr(31,2)));
//
//                   xyz = date.clone();
//                   xyz.utcOffset(self.model.data.timezone)
//
////                   if (abc._d.toString().substr(16,2) != xyz._d.toString().substr(16,2) && abc._d.toString().substr(19,2) != xyz._d.toString().substr(19,2))
//
//                   abc.utcOffset(self.model.data.timezone)
//                   if (parseInt(date._d.toString().substr(16,2)) < parseInt(abc._d.toString().substr(16,2)))
//                   	diff = parseInt(abc._d.toString().substr(16,2)) - parseInt(date._d.toString().substr(16,2))
//                   else
//                   	diff = parseInt(date._d.toString().substr(16,2)) - parseInt(abc._d.toString().substr(16,2))
//                   return date.clone().utc().add(-diff, 'hours').locale('en').format('YYYY-MM-DD HH:mm:ss')

    }

    var DashboardController = AbstractController.extend({
        custom_events: _.extend({}, AbstractController.prototype.custom_events, {
            changeDate: '_onChangeDate',
            changeFilter: '_onChangeFilter',
            deleteRecord: '_onDeleteRecord',
            dropRecord: '_onDropRecord',
            next: '_onNext',
            openCreate: '_onOpenCreate',
            openEvent: '_onOpenEvent',
            prev: '_onPrev',
            quickCreate: '_onQuickCreate',
            updateRecord: '_onUpdateRecord',
            viewUpdated: '_onViewUpdated',
        }),
        events: {
            'click .resource.o_menu_item': '_onItemClick',
        },
        _onChangeFilter: function (event) {
            if (this.model.changeFilter(event.data) && !event.data.no_reload) {
                this.reload();
            }
        },
        _onItemClick: function (event) {
            event.preventDefault();
            event.stopPropagation();
            $(event.currentTarget).find('.dropdown-item').toggleClass('selected');
            var physician = [], state = [], company = [];
            this.$('.resource.o_menu_item').each(function(idx, value){
                if($(value).find('a').hasClass('selected')){
                    var data = $(value).data('id');
                    if ($(value).data('name') == 1){
                        company.push(data);
                    }else if(_.contains(['confirmed', 'none', 'not_available', 'left_message'], data)){
                        state.push(data);
                    }else{
                        physician.push(data);
                    }
                }
            })
            var filter = {employee : physician , state : state, company : company};
            this.model.setFilter(filter);
            this.reload();
        },
        _onViewUpdated: function (event) {
            this.mode = event.data.mode;
            if (this.$buttons) {
                this.$buttons.find('.active').removeClass('active');
                this.$buttons.find('.o_calendar_button_' + this.mode).addClass('active');
            }
            this._setTitle(this.displayName + ' (' + event.data.title + ')');
        },
        _updateRecord: function (record) {
            var reload = this.reload.bind(this, {});
            return this.model.updateRecord(record).then(reload, reload);
        },
         _onUpdateRecord: function (event) {
            this._updateRecord(event.data);
        },
        _onDropRecord: function (event) {
            this._updateRecord(_.extend({}, event.data, {
                'drop': true,
            }));
        },
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.current_start = null;
            this.displayName = params.displayName;
            this.quickAddPop = params.quickAddPop;
            this.disableQuickCreate = params.disableQuickCreate;
            this.eventOpenPopup = params.eventOpenPopup;
            this.formViewId = params.formViewId;
            this.readonlyFormViewId = params.readonlyFormViewId;
            this.mapping = params.mapping;
            this.context = params.context;
            this.previousOpen = null;
            // The quickCreating attribute ensures that we don't do several create
            this.quickCreating = false;
            this.employee = params.initialState.resources;
            //console.log("this.employee::::::::::", this.employee)

            this.company = params.initialState.more_resources;
            //console.log("this.company::::::::::", this.company)

            this.selected_company = params.initialState.selected_company;
            //console.log("this.selected_company::::::::::", this.selected_company)
        },
        _onOpenCreate: function (event) {
            var self = this;
            if (this.model.get().scale === "month") {
                event.data.allDay = true;
            }
            var data = this.model.calendarEventToRecord(event.data);

            var context = _.extend({}, this.context, event.options && event.options.context);
            context.default_name = data.name || null;
            context['default_' + this.mapping.date_start] = data[this.mapping.date_start] || null;
            if (this.mapping.date_stop) {
                context['default_' + this.mapping.date_stop] = data[this.mapping.date_stop] || null;
            }
            if (this.mapping.date_delay) {
                context['default_' + this.mapping.date_delay] = data[this.mapping.date_delay] || null;
            }
            if (this.mapping.all_day) {
                context['default_' + this.mapping.all_day] = data[this.mapping.all_day] || null;
            }
            if(event.data.resource_id){
                context['default_employee_id'] = event.data.resource_id || null;
            }

            for (var k in context) {
                if (context[k] && context[k]._isAMomentObject) {
                    context[k] = dateToServer(context[k],this);
                }
            }
//
            var options = _.extend({}, this.options, event.options, {
                context: context,
                title: _.str.sprintf(_t('Create: %s'), (this.displayName || this.renderer.arch.attrs.string))
            });
//
            if (this.quick != null) {
                this.quick.destroy();
                this.quick = null;
            }

            var title = _t("Create");
            if (this.renderer.arch.attrs.string) {
                title += ': ' + this.renderer.arch.attrs.string;
            }

            if (this.eventOpenPopup) {
                if (this.previousOpen) { this.previousOpen.close(); }
                this.previousOpen = new dialogs.FormViewDialog(self, {
                    res_model: this.modelName,
                    context: context,
                    title: title,
                    view_id: this.formViewId || false,
                    disable_multiple_selection: true,
                    on_saved: function () {
                        if (event.data.on_save) {
                            event.data.on_save();
                        }
                        self.reload();
                    },
                });
                this.previousOpen.open();
            } else {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: this.modelName,
                    views: [[this.formViewId || false, 'form']],
                    target: 'current',
                    context: context,
                });
            }
        },
        _onChangeDate: function (event) {
            var modelData = this.model.get();
//            if (modelData.target_date.format('YYYY-MM-DD') === event.data.date.format('YYYY-MM-DD')) {
//                // When clicking on same date, toggle between the two views
//                switch (modelData.scale) {
//                    case 'month': this.model.setScale('week'); break;
//                    case 'week': this.model.setScale('day'); break;
//                    case 'day': this.model.setScale('month'); break;
//                }
//            } else if (modelData.target_date.week() === event.data.date.week()) {
//                // When clicking on a date in the same week, switch to day view
//                this.model.setScale('day');
//            } else {
//                // When clicking on a random day of a random other week, switch to week view
//                this.model.setScale('week');
//            }
            this.model.setDate(event.data.date);
            this.reload();
        },
        _onOpenEvent: function (event) {
            var self = this;
            var id = event.data._id;
            id = id && parseInt(id).toString() === id ? parseInt(id) : id;

            if (!this.eventOpenPopup) {
                this._rpc({
                    model: self.modelName,
                    method: 'get_formview_id',
                    //The event can be called by a view that can have another context than the default one.
                    args: [[id]],
                    context: event.context || self.context,
                }).then(function (viewId) {
                    self.do_action({
                        type:'ir.actions.act_window',
                        res_id: id,
                        res_model: self.modelName,
                        views: [[viewId || false, 'form']],
                        target: 'current',
                        context: event.context || self.context,
                    });
                });
                return;
            }

            var options = {
                res_model: self.modelName,
                res_id: id || null,
                context: event.context || self.context,
                title: _t("Open: ") + _.escape(event.data.title),
                on_saved: function () {
                    if (event.data.on_save) {
                        event.data.on_save();
                    }
                    self.reload();
                },
            };
            if (this.formViewId) {
                options.view_id = parseInt(this.formViewId);
            }
            new dialogs.FormViewDialog(this, options).open();
        },
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
            self.$buttons.on('click', '.o_calendar_button_month_change', function (ev) {
                self.redirect_month(ev);
            });
            _.each(['day', 'week', 'month'], function (scale) {
                self.$buttons.on('click', '.o_calendar_button_' + scale, function () {
                    self.model.setScale(scale);
                    self.reload();
                });
            });
            this.$buttons.find('.o_calendar_button_' + this.mode).addClass('active');
            this.$buttons.find("#select_date").datepicker({
                showOn: "button",
                buttonText: "<i class='fa fa-calendar'></i>",
                'onSelect': function (datum, obj) {
                    self.trigger_up('changeDate', {
                        date: moment(new Date(+obj.currentYear , +obj.currentMonth, +obj.currentDay))
                    });
                },
                'showOtherMonths': true,
            });
//            this.$small_calendar.datepicker();

            if ($node) {
                this.$buttons.appendTo($node);
            } else {
                this.$('.o_calendar_buttons').replaceWith(this.$buttons);
            }
            self.$buttons.on('click', '.print_appointment_report', function () {
                self._onPrintClick(this);
            });
            var state = [{'none': 'None',
                        'left_message' : 'Left Message',
                        'not_available' : 'Not Available',
                        }]
            this.$buttons.find('.custom.dropdown-menu').html(qweb.render("CustomFilter", {employee : this.employee, select_company : this.selected_company , company : this.company}));
       },
        _move: function (to) {
            this.model[to]();
            return this.reload();
        },
        redirect_month : function(month){
            this.model.redirect_month(Number($(month.currentTarget).data('month')));
            return this.reload();
        },
        _onPrintClick: function (event) {
            var self = this
            self.do_action({
                name: 'Appointments',
                res_model: 'appointment.report',
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                target: 'new',
            })
        },
    });

    return DashboardController;

});
