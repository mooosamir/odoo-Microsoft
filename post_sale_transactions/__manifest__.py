# -*- coding: utf-8 -*-
{
    'name': "Post Sale Transactions",
    'summary': """
        Post Sale Transactions""",
    'description': """
        Post Sale Transactions for Exchange, Remake, Warranty, Return
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'ivis_order_grouping'],
    'external_dependencies': {
        'python': ['stripe==2.64.0'],
    },
    'data': [
        'security/ir.model.access.csv',
        "report/sale_report.xml",
        # 'demo/payment_acquirer_data.xml',
        'views/assets.xml',
        'views/templates.xml',
        'views/post_sale_reasons.xml',
        'views/stock_picking.xml',
        'views/sale_order.xml',
        'views/sale_order_session.xml',
        'views/account_payment.xml',
        'views/payment_acquirer.xml',
        'views/payment_token.xml',
        'views/multi_order_type.xml',
        'views/account_move.xml',

        'data/sale_order_server_action.xml',

        'wizard/post_sale_transactions.xml',
        'wizard/multi_invoice_payment.xml',
        'wizard/balance_reporting.xml',

        'views/menu_items.xml',
        'views/res_config_settings_view.xml',
    ],
    'qweb': [
        'static/src/xml/templates.xml',
        'static/src/xml/dialog.xml',
    ],
    'demo': [
        'demo/payment_acquirer_data.xml',
        # 'demo/demo.xml',
    ],
}
