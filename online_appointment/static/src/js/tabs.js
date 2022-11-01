odoo.define('online_appointment.tabs', function (require) {

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');

    var _t = core._t;

    publicWidget.registry.OnlineAppointmentTabs = publicWidget.Widget.extend({
        selector: '.online_appointment_tabs',
        events: {
            'click .scheduling_appointment #tab1_box .next': 'on_click_tab1',
            'click .scheduling_appointment #tab2_box .next': 'on_click_tab2',
            'click .scheduling_appointment #tab2_box .back': 'on_back_click_tab2',
            'change .scheduling_appointment #tab2_box input[name="doctor"]': 'show_calender',
            'click .scheduling_appointment #tab3_box .next': 'on_click_tab3',
            'change .scheduling_appointment #tab3_box .insurance_question': 'scheduling_appointment_insurance_question',
            'click .scheduling_appointment #tab3_box .back': 'on_back_click_tab3',
            'click .appointment_confirmed .next': 'on_click_tab4',
            'click .appointment_confirmed .back': 'on_back_click_tab4',
            'click .appointment_error .yes': 'on_click_tab4',
            'click .appointment_error .edit': 'appointment_error_edit',
            'click .appointment_error .not_sure': 'appointment_error_not_sure',
        },
        start: function () {
            var self = this;
            var phones = [{ "mask": "###-###-####"}, { "mask": "###-###-####"}];

            var res = this._super.apply(this.arguments).then(function () {
                if ($('input[name="selected_doctor"]').length == 1)
                    self.show_calender();
                $('.scheduling_appointment input[name="mobile"]').inputmask({
                    mask: phones,
                    greedy: false,
                    definitions: { '#': { validator: "[0-9]", cardinality: 1}}
                });
            });
            return res;
        },
        scheduling_appointment_insurance_question: function(ev){
            ev.preventDefault();
            ev.stopPropagation();
            if ($("input[name='insurance_q']:checked").val() == 'Y'){
                $('.insurance_q').css('display','flex');
                $('.insurance_q').css('display','flex');
            }
            else{
                $('.insurance_q').hide();
                $('.insurance_q').hide();
            }
        },
        on_click_tab1: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);

            if ( $("input[name='contacts']:checked").val()
                &&  $("input[name='online_service']:checked").val()){
                    if ($('#tab3_box').css('display') != "block"){
                        $('#tab1_box').hide();
                        $('#no_ajax_tabs_tab_1').removeClass("tab_active");
                        $('#tab2_box').show();
                        $('#no_ajax_tabs_tab_2').addClass("tab_active");
                    }
            }
            else{
                var message = "Following fields are required: \n\n\n";
                if (!$("input[name='contacts']:checked").val())
                    message += "Do you currently wear contacts?\n";
                if (!$("input[name='online_service']:checked").val())
                    message += "Exam\n";
                alert(message);
            }
            $button.attr('disabled', false);

//        $('#conference_registration_form table').siblings('.alert').remove();
//        $('#conference_registration_form select').each(function () {
//            post[$(this).attr('name')] = $(this).val();
//        });

//                return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
//                    var $modal = $(modal);
//                    $modal.modal({backdrop: 'static', keyboard: false});
//                    $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
//                    $modal.appendTo('body').modal();
//                    $modal.on('click', '.js_goto_event', function () {
//                        $modal.modal('hide');
//                        $button.prop('disabled', false);
//                    });
//                    $modal.on('click', '.close', function () {
//                        $button.prop('disabled', false);
//                    });
//                });
        },
        on_click_tab2: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);

            if ( $("input[name='doctor']:checked").val() && $("input[name='date_time']:checked").val()){
                $('#tab2_box').hide();
                $('#no_ajax_tabs_tab_2').removeClass("tab_active");
                $('#tab3_box').show();
                $('#no_ajax_tabs_tab_3').addClass("tab_active");
            }
            else{
                var message = "Following fields are required: \n\n\n";
                if (!$("input[name='doctor']:checked").val())
                    message += "Doctor\n";
                if (!$("input[name='date_time']:checked").val())
                    message += "date time of appointment\n";
                alert(message);
            }
            $button.attr('disabled', false);
        },
        on_back_click_tab2: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);

            $('#tab2_box').hide();
            $('#no_ajax_tabs_tab_2').removeClass("tab_active");
            $('#tab1_box').show();
            $('#no_ajax_tabs_tab_1').addClass("tab_active");
            $button.attr('disabled', false);
        },
        on_click_tab3: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);

            if ( ($("input[name='first_name']").val() && $("input[name='dob']").val() && $("input[name='mobile']").val()
                && $("input[name='last_name']").val() && $("input[name='email']").val() && $("input[name='insured_dob']").val()
                && $("input[name='insurance_q']:checked").val() == 'Y' && $("input[name='primary_insured']").val() && $("input[name='ssn']").val())
                ||
                ( $("input[name='first_name']").val() && $("input[name='dob']").val() && $("input[name='mobile']").val()
                && $("input[name='last_name']").val() && $("input[name='email']").val()
                && $("input[name='insurance_q']:checked").val() == 'N')
                ){
                    var data = {};
                    $("#online_scheduling_form").serializeArray().map(function(x){data[x.name] = x.value;});
                    if (document.getElementsByName('validation_check')[0].value != 1)
                        return ajax.jsonRpc('/online_appointment/patient_check', 'call', data).then(function (response) {
                            $('.scheduling_appointment').hide();
                            $('.scheduling_appointment').hide();
                            $('.scheduling_appointment').hide();
                            if (response == 'yes' || response == 'no'){
                                $('.appointment_confirmed').css('display','flex');

                                let d = $("input[name='dob']").val();

                                var datestring = d.substr(5,2) + "/" + d.substr(8,2) + "/" + d.substr(0,4);

                                function camelize(str) {
                                      return str.replace(/(?:^\w|[A-Z]|\b\w)/g, function(word, index) {
                                      return word.toUpperCase();
                                      }).replace(/\s+/g, '');
                                    }

                                $('.ra_dab')[0].innerHTML = $("input[name='date_time']:checked").attr('value') + ',' + $("input[name='date_time']:checked").attr('value2');
                                $('.ra_doc')[0].innerHTML = $("input[name='doctor']:checked")[0].attributes['value2'].nodeValue;
                                $('.ra_name')[0].innerHTML = camelize($("input[name='first_name']").val()) + ' ' + camelize($("input[name='last_name']").val());
                                $('.ra_dob')[0].innerHTML = datestring;
                                $('.ra_mob')[0].innerHTML = $("input[name='mobile']").val();
                                $('.ra_email')[0].innerHTML = $("input[name='email']").val();
                                $button.attr('disabled', false);

                            }
                            else if (response == 'maybe')
                                $('.appointment_error').css('display','flex');
                        });
                    else
                        $button.attr('disabled', false);
                        this.on_click_tab4();
            }
            else{
                var message = "Following fields are required: \n\n\n";
                if (!$("input[name='first_name']").val())
                    message += "First Name\n";
                if (!$("input[name='dob']").val())
                    message += "Date Of Birth\n";
                if (!$("input[name='mobile']").val())
                    message += "Mobile\n";
                if (!$("input[name='last_name']").val())
                    message += "Last Name\n";
                if (!$("input[name='email']").val())
                    message += "Email\n";
                if ($("input[name='insurance_q']:checked").val() == 'Y'){
                    if (!$("input[name='primary_insured']").val())
                        message += "Primary Insured\n";
                    if (!$("input[name='insured_dob']").val())
                        message += "Insured Date of Birth\n";
                    if (!$("input[name='ssn']").val())
                        message += "Last 4 SSN\n";
                }
                alert(message);
            }

            $button.attr('disabled', false);
        },
        on_back_click_tab3: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);

            $('#tab3_box').hide();
            $('#no_ajax_tabs_tab_3').removeClass("tab_active");
            $('#tab2_box').show();
            $('#no_ajax_tabs_tab_2').addClass("tab_active");
            $button.attr('disabled', false);
        },
        on_click_tab4: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $button = $(ev.currentTarget).closest('.next');
            var data = {};
            $("#online_scheduling_form").serializeArray().map(function(x){data[x.name] = x.value;});
            data.date = $("input[name='date_time']:checked").attr('value2');
            data.mobiles = $("input[name='mobile']").val().replaceAll('-','')

            return ajax.jsonRpc('/online_appointment/registration', 'call', data).then(function (modal) {
                if (modal == false)
                    alert('Appointment already booked at selected date time, kindly select another slot.');
                else
                    window.location.href = modal;
            });
        },
        on_back_click_tab4: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);
            $('.scheduling_appointment').show();
            $('.scheduling_appointment').show();
            $('.scheduling_appointment').show();
//                  $('.appointment_confirmed').css('display','flex');
            $('.appointment_confirmed').hide();
            $button.attr('disabled', false);
        },
        appointment_error_edit: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            document.getElementsByName('validation_check')[0].value = 1;
            var $div = $(ev.currentTarget).closest('div');
            var $button = $(ev.currentTarget).closest('.next');
            $button.attr('disabled', true);
            $('.scheduling_appointment').show();
            $('.scheduling_appointment').show();
            $('.scheduling_appointment').show();

            $('.appointment_error').hide();
            $button.attr('disabled', false);
        },
        appointment_error_not_sure: function (ev) {
            document.getElementsByName('not_sure')[0].value = 1;
            this.on_click_tab4(ev);
        },
        show_calender: function (ev) {
            var self = this;
            if (ev != undefined){
                ev.preventDefault();
                ev.stopPropagation();
            }
            var data = {};
            self = self;
            $("#tab2_box .calender").addClass("col-lg-12");
            $("#tab2_box .calender").html(
            "<br/><br/><br/><div class='row'><div class='col-lg-4'/><div class='col-lg-4'><h3>Refreshing ...</div><div class='col-lg-4'/></div></h3>");
            data.doctor = $("input[name='doctor']:checked").val();
            data.branch = parseInt($('input[name="branch"]').val());
            return ajax.jsonRpc('/online_appointment/doctor_calender', 'call', data).then(function (modal) {
                $("#tab2_box .calender").html(modal);
                $('#tab2_box .calender .fa-chevron-left')
                    .off('click')
                    .click(function (ev) {
                        self.show_calender_left(ev);
                    });
                $('#tab2_box .calender .fa-chevron-right')
                    .off('click')
                    .click(function (ev) {
                        self.show_calender_right(ev);
                    });
            });
        },
        show_calender_left: function (ev) {
            var self = this;
            ev.preventDefault();
            ev.stopPropagation();
            var data = {};
            $("#tab2_box .calender").addClass("col-lg-12");
            data.end_date = $('#tab2_box .fa-chevron-left').attr('value')
            $("#tab2_box .calender").html(
            "<br/><br/><br/><div class='row'><div class='col-lg-4'/><div class='col-lg-4'><h3>Refreshing ...</div><div class='col-lg-4'/></div></h3>");
            data.doctor = $("input[name='doctor']:checked").val();
            data.branch = parseInt($('input[name="branch"]').val());
            return ajax.jsonRpc('/online_appointment/doctor_calender', 'call', data).then(function (modal) {
                $("#tab2_box .calender").html(modal);
                $('#tab2_box .calender .fa-chevron-left')
                    .off('click')
                    .click(function (ev) {
                        self.show_calender_left(ev);
                    });
                $('#tab2_box .calender .fa-chevron-right')
                    .off('click')
                    .click(function (ev) {
                        self.show_calender_right(ev);
                    });
            });
        },
        show_calender_right: function (ev) {
            var self = this;
            ev.preventDefault();
            ev.stopPropagation();
            var data = {};
            $("#tab2_box .calender").addClass("col-lg-12");
            data.start_date = $('#tab2_box .fa-chevron-right').attr('value')
            $("#tab2_box .calender").html(
            "<br/><br/><br/><div class='row'><div class='col-lg-4'/><div class='col-lg-4'><h3>Refreshing ...</div><div class='col-lg-4'/></div></h3>");
            data.doctor = $("input[name='doctor']:checked").val();
            data.branch = parseInt($('input[name="branch"]').val());
            return ajax.jsonRpc('/online_appointment/doctor_calender', 'call', data).then(function (modal) {
                $("#tab2_box .calender").html(modal);
                $('#tab2_box .calender .fa-chevron-left')
                    .off('click')
                    .click(function (ev) {
                        self.show_calender_left(ev);
                    });
                $('#tab2_box .calender .fa-chevron-right')
                    .off('click')
                    .click(function (ev) {
                        self.show_calender_right(ev);
                    });
            });
        },
    });
});