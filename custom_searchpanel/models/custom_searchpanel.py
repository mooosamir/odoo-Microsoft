# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api


class CustomSearchPanel(models.Model):
    _name = 'custom.searchpanel'

    def search(self, domain, model):
        domains = json.loads(domain)
        data = self.env[model].search(domains['domain'], limit=domains['limit'], order=domains['order'])
        values = []
        for row in data:
            values.append({
                'id': row.id,
                'name': row.name,
                'dob': row.age,
                'ids': row.ids,
            })
        return values
