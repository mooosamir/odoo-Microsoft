""""Inherited Mail Thread Model."""
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import dateutil
import email
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
import time
import threading
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from collections import namedtuple
from email.message import Message
from lxml import etree
from werkzeug import url_encode
from werkzeug import urls

from odoo import _, api, exceptions, fields, models, tools, \
    registry, SUPERUSER_ID
from odoo.osv import expression

from odoo.tools import pycompat, ustr
from odoo.tools.misc import clean_context, split_every
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    """"Inherited Mail Thread Model."""

    _inherit = 'mail.thread'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, body='',
                     subject=None, message_type='notification',
                     email_from=None,
                     author_id=None, parent_id=False,
                     subtype_id=False, subtype=None,
                     partner_ids=None, channel_ids=None,
                     attachments=None, attachment_ids=None,
                     add_sign=True, record_name=False, **kwargs):
        """Overridden method from base "Mail" Module."""
        self.ensure_one()
        # should always be posted on a record, use message_notify if no record
        # split message additional values from notify additional values
        msg_kwargs = dict((key, val) for key, val in kwargs.items()
                          if key in self.env['mail.message']._fields)
        notif_kwargs = dict((key, val)
                            for key, val in kwargs.items()
                            if key not in msg_kwargs)

        if self._name == 'mail.thread' or not self.id or \
                message_type == 'user_notification':
            raise ValueError('message_post should only be call to post'
                             ' message on record. Use message_notify instead')

        if 'model' in msg_kwargs or 'res_id' in msg_kwargs:
            raise ValueError("message_post doesn't support model and "
                             "res_id parameters anymore. "
                             "Please call message_post on record")

        # add lang to context imediatly since it will be
        # usefull in various flows latter.
        self = self.with_lang()

        # Explicit access rights check,
        # because display_name is computed as sudo.
        self.check_access_rights('read')
        self.check_access_rule('read')
        record_name = record_name or self.display_name

        partner_ids = set(partner_ids or [])
        channel_ids = set(channel_ids or [])

        if any(not isinstance(pc_id, int)
                for pc_id in partner_ids | channel_ids):
            raise ValueError('message_post partner_ids and '
                             'channel_ids must be integer list, not commands')

        # Find the message's author
        author_info = self._message_compute_author(
            author_id, email_from, raise_exception=True)
        author_id, email_from = \
            author_info['author_id'], author_info['email_from']

        if not subtype_id:
            subtype = subtype or 'mt_note'
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)

        # automatically subscribe recipients if asked to
        if self._context.get('mail_post_autofollow') and partner_ids:
            self.message_subscribe(list(partner_ids))

        MailMessage_sudo = self.env['mail.message'].sudo()
        if self._mail_flat_thread and not parent_id:
            parent_message = MailMessage_sudo.search([
                ('res_id', '=', self.id),
                ('model', '=', self._name),
                ('message_type', '!=', 'user_notification')],
                order="id ASC", limit=1)
            # parent_message searched in sudo for performance,
            # only used for id.
            # Note that with sudo we will match message with internal subtypes.
            parent_id = parent_message.id if parent_message else False
        elif parent_id:
            old_parent_id = parent_id
            parent_message = MailMessage_sudo.search(
                [('id', '=', parent_id), ('parent_id', '!=', False)], limit=1)
            # avoid loops when finding ancestors
            processed_list = []
            if parent_message:
                new_parent_id = parent_message.parent_id and \
                    parent_message.parent_id.id
                while (new_parent_id and new_parent_id not in processed_list):
                    processed_list.append(new_parent_id)
                    parent_message = parent_message.parent_id
                parent_id = parent_message.id

        values = dict(msg_kwargs)
        values.update({
            'author_id': author_id,
            'email_from': email_from,
            'model': self._name,
            'res_id': self.id,
            'body': body,
            'subject': subject or False,
            'message_type': message_type,
            'parent_id': parent_id,
            'subtype_id': subtype_id,
            'partner_ids': partner_ids,
            'channel_ids': channel_ids,
            'add_sign': add_sign,
            'record_name': record_name,
        })
        # ===============================================================
        # Added Below code by overriding the method to fix reply-to
        # email address issue when we receive the email.
        # we need the email address same that we are using in
        # outgoing mail server from User Form view.
        # ===============================================================
        if values.get('author_id', False):
            auther_rec = self.env['res.partner'].browse(values['author_id'])
            auther_user = auther_rec.user_ids and \
                auther_rec.user_ids[0] or False
            if auther_user and auther_user.outgoing_mail_server_ids:
                server_ids = auther_user.outgoing_mail_server_ids.ids
                auther_server = self.env['ir.mail_server'].\
                    search([('id', 'in', server_ids),
                            ('default', '=', True)], limit=1)
                if auther_rec and auther_server:
                    e_from = '"' + auther_rec.name + '" ' + \
                        '<' + auther_server.smtp_user + '>'
                    values.update({'email_from': e_from})
        # ===============================================================
        attachments = attachments or []
        attachment_ids = attachment_ids or []
        attachement_values = self._message_post_process_attachments(
            attachments, attachment_ids, values)
        values.update(attachement_values)  # attachement_ids, [body]

        new_message = self._message_create(values)

        # Set main attachment field if necessary
        self._message_set_main_attachment_id(values['attachment_ids'])

        if values['author_id'] and values['message_type'] != 'notification' \
                and not self._context.get('mail_create_nosubscribe'):
            # if self.env['res.partner'].browse(values['author_id']).active:
            # we dont want to add odoobot/inactive as a follower
            self._message_subscribe([values['author_id']])

        self._message_post_after_hook(new_message, values)
        self._notify_thread(new_message, values, **notif_kwargs)
        return new_message
