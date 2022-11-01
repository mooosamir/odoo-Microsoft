# See LICENSE file for full copyright and licensing details.

{
    "name": "RMA - Return Merchandise Authorization Return Exchange "
            "Management",
    "version": "13.0.1.0.0",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "summary": '''Return merchandise authorization
    RMA Return goods
    Exchange goods
    Credit notes
    Replace item
    Goods Return Refund,
    Exchange,
    Payback
    ''',
    "website": "http://www.serpentcs.com",
    "description": '''Return merchandise authorization module helps
    you to manage with product returns and exchanges.
    RMA Return goods
    Exchange goods
    Credit notes
    Replace item
    Goods Return Refund,
    Exchange,
    Payback''',
    "license": 'LGPL-3',
    "depends": ['sale_management', 'stock', 'purchase', 'opt_custom'],
    "category": "Warehouse",
    "sequence": 1,
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'data/rma_data.xml',
        #     'views/res_company.xml',
            'views/rma_view.xml',
            'views/sale_views.xml',
            'views/purchase_views.xml',
            'views/stock_views.xml',
            'report/report_mer_auth_rma.xml',
            'report/rma_report_mer_auth_reg.xml',
            'data/reason_data.xml',
    ],
    'images': ['static/description/rma.png'],
    'installable': True,
    'price': 53,
    'currency': 'EUR',
    'pre_init_hook': 'pre_init_hook',
}
