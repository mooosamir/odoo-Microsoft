odoo.define('ks_theme_kernel.ks_special_icon_widget', function (require) {
"use strict";

var core = require('web.core');
var basic_fields = require('web.basic_fields');
var registry = require('web.field_registry');
var Widget = require('web.Widget');
var weWidgets = require('wysiwyg.widgets');

var QWeb = core.qweb;

var KsSpecialIconsWidget = basic_fields.FieldBinaryImage.extend({

    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        this.ksSelectedIconKernel = false;
        // threeD, twoD, default
        this.ks_icon_set_kernel = [
            ['account_accountant.png', 'account_asset.png', 'account_invoicing.png', 'Calendar.png', 'Contacts.png', 'CRM.png', 'Dashboard.png', 'delivery_bpost.png', 'delivery_dhl.png', 'delivery_fedex.png', 'delivery_ups.png', 'Fleet.png', 'Gamification.png', 'Google_Calendar.png', 'Google_Drive.png', 'HelpDesk.png', 'Holiday.png', 'HR.png', 'HR_Appraisal.png', 'HR_Attendance.png', 'HR_Expense.png', 'HR_Payroll.png', 'HR_Recruitment.png', 'HR_TimeSheet.png'],
            ['Account-Asset.png', 'Account_Invoice.png', 'Account-SEPA.png', 'Board.png', 'Calendar.png', 'Contact.png', 'CRM.png', 'Delivery_Bpost.png', 'Delivery_UpS.png', 'Delivery_USPS.png', 'DHL.png', 'Event.png', 'Fedex-Delivery.png', 'Fleet.png', 'Gamification.png', 'Helpdesk.png', 'HR.png', 'HR-Appraisal.png', 'HR-Attendance.png', 'HR-Expense.png', 'HR-Holidays.png', 'HR-Payroll.png', 'HR-Rcruitment.png', 'IM-Livechat.png', 'Limited-Stock.png', 'Lunch.png', 'Mail.png', 'Mail-Github.png', 'Mail-Push.png', 'Maintenace.png', 'Modules.png', 'MRP.png', 'MRP-Maintenance.png', 'MRP-PLM.png', 'Notes.png', 'Payment.png', 'POS.png', 'Project.png', 'Project_Forecast.png', 'Purchase.png', 'Qulaity.png', 'Repair.png', 'Sale.png', 'Sale-Managemnt.png', 'Sale-Subscription.png', 'Setting.png', 'Stock-Barcode.png', 'Survey.png', 'VOIP.png', 'Website.png', 'Website_Blog.png', 'Website_Caladendar.png', 'Website_CRM.png', 'Website_CRM_Partenr.png', 'Website_CRM_Score.png', 'Website_Customer.png', 'Website_Editor.png', 'Website_Enterprise.png', 'Website_Event.png', 'Website_Event_Sale.png', 'Website_Event_Track.png', 'Website_Forum.png', 'Website_Forum_Doc.png', 'Website_Gengo.png', 'Website_HR.png', 'Website_HR-Recruitmentt.png', 'Website_Livechat.png', 'Website_Mail_Channel.png', 'Website_Membership.png', 'Website_Partner.png', 'Website_Payment.png', 'Website_Qoute.png', 'Website-_Question.png', 'Website_Rating.png', 'Website_Sale.png', 'Website_Sale_Delivery.png', 'Website_Sale_Option.png', 'Website_Sign.png', 'Website_Slide.png', 'Website_Theme_Installed.png', 'Website_Twitter.png', 'Website_Versions.png', 'Webstudio.png'],
            ['account_accountant.png', 'account_asset.png', 'account_invoicing.png', 'account_sepa.png', 'board.png', 'calendar.png', 'contacts.png', 'crm.png', 'delivery_bpost.png', 'delivery_dhl.png', 'delivery_fedex.png', 'delivery_ups.png', 'delivery_usps.png', 'event.png', 'fleet.png', 'gamification.png', 'google_calendar.png', 'google_drive.png', 'helpdesk.png', 'hr.png', 'hr_appraisal.png', 'hr_attendance.png', 'hr_expense.png', 'hr_holidays.png', 'hr_payroll.png', 'hr_recruitment.png', 'hr_timesheet.png', 'im_livechat.png', 'lunch.png', 'mail.png', 'mail_github.png', 'mail_push.png', 'maintenance.png', 'marketing_automation.png', 'mass_mailing.png', 'membership.png', 'modules.png', 'mrp.png', 'mrp_maintenance.png', 'mrp_plm.png', 'note.png', 'payment.png', 'point_of_sale.png', 'project.png', 'project_forecast.png', 'purchase.png', 'quality_control.png', 'repair.png', 'sale.png', 'sale_management.png', 'sale_subscription.png', 'settings.png', 'stock.png', 'stock_barcode.png', 'survey.png', 'voip.png', 'website.png', 'website_blog.png', 'website_calendar.png', 'website_crm.png', 'website_crm_partner_assign.png', 'website_crm_score.png', 'website_customer.png', 'website_enterprise.png', 'website_event.png', 'website_event_questions.png', 'website_event_sale.png', 'website_event_track.png', 'website_form_editor.png', 'website_forum.png', 'website_forum_doc.png', 'website_gengo.png', 'website_hr.png', 'website_hr_recruitment.png', 'website_livechat.png', 'website_mail_channel.png', 'website_membership.png', 'website_partner.png', 'website_payment.png', 'website_quote.png', 'website_rating_project.png', 'website_sale.png', 'website_sale_delivery.png', 'website_sale_options.png', 'website_sign.png', 'website_slides.png', 'website_theme_install.png', 'website_twitter.png', 'website_version.png', 'web_studio.png']
        ];
    },

    template: 'KsFieldBinaryImageKernel',

    events: _.extend({}, basic_fields.FieldBinaryImage.prototype.events, {
        'click .ks_image_widget_icon_container_kernel': 'ks_image_widget_icon_container_kernel', // View container
//        'click .ks_icon_container_close_button': 'ks_icon_container_close_button',
    }),

     _render: function () {
         this._super.apply(this, arguments);
         var ks_self = this;
     },

     //This will show modal box on clicking on open icon button.
     ks_image_widget_icon_container_kernel: function (e) {
        var ks_self = this;
        if (this.ks_icon_modal_destroy || $('#ks_kernel_icon_container_modal_id')[0]){
            $('#ks_kernel_icon_container_modal_id')[0].remove();
        }
            this.ks_icon_modal_destroy = $($(QWeb.render('KsSpecialIconView', {
                ks_special_icons_set: this.ks_icon_set_kernel
            })).modal('show')).css('z-index','1111');

            //To add class on selected element
            $(this.ks_icon_modal_destroy).find('.ks_special_icon_list').click(function(ev){
                var self = this;
                ks_self.ksSelectedIconKernel = $(ev.currentTarget).find('img').attr('src');
                _.each($('.ks_special_icon_list'), function (selected_icon) {
                    $(selected_icon).removeClass('ks_icon_selected');
                });
                $(ev.currentTarget).addClass('ks_icon_selected');
            });

            // To select the Icon
            $(this.ks_icon_modal_destroy).find('.ks_icon_container_open_button_kernel').click(function(ev){
                var self = this;

                var convertImgToDataURLviaCanvas = function(url, callback) {
                    var img = new Image();

                    img.crossOrigin = 'Anonymous';

                    img.onload = function() {
                        var canvas = document.createElement('CANVAS');
                        var ctx = canvas.getContext('2d');
                        var dataURL;
                        canvas.height = this.height;
                        canvas.width = this.width;
                        ctx.drawImage(this, 0, 0);
                        dataURL = canvas.toDataURL();
                        callback(dataURL);
                        canvas = null;
                    };
                    img.src = url;
                }
                convertImgToDataURLviaCanvas(ks_self.ksSelectedIconKernel, function( base64_data ) {
                    ks_self.$el.children('img')[0].src = base64_data;
                    ks_self._rpc({
                        model: 'ks.menu.icon.singleton',
                        method: 'create',
                        args: [{'ks_attachment': base64_data}]
                    });
                });
            });
     },

});

registry.add('ks_special_icon_widget', KsSpecialIconsWidget);

return {
    KsSpecialIconsWidget: KsSpecialIconsWidget,
};
});