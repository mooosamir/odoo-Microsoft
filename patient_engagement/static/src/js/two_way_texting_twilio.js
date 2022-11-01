odoo.define('patient_engagement.two_way_texting_twilio', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var two_way_texting_twilio = AbstractAction.extend({
        template: 'two_way_texting',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'click #archived': 'archived_click',
            'click #not_archived': 'not_archived_click',
            'click #new_message': 'new_message',
            'keyup #new_search': 'new_search',
            'change #file': 'file_upload',
            'click #message_box .send': 'send_message',
            'click #emojis_picker' : 'display_emojis',
        },

//        willStart: function() {
//            return Promise.all([this._super.apply(this, arguments), this.get_patient_box()]);
//        },

        init: function(parent, args) {
            var self = this;
            this._super(parent, args);
            this.archived = false;
            this.get_branches();
            this.emojis = ["😀","😁","😂","😃","😄","😅","😆","😇","😈","😉","😊","😋","😌","😍","😎","😏","😐","😑","😒","😓","😔","😕","😖","😗","😘","😙","😚","😛","😜","😝","😞","😟","😠","😡","😢","😣","😤","😥","😦","😧","😨","😩","😪","😫","😬","😭","😮","😯","😰","😱","😲","😳","😴","😵","😶","😷","😸","😹","😺","😻","😼","😽","😾","😿","🙀","🙁","🙂","🙃","🙄","🙅","🙆","🙇","🙈","🙉","🙊","🙋","🙌","🙍","🙎","🙏","🤐","🤑","🤒","🤓","🤔","🤕","🤖","🤗","🤘","🤙","🤚","🤛","🤜","🤝","🤞","🤟","🤠","🤡","🤢","🤣","🤤","🤥","🤦","🤧","🤨","🤩","🤪","🤫","🤬","🤭","🤮","🤯","🤰","🤱","🤲","🤳","🤴","🤵","🤶","🤷","🤸","🤹","🤺","🤼","🤽","🤾","🤿","🥀","🥁","🥂","🥃","🥄","🥅","🥇","🥈","🥉","🥊","🥋","🥌","🥍","🥎","🥏","🥐","🥑","🥒","🥓","🥔","🥕","🥖","🥗","🥘","🥠","🥡","🥢","🥣","🥤","🥥","🥦","🥧","🥩","🥫","🥬","🥭","🥯","🥰","🥱","🥲","🥳","🥴","🥵","🥶","🥷","🥸","🥺","🥻","🥼","🥽","🥾","🥿","🦁","🦂","🦃","🦅","🦆","🦇","🦈","🦉","🦊","🦋","🦌","🦍","🦎","🦏","🦐","🦑","🦒","🦓","🦔"];
        },
        display_emojis : function(){
            if ($("#emoji_box").css('display') == "none")
                $("#emoji_box").css('display','block');
            else
                $("#emoji_box").css('display','none');
        },
        showEmoji : function(){
            var table = "<table><tbody><tr>";
            var emoji = 0;
            for (emoji in this.emojis){
                if (emoji % 10 == 0)
                    table += "</tr><tr>";
                table += '<td class="emoji">' + this.emojis[emoji] + "</td>";
            }

            table += "</tr></tbody></table>";
            $("#emoji_box").append(table);

            $('.emoji').hover(function() {
                $(this).css("cursor", "pointer");
            });

            $('.emoji').on('click',function(ev){
               $('#textArea').val($('#textArea').val() + $(ev.currentTarget).html());
            });
        },
        hide_chat_box: function(){
            $('.chat_patient_name').html('');
            $('.chat_patient_number').html('');
            $('#chat_box').html('');
            $('#message_box').hide();
        },
        set_as_archive: function(ev){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'set_patient_archive',
                args: [[], $(ev.currentTarget).attr('value')],
            }).then(function (result) {
                if (result)
                    $(ev.currentTarget).parent().remove();
                self.hide_chat_box();
            });
        },
        set_as_un_archive: function(ev){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'set_patient_un_archive',
                args: [[], $(ev.currentTarget).attr('value')],
            }).then(function (result) {
                if (result)
                    $(ev.currentTarget).parent().remove();
                self.hide_chat_box();
            });
        },
        archived_click: function(){
            this.archived = true;
            this.get_patient_box();
            this.hide_chat_box();
            $('#archived').hide();
            $('#not_archived').show();
        },
        not_archived_click: function(){
            this.archived = false;
            this.get_patient_box();
            this.hide_chat_box();
            $('#not_archived').hide();
            $('#archived').show();
        },
        new_message: function(){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'add_update_patient',
                args: [[], $('.company .selected_company').val()],
            }).then(function (result) {
                var $modal = $($(QWeb.render("twilio.add_patient_modal", {patient_list:result})));
                $modal.modal({backdrop: 'static', keyboard: false});
                $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
                $modal.appendTo('body').modal();
                $('.add_patient input[name="add_search"]')
                    .on('keyup',function (ev) {
                        self.update_new_message(ev);
                    });
                $('.add_patient .modal-body .radio_into_button input[name="add_patient"]')
                    .on('change',function (ev) {
                        self.add_new_patient_box(ev);
                        $('.modal.fade.show').remove();
                        $('.modal-backdrop.fade.show').remove();
                    });
            });
        },
        update_new_message: function(ev){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'add_update_patient',
                args: [[], $('.company .selected_company').val(), $('.add_patient input[name="add_search"]')[$('.add_patient input[name="add_search"]').length-1].value],
            }).then(function (result) {
                $('.add_patient .modal-body .radio_into_button').html($($(QWeb.render("twilio.update_patient_modal", {patient_list:result}))));
                $('.add_patient .modal-body .radio_into_button input[name="add_patient"]')
                    .on('change',function (ev) {
                        self.add_new_patient_box(ev);
                        $('.modal.fade.show').remove();
                        $('.modal-backdrop.fade.show').remove();
                    });
            });
        },
        new_search: function(){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'get_patient_box',
                args: [[], this.archived, $("#new_search").val(), $('.company .selected_company').val()],
            }).then(function (result) {
                $('#patient_box').html($(QWeb.render("twilio.patient_box", {patient_list:result})));
                $('#patient_box input[name="patient"]')
                    .on('change',function (ev) {
                        self.get_chat_box(ev);
                    });
                $('#patient_box .patient_box .archived')
                    .on('click',function (ev) {
                        self.set_as_archive(ev);
                    });
                $('#patient_box .patient_box .un_archived')
                    .on('click',function (ev) {
                        self.set_as_un_archive(ev);
                    });
            });
        },
        get_patient_box: function(){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'get_patient_box',
                args: [[], this.archived, "", $('.company .selected_company').val()],
//                method: 'read_group',
//                kwargs: {
//                    domain: [['message_sid', '!=', '']],
//                    fields: ['patient_id'],
//                    groupby: ['patient_id'],
//                },
//                lazy: false,
            }).then(function (result) {
                $('#patient_box').html($(QWeb.render("twilio.patient_box", {patient_list:result})));
                $('#patient_box input[name="patient"]')
                    .on('change',function (ev) {
                        self.get_chat_box(ev);
                    });
                $('#patient_box .patient_box .archived')
                    .on('click',function (ev) {
                        self.set_as_archive(ev);
                    });
                $('#patient_box .patient_box .un_archived')
                    .on('click',function (ev) {
                        self.set_as_un_archive(ev);
                    });
            });
        },
        add_new_patient_box: function(){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'get_patient_box',
                args: [[], this.archived, "", $('.company .selected_company').val(), $('.add_patient .modal-body .radio_into_button input[name="add_patient"]:checked').val()],
            }).then(function (result) {
                $('#patient_box .radio_into_button').append($(QWeb.render("twilio.update_patient_box", {patient_list:result})));
                $('#patient_box input[name="patient"]')
                    .on('change',function (ev) {
                        self.get_chat_box(ev);
                    });
                $('#patient_box .patient_box .archived')
                    .on('click',function (ev) {
                        self.set_as_archive(ev);
                    });
                $('#patient_box .patient_box .un_archived')
                    .on('click',function (ev) {
                        self.set_as_un_archive(ev);
                    });
                self.get_chat_box();
            });
        },
        get_chat_box: function(ev){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'get_chat_box',
                args: [[], $("input[name='patient']:checked").val()],
            }).then(function (result) {
                self.call('mail_service', 'getMailBus').trigger('twilio_notification_updated', {message_seen: result[2]});
                $('.chat_patient_name').html(result[0].name);
                $('.chat_patient_number').html(result[0].mobile);
                var chat_box = document.getElementById('chat_box')
                $('#chat_box').html($(QWeb.render("twilio.chat_box", {chat_box:result[1], patient:result[0]})));
                chat_box.scrollTop = chat_box.scrollHeight;
                $('#message_box').show();
                if (ev){
                    $(ev.currentTarget.parentElement).find('.unread_count').remove();
                    $(ev.currentTarget.parentElement).find('label').removeClass('bold');
                }
                $('#chat_box .chat_options')
                    .on('click',function (ev) {
                        if ($(ev.currentTarget).attr('value')== 'unread')
                            self.unread(ev);
                    });

            });
        },
        send_message: function(){
            var message = $('#message_box textarea').val();
            if (message !== '')
                this._rpc({
                    model: 'messaging.history',
                    method: 'send_message',
                    args: [[], $("input[name='patient']:checked").val(), message, $("input[name='messaging_history_id']").val()],
                }).then(function (result) {
                    $('#message_box textarea').val('');
                    $('#chat_box').append($(QWeb.render("twilio.chat_box", {chat_box:result[1], patient:result[0]})));
                    $("input[name='messaging_history_id']").val('0');
                });
        },
        get_quick_response: function(){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'get_quick_response',
                args: [[], $('.company .selected_company').val()],
            }).then(function (result) {
                $('#message_box .dropup-content').html($(QWeb.render("twilio.quick_response", {quick_response:result})));
                $('#message_box .dropup-content .quick_response')
                    .on('click',function (ev) {
                        $("#message_box textarea").val($(ev.currentTarget).attr('value'));
                    });
            });
        },
        get_branches: function(){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'get_branches',
                args: [[]],
            }).then(function (result) {
                $('.company .dropdown-content').html($(QWeb.render("twilio.branch", {branches:result[0]})));
                $('.company .selected_company').html(result[1][0].branch);
                $('.company .selected_company').val(result[1][0].id);
                self.showEmoji();
                self.get_patient_box();
                self.get_quick_response();
                $('.company .dropdown-content .branch')
                    .on('click',function (ev) {
                        self.set_branch(ev);
                    });
            });
        },
        set_branch: function(ev){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'set_branch',
                args: [[], $(ev.currentTarget).attr('value')],
            }).then(function (result) {
                $(".company .selected_company").val($(ev.currentTarget).attr('value'))
                $(".company .selected_company").html($(ev.currentTarget).html())
                self.get_patient_box();
                self.get_quick_response();
                self.hide_chat_box();
            });
        },
        unread: function(ev){
            var self = this;
            this._rpc({
                model: 'messaging.history',
                method: 'unread',
                args: [[], $(ev.currentTarget).attr('data-id')],
            }).then(function (result) {
                if (!result){
                    $(ev.currentTarget).remove();
                    self.call('mail_service', 'getMailBus').trigger('twilio_notification_updated', {message_received: 1});
                }
            });
        },
        file_upload: function(){
            var formData = new FormData();
            formData.append('messaging_history_id', $("input[name='messaging_history_id']").val());
            formData.append('image', $('input[type=file]')[0].files[0]);
                $.ajax({
                    url: 'two_way_chat/upload_document',
                    type: "POST",
                    enctype: 'multipart/form-data',
                    processData: false,
                    contentType: false,
                    data: formData,
                    success: function (result) {
                        console.log(result)
                        $("input[name='messaging_history_id']").val(result);
                    }
                });
        },

    });

    core.action_registry.add("two_way_texting_twilio", two_way_texting_twilio);
    return two_way_texting_twilio;
});