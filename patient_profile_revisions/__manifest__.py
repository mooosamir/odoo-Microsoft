# -*- coding: utf-8 -*-
{
    'name': "patient_profile_revisions",
    'summary': """
    """,

    'description': """
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'opt_custom', 'web_confirm_on_save'],
    'external_dependencies': {
        'python': ['twilio'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security_rules.xml',

        'views/assets.xml',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/spec_contact_lenses.xml',
        'report/prescription_report.xml',
        'wizard/manufacturer_options.xml',
        'wizard/mail_compose_message.xml',
        'wizard/base_partner_merge_automatic_wizard.xml',

    ],
}
