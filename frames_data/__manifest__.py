# -*- coding: utf-8 -*-
{
    'name': "frames_data",
    'summary': """ """,
    'description': """ """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'opt_custom', 'web_widget_image_url'],
    'external_dependencies': {
        'python': ['requests_futures'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/product_template.xml',
        'views/res_config_settings_view.xml',
        'data/ir_actions_server.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
}
