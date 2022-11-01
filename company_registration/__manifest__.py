# -*- coding: utf-8 -*-
{
    'name': "company_registration",
    'summary': """ """,
    'description': """
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'base_setup', 'opt_custom', 'gws_google_maps'],
    'data': [
        'security/ir.model.access.csv',
        'views/company_view.xml',
        #'views/integrated_partner_view.xml',
        'views/default_label_view.xml',
        'views/res_config_settings.xml',
    ],
}
