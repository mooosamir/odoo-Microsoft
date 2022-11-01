from odoo import fields, models, api


class Diagnosis(models.Model):
	_name = "diagnosis.setup"

	name = fields.Char("Code")
	description = fields.Char("Description")

	@api.model
	def create(self, vals):
		name = vals.get('name')
		name = name.upper()
		res = super(Diagnosis, self).create({'name':name, 'description': vals.get('description')})
		return res

	def write(self, vals):
		name = vals.get('name')
		name = name.upper()
		res = super(Diagnosis, self).write({'name':name, 'description': vals.get('description')})
		return res