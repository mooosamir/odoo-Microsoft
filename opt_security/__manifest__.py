# -*- coding: utf-8 -*-
{
    'name': "Security",
    'summary': """
        Groups, access rights & record rules for entire optical
    """,
    'description': """
        Groups, access rights & record rules for entire optical
    """,
    'author': "Zain Irfan",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'opt_custom', 'web_widget_multi_image', 'opt_appointment', 'sale',
                'patient_engagement', 'stock', 'purchase', 'taxes','acs_consent_form', 'scs_rma', 'promotion_program',
                'post_sale_transactions', 'patient_form_line', 'opt_diagnosis', 'outside_doctor',
                'company_registration', 'calendar', 'hr', 'hr_expense',
                'hr_holidays', 'mass_mailing','account', 'website', 'contacts'
                ],
    'data': [
        'data/res_groups_patients.xml',
        'data/res_groups_appointments.xml',
        'data/res_groups_orders.xml',
        'data/res_groups_invoice.xml',
        'data/res_groups_product.xml',
        'data/res_groups_inventory.xml',
        'data/res_groups_patient_engagement.xml',
        'data/res_groups_attendance.xml',
        'data/res_groups_claims.xml',
        # 'data/res_groups_configurations.xml',

        'views/hide_menuitems.xml',
        'views/assets.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/patient_engagement.xml',
        'views/hr_attendance.xml',
        # 'views/opt_configurations.xml',
        'views/stock_picking.xml',
        'views/opt_inventory.xml',
        'views/purchase_order.xml',
        # 'views/opt_insurance.xml',

        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
