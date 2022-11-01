from odoo import fields, models


class KsPartner(models.Model):
    _inherit = "res.partner"

    ks_show_clock = fields.Boolean("Show clock", default=True)
    ks_time_format = fields.Selection([('hour24', '24-Hour'), ('hour12', '12-Hour')], "Time Format", required=True, default='hour24')
    ks_click_edit = fields.Boolean("Double Click Edit", default=True)


class KsUsers(models.Model):
    _inherit = "res.users"

    ks_show_clock = fields.Boolean(related="partner_id.show_clock", inherited=True, help="To display the Clock.")
    ks_time_format = fields.Selection(related="partner_id.ks_time_format", inherited=True,
                                      help="Select the time format for clock.")
    ks_click_edit = fields.Boolean(related="partner_id.ks_click_edit", inherited=True,
                                   help="Enable to edit the form on double click.")

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        ks_kernel_user = [
            'ks_show_clock',
            'ks_click_edit',
            'ks_time_format'
        ]
        init_res = super(KsUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = type(self).SELF_READABLE_FIELDS + ks_kernel_user
        type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + ks_kernel_user
        return init_res

    def is_ks_click_edit_enabled(self, request):
        value = self.env['res.users'].sudo().search_read([('id', '=', request.uid)], ['ks_click_edit'], limit=1)
        if value:
            return value[0]['ks_click_edit']
        else:
            return True
