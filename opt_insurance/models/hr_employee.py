from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def name_get(self):
        result = []
        for res in self:
            result.append((res.id, "%s%s%s%s" % (res.last_name if res.last_name else '', " " + res.first_name if res.first_name else '', " " + res.middle_name if res.middle_name else ''," " + res.credential if res.credential else '')))
        # result = super(ResPartner, self).name_get()
        return result

    title = fields.Char('Title')
    middle_name = fields.Char('Middle Name')
    active = fields.Boolean('Active')
    website = fields.Char(String="Website")

    def open_user_from_employee(self):
        email = self.private_email
        user = self.env['res.users'].search([('login','=',email)])
        if user.id:
            return {
                'name': _('Users'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'res.users',
                'type': 'ir.actions.act_window',
                # 'domain': [('login','=', email)],
                'res_id': user.id,
                'views': [(self.env.ref('base.view_users_form').id, 'form')],
                # 'context': context,
                # 'target': 'fullscreen'
            }
        else:
            raise UserError("No user created for this Employee.")

    provide = fields.Selection(
        [('outside_provide', 'Outside'), ('provide', 'In-House')], default='outside_provide', string="outside")
    first_name = fields.Char(string="Frist Name")
    last_name = fields.Char(string="Last Name")
    # credential = fields.Selection([('od', 'OD'), ('md', 'MD'),
    #                                ('do', 'DO'), ('abo', 'ABO'), ('Staff', 'Staff')], string="Credential")
    signature = fields.Binary(string="Signature")
    signature_date = fields.Date(string="Signature Date")
    fax = fields.Char(string="Fax")
    ein = fields.Integer(string="EIN")
    license = fields.Char(string="License")
    dea = fields.Char(string="DEA")
    npi = fields.Char(string="NPI")
    npi_type = fields.Selection(
        [('group', 'Group'), ('individual', 'Individual')], default="group", string="NPI type")
    taxonomy = fields.Char(string="Taxonomy")
    # online_appointment = fields.Boolean(string='Online Appointment')
    appointment = fields.Boolean(
        string='Appointment')
    allow_overbooks = fields.Integer(string="Allow Overbooks")
    duration = fields.Float(string="Duration")
    insurance_ids = fields.One2many(
        'spec.employee.insurance', 'employee_id', string="Insurance")
    color = fields.Char(string="Color")
    prefix = fields.Char('Prefix',index=True)
    credential = fields.Char("Credential")

    # below fields are created by Siddhant Kaushik
    nick_name = fields.Char("Nick Name")
    street = fields.Char("street 1")
    street2 = fields.Char("street 2")
    city = fields.Char(string="City")
    state_id = fields.Many2one("res.country.state", string="State")
    country_id = fields.Many2one("res.country", string="State")
    zip = fields.Char("Zip")
    ssn = fields.Char("SSN")
    personal_status = fields.Boolean('Active', default=True)
    security_group = fields.Many2one("employee.role", string="Employee Role")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="hr.group_hr_user", default="", tracking=True)
    private_email = fields.Char(related='', string="Private Email", groups="hr.group_hr_user")
    phone = fields.Char(related='', related_sudo=False, string="Private Phone", groups="hr.group_hr_user")
    doctor = fields.Boolean("Provider")
    is_user_created = fields.Boolean()

    @api.onchange('first_name', 'last_name')
    def _onchange_name(self):
        name = ' '
        if self.first_name:
            name += self.first_name + ' ' or ''
        if self.last_name:
            name += self.last_name + ' ' or ''
        self.name = name

    @api.model
    def create(self, vals):
        name = vals.get('name')
        email = vals.get('private_email')
        security = vals.get('security_group')
        security_id = self.env['employee.role'].browse(security)
        user_vals={'name':name, 'login': email}
        # if not self._context.get('no_user_create', False) and vals.get('doctor'):
        #     user_vals.update({'doctor_type':'doctor', 'npi':vals.get('npi') })
        # if self._context.get('no_user_create', False) and vals.get('doctor'):
        #     user_vals.update({'doctor_type':'out_doctor', 'npi':vals.get('npi') })
        if vals.get('doctor'):
            user_vals.update({'doctor_type':'doctor', 'npi':vals.get('npi') })
        if vals.get('is_outside_doctor'):
            user_vals.update({'doctor_type':'out_doctor', 'npi':vals.get('npi') })
        user_id = self.env['res.users']
        if not self._context.get('no_user_create', False):
            user_id = self.env['res.users'].sudo().create(user_vals)
        else:
            if not vals.get('is_outside_doctor'):
                vals.update({'is_user_created': False})
        if user_id.id:
            vals.update({'address_home_id': user_id.partner_id.id})
            for rec in security_id.groups:
                user_id.groups_id = [(4, rec.id)]
        res = super(HrEmployee, self).create(vals)
        return res

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)
        if not self.is_user_created and self.private_email:
            name = vals.get('name')
            email = vals.get('private_email')
            user_vals = {'name': name, 'login': email}
            if self.doctor:
                user_vals.update({'doctor_type': 'doctor', 'npi': vals.get('npi')})
            elif self.is_outside_doctor:
                user_vals.update({'doctor_type': 'out_doctor', 'npi': vals.get('npi')})
            user_id = self.env['res.users']
            user_id = self.env['res.users'].sudo().create(user_vals)
            self.is_user_created = True
        if self.doctor and self.address_home_id:
            self.address_home_id.write({'doctor_type':'doctor', 'npi':self.npi})
        return res


class EmployeeInsurance(models.Model):
    _name = 'spec.employee.insurance'
    _description = 'Employee Insurance'

    name = fields.Char(string="Insurance")
    npi_type = fields.Selection(
        [('group', 'Group'), ('individual', 'Individual')], default="group", string="NPI type")
    #field type is changed to Char of following billing_npi,rendering_provider_npi and tax_id by Siddhant Kaushik
    billing_npi = fields.Char(string="Billing NPI")
    rendering_provider_npi = fields.Char(string="Rendering NPI")
    tax_id = fields.Char(string="Tax ID")
    employee_id = fields.Many2one('hr.employee', string="Employee")