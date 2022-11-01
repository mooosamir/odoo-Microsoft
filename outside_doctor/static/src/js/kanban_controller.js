odoo.define('outside_doctor.kanban_controller', function (require) {
    var KanbanController = require('web.KanbanController');

    KanbanController.include({
        renderButtons: function () {
            this._super.apply(this, arguments); // Sets this.$buttons
            if (!this.$buttons) {
                return;
            }
            var self = this;
            this.$buttons.on('click', '.emoployee_inside_doctor_class', function () {
                    self._emoployee_inside_doctor_class(this);
            });
            this.$buttons.on('click', '.outside_emoployee_inside_doctor_class', function () {
                    self._outside_emoployee_inside_doctor_class(this);
            });
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

    });



});