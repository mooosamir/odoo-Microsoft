# -*- coding: utf-8 -*-
{
    'name': "Remittance Advice",

    'summary': """Remittance Advice""",

    'description': """
        Add User Group
    """,

    'author': "MOH&ZA",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
    ],

}
