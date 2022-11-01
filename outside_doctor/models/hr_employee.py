from collections import defaultdict
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
# import pandas as pd
import requests
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils
import json
from odoo.exceptions import UserError

ROUNDING_FACTOR = 16


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('first_name', 'last_name')
    def onchange_name(self):
        for rec in self:
            if rec.is_outside_doctor:
                name_list = []
                name_list.append(rec.first_name or '')
                name_list.append(rec.last_name or '')
                name = ' '.join(name_list)
                rec.update({'name': name})

    is_outside_doctor = fields.Boolean(string="Outside Provider", default=False)
    mobile = fields.Char("Mobile")
    code = fields.Char("Code")
    license_doctor = fields.Char("License")
    medicaid = fields.Char("Medicaid")
    email = fields.Char("Email")
    website = fields.Char("Website")

    comment = fields.Text(string='Notes')

    # partner_id = fields.Many2one('res.partner',
    #                              string='Outside Provider',
    #                              delegate=True,
    #                              ondelete='restrict')

    def outside_emoployee_inside_doctor_class(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Import Outside Provider',
            'tag': 'outside_doctor',
            'context': {'no_user_create': 1}
        }
        return res

    def emoployee_inside_doctor_class(self):
        res = {
            'type': 'ir.actions.client',
            'name': 'Employee Import Data',
            'tag': 'outside_doctor',
            'context': {'is_employee': 1,
                        'no_user_create': 1}
        }
        print('res++++++++', res)
        return res

    @api.model
    def import_data(self):
        print('test$$$$$$$$$$$$$$$$$$$$$$$')

    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        print("employee", employee)
        return employee

    @api.model
    def get_api_data(self, data):
        ctx = data
        api = "https://npiregistry.cms.hhs.gov/api/"
        params = {}
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        if ctx.get('city'):
            params.update({'city': ctx.get('city')})
        params.update({'last_name': ctx.get('last_name'), 'state': ctx.get('state'), 'version': 2.1, 'limit': 200})
        try:
            response = requests.request("GET", api, params=params).text
            response_data = json.loads(response)
            if response_data and response_data.get('results'):
                dict_data = self.prepare_data(response_data)
                return dict_data
        except:
            raise UserError(_('Connection Failed!'))

    def doctor_class(self, datas):
        datas = datas[0]
        print('datasdatasdatasdatasdatasdatasdatas', datas)
        employee_obj = self.env['hr.employee']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        dict_data = {'exist_lst': [],
                     'data_lst': [],
                     'checked_rec': [datas]
                     }
        flag = False
        if not datas['data']:
            return {'message': "Please Select Record!"}
        for line in datas['data']:
            print('line=++++++++++++', line)
            inside_dc_exist = employee_obj.search([('npi', '=', line.get('npi'))])
            if inside_dc_exist:
                dict_data['exist_lst'].append(inside_dc_exist)
            if not inside_dc_exist:
                vals = {}
                if line.get('country'):
                    country_data = line.get('country').split('/')
                    country = country_data[0]
                    state = country_data[1]
                    country_id = country_obj.search([('code', '=', country)], limit=1)
                    state_id = state_obj.search([('country_id', '=', country_id.id), ('code', '=', state)], limit=1)
                    # vals.update({'country_id': country_id.id, 'state_id': state_id.id})
                vals.update({
                    'pin': line.get('zip'),
                    'name': line.get('last_name') + ' ' + line.get('first_name'),
                    'first_name': line.get('first_name'),
                    'last_name': line.get('last_name'),
                    'credential': line.get('credential'),
                    'prefix': line.get('prefix'),
                    'work_phone': line.get('phone'),
                    'phone': line.get('phone'),
                    'npi': line.get('npi'),
                    'npi_type': line.get('npi_type'),
                    'taxonomy': line.get('taxonomies'),
                    'license': line.get('license_doctor'),
                    'doctor': True,
                    'private_email': " ",
                    # 'state': state
                })
                print('hhhhhhhhhhhhhhhh', line.get('zip'), line.get('prefix'))
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>', vals)
                if 'no_user_create' in datas['context_data']:
                    doctor_id = inside_dc_exist.with_context(no_user_create=1).create(vals)
                else:
                    doctor_id = inside_dc_exist.create(vals)
                # doctor_id._onchange_name()
                dict_data['data_lst'].append(doctor_id.id)
                flag = True
        if len(dict_data['exist_lst']) == len(dict_data['checked_rec']):
            return {'message': "Provider already exists."}
        if flag:
            return {'data': dict_data['data_lst'],
                    'action': {
                        'name': "Provider",
                        'type': 'ir.actions.act_window',
                        'res_model': 'hr.employee',
                        'view_mode': 'tree,form',
                        'views': [(False, 'list'), (False, 'form')],
                        # 'views': [[self.env.ref('outside_doctor.outside_doctor_tree_view').id, 'list'],
                        #           [self.env.ref('outside_doctor.outside_doctor_form_view').id, 'form']],
                        'domain': [('id', 'in', dict_data['data_lst']), ('doctor', '=', True)],
                        'target': 'current'
                    }}

        else:
            return {'message': "Provider already exists."}

    def import_employee(self, datas):
        datas = datas[0]
        print('datasdatasdatasdatasdatasdatasdatas', datas)
        employee_obj = self.env['hr.employee']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        dict_data = {'exist_lst': [],
                     'data_lst': [],
                     'checked_rec': [datas]
                     }
        flag = False
        if not datas['data']:
            return {'message': "Please Select Record!"}
        for line in datas['data']:
            print('line=++++++++++++', line)
            inside_dc_exist = employee_obj.search([('npi', '=', line.get('npi'))])
            if inside_dc_exist:
                dict_data['exist_lst'].append(inside_dc_exist)
            if not inside_dc_exist:
                vals = {}
                if line.get('country'):
                    country_data = line.get('country').split('/')
                    country = country_data[0]
                    state = country_data[1]
                    country_id = country_obj.search([('code', '=', country)], limit=1)
                    state_id = state_obj.search([('country_id', '=', country_id.id), ('code', '=', state)], limit=1)
                    # vals.update({'country_id': country_id.id, 'state_id': state_id.id})
                vals.update({
                    'pin': line.get('zip'),
                    'name': line.get('last_name') + ' ' + line.get('first_name'),
                    'first_name': line.get('first_name'),
                    'last_name': line.get('last_name'),
                    'credential': line.get('credential'),
                    'prefix': line.get('prefix'),
                    'work_phone': line.get('phone'),
                    'phone': line.get('phone'),
                    'npi': line.get('npi'),
                    'npi_type': line.get('npi_type'),
                    'taxonomy': line.get('taxonomies'),
                    'license': line.get('license_doctor'),
                    'is_outside_doctor': True,
                    'private_email': " ",
                    # 'state': state
                })
                print('hhhhhhhhhhhhhhhh', line.get('zip'), line.get('prefix'))
                print('>>>>>>>>>>>>>>>>>>>>>>>>>>', vals)
                if 'no_user_create' in datas['context_data']:
                    doctor_id = inside_dc_exist.with_context(no_user_create=1).create(vals)
                else:
                    doctor_id = inside_dc_exist.create(vals)
                doctor_id._onchange_name()
                dict_data['data_lst'].append(doctor_id.id)
                flag = True
        if len(dict_data['exist_lst']) == len(dict_data['checked_rec']):
            return {'message': "Provider already exists."}
        if flag:
            return {'data': dict_data['data_lst'],
                    'action': {
                        'name': "Provider",
                        'type': 'ir.actions.act_window',
                        'res_model': 'hr.employee',
                        'view_mode': 'tree,form',
                        'views': [[self.env.ref('outside_doctor.outside_doctor_tree_view').id, 'list'],
                                  [self.env.ref('outside_doctor.outside_doctor_form_view').id, 'form']],
                        'domain': [('id', 'in', dict_data['data_lst']), ('is_outside_doctor', '=', True)],
                        'target': 'current'
                    }}
        else:
            return {'message': "Provider already exists."}

    @api.model
    def create_data(self, *args, **kwargs):
        # print('current_context++++++++++', kwargs, args[0]['context_data']['is_employee'])
        print('>>>>>>>>>>>>>>>>>>>>>         args[0//////////', args[0]['context_data'])
        if 'is_employee' not in args[0]['context_data']:
            return self.import_employee(args)
        else:
            print("***********************")
            return self.doctor_class(args)

    def prepare_data(self, response_data):
        # import_line_obj = self.env['doctor.import.line.wizard']
        lst = []
        sequence = 1
        for data in response_data['results']:
            city = ''
            phone = ''
            taxonomies = ''
            vals = {}
            if 'last_name' in data['basic']:
                vals.update({'last_name': data['basic']['last_name']})
            if 'first_name' in data['basic']:
                vals.update({'first_name': data['basic']['first_name']})
            if 'middle_name' in data['basic']:
                vals.update({'middle_name': data['basic']['middle_name']})
            if 'credential' in data['basic']:
                vals.update({'credential': data['basic']['credential']})
            if 'number' in data:
                vals.update({'npi': data['number']})
            if 'enumeration_type' in data:
                enumeration_type = 'Individual' if data['enumeration_type'] == 'NPI-1' else "Group"
                if enumeration_type == 'Individual':
                    vals.update({'npi_type': 'individual'})
                else:
                    vals.update({'npi_type': 'group'})
            if 'name_prefix' in data['basic']:
                vals.update({'prefix': data['basic']['name_prefix']})
            for address in data.get('addresses'):
                if address.get('address_purpose') == 'LOCATION':
                    if 'state' in address and address.get('state') not in [None, False, 'None', 'False']:
                        vals.update({'state': address.get('state')})
                    if 'postal_code' in address and address.get('postal_code') not in [None, False, 'None', 'False']:
                        vals.update({'zip': address.get('postal_code')})
                    if 'country_code' in address and address.get('country_code') not in [None, False, 'None', 'False']:
                        country = address.get('country_code') + "/" + address.get('state')
                        vals.update({'country': country})
                    if 'city' in address and address.get('city') not in [None, False, 'None', 'False']:
                        city = address.get('city')
                        vals.update({'city': city})
                    if 'telephone_number' in address and address.get('telephone_number') not in [None, False, 'None',
                                                                                                 'False']:
                        phone = address.get('telephone_number')
                        vals.update({'phone': phone})
                    if 'address_1' in address and address.get('address_1') not in [None, False, 'None', 'False']:
                        street = address.get('address_1')
                        vals.update({'street': street})
                    if 'address_2' in address and address.get('address_2') not in [None, False, 'None', 'False']:
                        street2 = address.get('address_2')
                        vals.update({'street2': street2})
            if 'taxonomies' in data and data.get('taxonomies') not in [None, False, 'None', 'False']:
                for taxo in data.get('taxonomies'):
                    if taxo.get('primary'):
                        if 'code' in taxo:
                            vals.update({'taxonomies': taxo.get('code')})
                        if 'license' in taxo:
                            vals.update({'license_doctor': taxo.get('license')})
            if 'identifiers' in data and data.get('identifiers') not in [None, False, 'None', 'False']:
                for taxo in data.get('identifiers'):
                    identifier = taxo.get('identifier')
                    if 'identifier' in taxo:
                        vals.update({'medicaid': identifier})
            vals.update({'sequence_id': sequence})
            lst.append(vals)
            sequence = sequence + 1
        print('lst++++++++++++++++++', lst)
        return lst

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if args is None:
            args = []
        if self._context.get('inside_outside_doctor', False):
            if ['is_outside_doctor', '=', True] in args and ['doctor', '=', True] in args:
                args.pop(args.index(['doctor', '=', True]) - 1)
                args.remove(['is_outside_doctor', '=', True])
                args.remove(['doctor', '=', True])
            domain1 = args.copy()
            domain2 = args.copy()
            domain1 += [('doctor', '=', True)]
            domain2 += [('is_outside_doctor', '=', True)]
            return super(HrEmployee, self).search(domain1, limit=8, order="last_name").name_get() + super(HrEmployee,
                                                                                                          self).search(
                domain2, limit=8).name_get()
        else:
            return super(HrEmployee, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)