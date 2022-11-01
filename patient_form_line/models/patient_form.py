from odoo import api, fields, models, _


class PatientFormLine(models.Model):
    _name = 'patient.form.line'
    _description = 'patient.form.line'

    intake_form_name = fields.Char(string='Intake Form Name')
    welcome_message = fields.Text(string='Welcome Message', default='Welcome')
    completed_message = fields.Text(string='Completed Message')
    appointment_ids = fields.Many2one('product.template',string='Appointment Selection', domain=[('categ_id.name','=','Services'),('appointment_checkbox','=',True)])
    settings_id = fields.Many2one('pe.settings')

