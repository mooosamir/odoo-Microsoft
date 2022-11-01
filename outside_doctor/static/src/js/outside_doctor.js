odoo.define('outside_doctor.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var OutsideDoctorDashboard = AbstractAction.extend({
    template: 'OutsideMain',
    cssLibs: [
        '/hrms_dashboard/static/src/css/lib/nv.d3.css'
    ],
    jsLibs: [
        '/hrms_dashboard/static/src/js/lib/d3.min.js'
    ],
    events: {
        'click .fetch_data_class': 'fetch_data_api_data',
        'click .select_all': 'select_all_data',
        'click .import_data': 'import_datas',
    },

    init: function(parent, context) {
        this._super(parent, context);
        console.log('##################3',context)
        this.address_data = [];
        this.current_filter = {};
        this.date_range = 'week';  // possible values : 'week', 'month', year'
        this.date_from = moment().subtract(1, 'week');
        this.date_to = moment();
        this.dashboards_templates = ['OutSideDoctor'];
        this.employee_birthday = [];
        this.upcoming_events = [];
        this.announcements = [];
        this.current_context = context;
    },

    willStart: function() {
        var self = this;
            return self.fetch_data();
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            //self.update_cp();
            self.render_dashboards();
            //self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    select_all_data: function(e){
        this.selection = [];
        var self = this;
        var $inputs = $('#emp_data_details').find('.checkbox_box input');
        $inputs.each(function (index, input) {
            if (input.checked) {

                self.selection.push($(input))
                $(input).prop('checked', false);
            }
            else{
                $(input).prop('checked', true);
            }
        });

        if (self.selection.length == $($inputs).length){
            $('#emp_data_details').find('.checkbox_box input').prop('checked', false)
        }
        else{
            $('#emp_data_details').find('.checkbox_box input').prop('checked', true)
        }
    },

    import_datas: function(){
        var self = this;
        var lst = []
        var $inputs = $('#emp_data_details').find('.checkbox_box input');
        if ($inputs.length){
            console.log('$($inputs).length++++++++++++++', $($inputs).prop('checked').length)
            // if ($($inputs).length > 1){
            //     self.do_warn(_t("Warning"), _t("Please Select One Record!"));
            // }
            var len = $("#emp_data_details input[name='checked_boxs']:checked");
            console.log("======#####", len)
            // if ((len).length > 1){
            //     alert("Select one Record at a time")
            // }
            _.each($('#emp_data_details').find('.api_tr'), function(item){
                var checkbox_item = $(item).find('input');
                if(checkbox_item.prop('checked')){
                    $.each($(checkbox_item), function(i, datas) {
                        // console.log("============",$(datas).attr('last'), $(datas).attr('taxonomies'));
                        var vals = {
                            'last_name': $(datas).attr('last'),
                            'city': $(datas).attr('city'),
                            'taxonomies': $(datas).attr('taxonomies'),
                            'credential': $(datas).attr('credential'),
                            'npi_type': $(datas).attr('npi_type'),
                            'npi': $(datas).attr('npi'),
                            'first_name': $(datas).attr('first_name'),
                            'middle_name': $(datas).attr('middle_name'),
                            'street': $(datas).attr('street'),
                            'street2': $(datas).attr('street2'),
                            'license_doctor': $(datas).attr('license_doctor'),
                            'medicaid': $(datas).attr('medicaid'),
                            'phone': $(datas).attr('phone'),
                            'country': $(datas).attr('country'),
                            'prefix': $(datas).attr('prefix'),
                            'zip': $(datas).attr('zip'),
                        }
                        lst.push(vals)
                    });
                }
            });
            console.log('lenght+++++++++++++++++',lst.length)
            if ((lst).length > 1){
                alert("Please Select one record at a time.")
            }
            else{
                rpc.query({
                    model: 'hr.employee',
                    method: 'create_data',
                    args: [{'data': lst, 'context_data': self.current_context.context}]
                }, []).then(function(result){
                    if ('data' in result && !('is_employee' in self.current_context.context)){
                        self.do_action(result['action']);
                    }
                    else if ('data' in result && 'is_employee' in self.current_context.context){
                        self.do_action(result['action']);
                    }
                    else{
                        self.do_warn(_t("Warning"), _t(result['message']));
                    }
                });
            }
        }
        else{
            alert('no record selected.')
        }
    },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'hr.employee',
                method: 'get_user_employee_details'
        }).then(function(result) {
            self.login_employee =  result[0];
            console.log("@@@@@@@@@@",result[0])
            //self.address_data = result[0]
        });
        return $.when(def1);
    },

    render_dashboards: function() {
        var self = this;
        var self = this;
        if (this.login_employee){
            var templates = []
            templates = ['OutSideDoctor'];
            console.log("templates",self.current_context.context.is_employee)
            self.outside_dashboard = $(QWeb.render(templates[0], {widget: self}));
            //$( ".o_control_panel" ).addClass( "o_hidden" );
            $(".main-section").addClass("o_hidden");
            $(self.outside_dashboard).prependTo(self.$el);
        }
        return self.outside_dashboard
    },

    fetch_data_api_data: function(event) {
        var self = this;
        var last_name = document.querySelector('#last_name_api').value;
        var city = document.querySelector('#city_api').value;
        var state = document.querySelector('#state_api').value;
        console.log("###############",state, city);
        rpc.query({
            model: 'hr.employee',
            method: 'get_api_data',
            args: [{"last_name":last_name, "city": city, "state": state}]
            //context:{"last_name":last_name,"first_name": first_name , "city": city, "state": state}
        }, []).then(function(result){
            if (result){
                console.log("++++++++++++++++++++",result);
                self.address_data = result
                self.current_filter = {"last_name":last_name, "city": city, "state": state}
                self.render_dashboards();   
            }
            else{
                //$("#emp_data_details").empty();
                $("#emp_data_details tbody tr").remove();
                self.do_warn(_t("Warning"), _t("Record Not Found!"));
            }
        });

    },
});


core.action_registry.add('outside_doctor', OutsideDoctorDashboard);
return OutsideDoctorDashboard;

});
