# -*- coding: utf-8 -*-
{
    'name': "opt_reports",
    'summary': """ """,
    'description': """
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'general_template', 'stock_account', 'stock', 'hr_attendance', 'ivis_order_grouping',
                'post_sale_transactions', 'ivis_order_grouping', 'promotion_program'],
    'data': [
        'security/ir.model.access.csv',

        'report/report_action/custom.xml',
        'report/report_action/appointment_report_action.xml',
        'report/report_action/sales_invoices_report_action.xml',

        'wizard/appointment_schedule_report.xml',
        'report/appointment_schedule_report.xml',

        'wizard/appointment_services_count.xml',
        'report/appointment_services_count.xml',

        'data/appointment_details_report.xml',
        'wizard/appointment_details_report.xml',
        'report/appointment_details_report.xml',

        'wizard/payment_transactions.xml',
        'report/payment_transactions.xml',

        'wizard/post_sale_transactions_report.xml',
        'report/post_sale_transactions_report.xml',

        'wizard/aged_receivables.xml',
        'report/aged_receivables.xml',

        'wizard/payment_summary.xml',
        'report/payment_summary.xml',

        'wizard/product_sales.xml',
        'report/product_sales.xml',

        'wizard/sales_session_report.xml',
        'report/sales_session_report.xml',

        'wizard/daily_sales.xml',
        'report/daily_sales.xml',

        'wizard/promotions.xml',
        'report/promotions.xml',

        'wizard/sales_order_discounts.xml',
        'report/sales_order_discounts.xml',

        'wizard/physician_production.xml',
        'report/physician_production.xml',

        'views/hr_attendance.xml',
        'views/menu_items.xml',
    ],
}
