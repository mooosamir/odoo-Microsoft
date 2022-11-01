# -*- coding: utf-8 -*-
{
    'name': "Promotion Program",
    'summary': """ """,
    'description': """
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale_coupon', 'sale', 'opt_custom'],
    'data': [
        'security/ir.model.access.csv',
        'views/promotion_form_view.xml',
        # 'views/promotion_client_action.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/apply_promotion_client_action.xml',
    ],
}
