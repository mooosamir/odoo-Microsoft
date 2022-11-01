# -*- encoding: utf-8 -*-

import babel
import base64
import copy
import datetime
import dateutil.relativedelta as relativedelta
import logging

import functools
import lxml
from werkzeug import urls

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import pycompat

from odoo.tools.safe_eval import safe_eval
import dateutil.relativedelta as relativedelta


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': urls.url_quote,
        'urlencode': urls.url_encode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': functools.reduce,
        'map': map,
        'round': round,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw : relativedelta.relativedelta(*a, **kw),
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class AcsConsentFormTags(models.Model):
    _name = "acs.consent.form.tag"
    _description = "Document Tags"

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class AcsConsentForm(models.Model):
    _name = 'acs.consent.form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin', ]
    _description = 'Consent Form'

    READONLYSTATES = {'tosign': [('readonly', True)], 'signed': [('readonly', True)]}

    name = fields.Char(string='Name', required=True, readonly=False, copy=False, default="/", states=READONLYSTATES)
    subject = fields.Char(string='Subject', required=False, states=READONLYSTATES)
    partner_id = fields.Many2one('res.partner', string='Patient', ondelete="restrict", states=READONLYSTATES,
        help="Partner to whome Document asigned", domain=[('patient','=', True)])
    user_id = fields.Many2one('res.users', string='User', ondelete="restrict", states=READONLYSTATES, 
        help="User who provided Document")
    date = fields.Date('Date', default=fields.Date.today, states=READONLYSTATES)
    consent_form_content = fields.Html('Consent Form Content', states=READONLYSTATES)
    state = fields.Selection([
        ('draft','Draft'),
        ('tosign','To Sign'),
        ('signed','Signed')
    ], 'Status', default="draft", tracking=1) 
    template_id = fields.Many2one('acs.consent.form.template', string="Template", ondelete="restrict", states=READONLYSTATES)
    tag_ids = fields.Many2many('acs.consent.form.tag', 'ditial_document_tag_rel', 'consent_form_id', 'tag_id', 
        string='Tags', states=READONLYSTATES, help="Classify and analyze your Consent Forms")
    print_header_in_report = fields.Boolean(string="Print Header", default=False)
    company_id = fields.Many2one('res.company', ondelete='restrict', 
        string='Company', default=lambda self: self.env.user.company_id.id, states=READONLYSTATES)

    acs_signed_on = fields.Datetime("Signed On")
    acs_signature = fields.Binary("Signature")
    acs_has_to_be_signed = fields.Boolean("Tobe Signed", default=True)

    def action_to_sign(self):
        self.name = self.env['ir.sequence'].next_by_code('acs.consent.form')
        self.state = 'tosign'

    def action_signed(self):
        self.state = 'signed'

    @api.onchange('template_id')
    def onchange_template(self):
        if self.template_id:
            mako_env = mako_safe_template_env #if self.env.context.get('safe') else mako_template_env
            template = mako_env.from_string(tools.ustr(self.template_id.consent_form_content))

            variables = {
                'format_date': lambda date, format=False, context=self._context: format_date(self.env, date, format),
                'format_tz': lambda dt, tz=False, format=False, context=self._context: format_tz(self.env, dt, tz, format),
                'format_amount': lambda amount, currency, context=self._context: format_amount(self.env, amount, currency),
                'user': self.env.user,
                'ctx': self._context,  # context kw would clash with mako internals
            }

            variables['object'] = self
            try:
                consent_form_content = template.render(variables)
            except:
                consent_form_content = _('Please Select Required Fields first and then reselect template to render template properly.')
            self.consent_form_content = consent_form_content

    def unlink(self):
        for data in self:
            if data.state!='draft':
                raise UserError(('Record Can be deleted in draft state only.'))
        return super(AcsConsentForm, self).unlink()

    def get_portal_sign_url(self):
        return "/my/consentform/%s/sign" % (self.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    def preview_consent_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': "/my/consentforms/%s" % (self.id),
        }

    def _get_portal_return_action(self):
        """ Return the action used to display record when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('acs_consent_form.action_acs_consent_form')


class AcsConsentFormTemplate(models.Model):
    _name = 'acs.consent.form.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Consent Form Template'

    name = fields.Char("Template")
    consent_form_content = fields.Html('Consent Form Content')
    company_id = fields.Many2one('res.company', ondelete='restrict',
        string='Company', default=lambda self: self.env.user.company_id.id, required=True)


class Partner(models.Model):
    _inherit = 'res.partner' 

    def action_open_consent_form(self):
        action = self.env.ref('acs_consent_form.action_acs_consent_form').read()[0]
        action['domain'] = [('partner_id','=',self.id)]
        action['context'] = {'default_partner_id': self.id}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: