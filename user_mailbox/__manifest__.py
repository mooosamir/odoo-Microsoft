# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{

    # Module information
    'name': 'User Mailbox',
    'category': 'Extra Tools',
    'sequence': 1,
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """
        User Based E-Mail SMTP/IMAP.
        User mailbox module provide a feature to configure IMAP
        and SMTP gateway user wise. With the help of this feature
        user can send a mail through user's own configured mail id.
    """,
    'description': """
        User Based E-Mail SMTP/IMAP.
        User mailbox module provide a feature to configure IMAP
        and SMTP gateway user wise. With the help of this feature
        user can send a mail through user's own configured mail id.
    """,

    # Author
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependencies
    'depends': ['fetchmail', 'mail_bot'],

    # Views
    'data': [
        "views/in_out_mail_server_view.xml",
        "views/res_users_view.xml"
    ],

    # Odoo App Store Specific
    'images': ['static/description/odoo-app-banner-user-mailbox.jpg'],

    # Technical
    'installable': True,
    'auto_install': False,
    'price': 99,
    'currency': 'EUR',
}
