odoo.define('contact_lens_import.contact_lens_import', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var contact_lens_import = AbstractAction.extend({
        template: 'contact_lens_import_wizard',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'click #cli_import': 'import_clicked',
            'click #cli_cancel': 'cancel_clicked',
        },
        start: function () {
            return this._super();
        },
        willStart: function() {
            var self = this;
            return Promise.all([
                this._super.apply(this, arguments),
                ]);
        },
        init: function(parent, args) {
            var self = this;
            this.error_stack = [];
            this._super(parent, args);
            this.controlPanelParams.context.dialog_size = 'medium';
            this.controlPanelParams.context.renderFooter = false;
        },
        cancel_clicked: function(ev){
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window_close'
            })
        },
        import_clicked: function(ev){
            var self = this;

            if (!$('.contact_lens_import_wizard form input')[0].files.length)
                alert("Select file to continue.");
            else{
                self.cancel_clicked();
                var formData = new FormData();
                formData.append('datas', $('.contact_lens_import_wizard form input')[0].files[0]);
                var msg = ("<p>Importing Data, please wait<\p><p> this may take a few minutes ... </p>");
                $.blockUI({
                    'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                        '    <br />' + msg +
                        '</h2>'
                });
                self.send_to_server(formData,0,0,0);
            }
        },
        send_to_server: function(formdata, series_id, product_family_id, products_id){
            var self = this;
            $.ajax({
                   url : '/contact_lens_import/xml_import/?series_id=' + series_id + '&product_family_id=' + product_family_id + '&products_id=' + products_id,
                   type : 'POST',
                   data : formdata,
                   headers: {
                         'Cache-Control': 'max-age=0'
                   },
                   processData: false,  // tell jQuery not to process the data
                   contentType: false,  // tell jQuery not to set contentType
                   success : function(data) {
                        data = JSON.parse(data);
                        if (data[0] == '-1')
                            alert('Invalid XML file/format');
                        else if (data[0] == '0' && data[1] != '')
                            self.error_stack.push(0);
                        else if (data[0] == '0' && data[1] == '')
                            alert('Server error');
                        if (data[1] != '' && data[1] != '-1')
                            self.send_to_server(formdata, data[1], data[2], data[3]);
                        if (data[1] == '-1'){
                            $.unblockUI();
                            if (data[0] == '1')
                                alert('Data Imported');
                        }
                   },
                   error: function (jqXHR, status, err) {
                        $.unblockUI();
                        console.log(err);
                   },
            });
       }

    });

    core.action_registry.add("contact_lens_import", contact_lens_import);
    return contact_lens_import;
});