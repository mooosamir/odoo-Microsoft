from odoo import api, fields, models, _


class ContactLensAnnualSupply(models.Model):
    _name = 'contact.lens.annual.supply'

    inventory_category = fields.Selection([
        ('contact_lens__replacement_schedule_id', 'Contact Lens/Replacement Schedule'),
        ('contact_lens__name', 'Contact Lens/Name'),
    ], string='Inventory Category', required=True)
    selection_contact_lens_replacement_schedule = fields.Many2many('spec.contact.lens.replacement.schedule',
                                                                   string='Selection', relation='new_contact_lens')
    many2many_field_selection = fields.Many2many('product.template', string='Selection')
    compute_selection = fields.Char(compute='compute_selection_field', string='Selection')
    min_quantity = fields.Integer(string='Min Qty')
    discount = fields.Float(string='Discounts')
    discount_type = fields.Selection([('amount','Amount'),('percent','Percent')])
    promotion_form_id = fields.Many2one('promotion.form', string='Inventory Details')


    @api.depends('selection_contact_lens_replacement_schedule','many2many_field_selection')
    def compute_selection_field(self):
        for s in self:
            s.compute_selection = ""
            if s.selection_contact_lens_replacement_schedule:
                for val in s.selection_contact_lens_replacement_schedule:
                    s.compute_selection += val.name + ", "
            elif s.many2many_field_selection:
                for val in s.many2many_field_selection:
                    s.compute_selection += val.name + ", "

            s.compute_selection = s.compute_selection[0:-2]

    @api.onchange('inventory_category')
    def on_change(self):

        if self.inventory_category == 'contact_lens__name':
            return {'domain': {'many2many_field_selection': [('prd_categ_name', '=', 'Contact Lens')]}}


