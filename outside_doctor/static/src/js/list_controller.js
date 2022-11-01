odoo.define('outside_doctor.list_controller', function (require) {
    var ListView = require('web.ListView');
    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function ($node) {
            var self = this;
            rec = this._super($node)
            if (self.$buttons){
                self.$buttons.on('click', '.import_out_side_doctor', function () {
                    self._importdoctorClick(this);
                });
                self.$buttons.on('click', '.emoployee_inside_doctor_class', function () {
                    self._emoployee_inside_doctor_class(this);
                });
                self.$buttons.on('click', '.outside_emoployee_inside_doctor_class', function () {
                    self._outside_emoployee_inside_doctor_class(this);
                });
            }
            return rec
        },
        _importdoctorClick: function (event) {
            var self = this
            self.do_action({
                name:'Import Outside Doctor',
                type: 'ir.actions.client',
                tag:'outside_doctor',
            })
        },
        _emoployee_inside_doctor_class: function (event) {
            var self = this
            self.do_action({
                tag: 'outside_doctor',
                target: 'current',
                type: 'ir.actions.client',
                name: 'Npi Import Employee',
                display_name: 'Npi Import Employee',
                context: {
                        is_employee: true,
                        no_user_create: true,
                },
            });
        },
        _outside_emoployee_inside_doctor_class: function (event) {
            var self = this
            self.do_action({
                tag: 'outside_doctor',
                target: 'current',
                type: 'ir.actions.client',
                name: 'Npi Import Outside Doctor',
                display_name: 'Npi Import Outside Doctor',
                context: {
                        no_user_create: true,
                },
            });
        },

    })

});