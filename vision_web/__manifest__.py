# -*- coding: utf-8 -*-
{
    'name': "VisionWeb",
    'summary': """ """,
    'description': """ """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'opt_custom', 'ivis_order_grouping'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/res_company.xml',
        'views/res_config_settings_view.xml',
        'views/multi_order_type.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
}
