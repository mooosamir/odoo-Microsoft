# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Meeting(models.Model):
    _inherit = 'calendar.event'
    _description = "Appointment"


    @api.depends('patient_id')
    def _compute_appintment_name(self):
        for rec in self:
            if rec.patient_id:
                rec.update({'name':rec.patient_id.display_name})

    @api.depends('start', 'stop')
    def _compute_appointment_duration(self):
        """ Get the duration value between the 2 given dates. """
        duration = 00
        for rec in self:
            if rec.start and rec.stop:
                diff = fields.Datetime.from_string(rec.stop) - fields.Datetime.from_string(rec.start)
                if diff:
                    duration = float(diff.days) * 24 + (float(diff.seconds) / 60)
            rec.update({'appointment_duration':int(duration)})

    name = fields.Char(compute="_compute_appintment_name", string='Meeting Subject', required=False, store=True)
    patient_id = fields.Many2one('res.partner', string="Patient")
    service_type = fields.Many2one('product.template', domain="[('prd_categ_name','=','Services')]", string="Service")
    insurance_id = fields.Many2one('spec.insurance', string="Insurance")
    phone = fields.Char(related='patient_id.phone', string="Phone")
    user_id = fields.Many2one('res.users', string='Resource', default=lambda self: self.env.user, readonly="False")
    pre_appointment = fields.Boolean(string="Pre-Appointment")
    appointment_date = fields.Date(string="Appointment Date")
    appointment_time = fields.Float(string="Appointment Time")
    confirmation_status = fields.Selection([('none', 'None'), ('left_message', 'Left Message'), ('not_available', 'Not Available'),
                                            ('confirmed', 'Confirmed')], default='none', string="Confirmation Status")
    appointment_status = fields.Selection([('none', 'Scheduled'), ('no_show', 'No Show'), ('checked_in', 'Checked In'), ('checked_out', 'Checked Out'),
                                           ('walk_in', 'Walk In'), ('cancel', 'Cancelled')], default='none', string="Appointment Status")
    notes = fields.Text(string="Notes")
    employee_id = fields.Many2one('hr.employee', string="Provider")
    preferred_location_id = fields.Many2one('res.company', "Location")
    telehealth = fields.Boolean(string="Telehealth")
    appointment_duration = fields.Integer(compute="_compute_appointment_duration", string='Duration')

    @api.constrains('patient_id', 'start_datetime', 'employee_id')
    def _check_appointment_clash(self):
        if not self._context.get('detaching'):
            for rec in self:
                self._cr.execute("""SELECT 
                                        id
                                    FROM
                                        calendar_event
                                    WHERE
                                        active = True AND
                                        id != %d AND
                                        employee_id = %d AND
                                        patient_id = %d AND
                                        appointment_status != 'rescheduled' AND
                                        (start_datetime, stop_datetime) OVERLAPS ('%s', '%s')
                                    LIMIT 1 """ % (rec.id, rec.employee_id.id, rec.patient_id.id,
                                    rec.start_datetime,
                                    rec.stop_datetime))
                if self._cr.fetchone():
                    raise ValidationError(_("Another appointment is already scheduled, would you still like to create an appointment?"))

    @api.onchange('patient_id')
    def _onchange_patient(self):
        self.partner_ids = False
        if self.patient_id:
            self.update({'partner_ids': [(6,0, [self.patient_id.id])]})
