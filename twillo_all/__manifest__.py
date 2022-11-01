# -*- coding: utf-8 -*-
{
    'name': "twillo_all",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['twilio'],
    },
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/twilio.xml',
        'views/res_config_settings_view.xml',
    ],
}
