# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Optical ERP",
    "category": "",
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "version": "1.0",
    "description": """
        Optical ERP module useful to manage:

        1. Frame segment
        2. Lens segment
""",
    'website': 'https://serpentcs.com',
    'depends': ['base','mail','account','contacts', 'website_sale', 'stock', 'auth_oauth',
                'auth_signup', 'hr', 'calendar', 'base_setup',
                'account', 'base_geolocalize', 'web_widget_multi_image',
                'gws_google_maps', 'delivery', 'purchase', 'sale_coupon',
                'purchase_requisition','ks_multi_company_inventory_transfer',
                'web_one2many_kanban',
                'uom'],
    'data': [
        'views/spec_rx_usage.xml',
        'views/rx_discontinue_reason.xml',
        'views/configurations_menuitem.xml',

        'security/optical_security.xml',
         'security/ir.model.access.csv',
         'data/spec.shape.shape.csv',
         'data/spec.frame.material.csv',
         'data/sequence.xml',
         'data/activities.xml',
         'data/gender.xml',
         'data/region.xml',
         'data/contact_lens_manufacturer.xml',
         'data/referred_by.xml',
         'data/rx_usage.xml',
         'data/product_attribute.xml',
         'data/product_category.xml',
         'data/frame_data.xml',
         'data/spec_contact_lens_replacement_schedule.xml',

         'wizard/accessory_change_cost_price_view.xml',
         'views/frame_view.xml',
         'views/partner_view.xml',
         'views/patients_view.xml',
         'views/uom_uom.xml',
         'views/appointment_view.xml',
         # 'views/signup_extend_templates.xml',
         'views/lens_view.xml',
         'views/contact_lens_view.xml',
         'views/accessory_view.xml',
         'views/service_view.xml',
         'views/company_view.xml',
         'views/assets.xml',
         # 'views/calendar_views.xml',
        #  'views/patient_appointment_view.xml',
         'views/lens_treatments_view.xml',
         'views/lens_parameters_view.xml',
         'views/product_receipts_view.xml',
        #  'report/report_cms_1500_form_template.xml',
         'report/report_view.xml',
         # 'views/edit_claim_view.xml',
         'wizard/update_email_patient_view.xml',
         'views/sale_coupon_rules.xml',
        #  'report/report_appointment_view.xml',
         'views/inventory_operations_views.xml',
         'views/patients_own_frame.xml',
         'views/sequence.xml',
         'views/integrated_partner_view.xml',
         'views/inventory_scrap.xml',
         'views/spec_contact_lens.xml',
         'views/stock_quant.xml',
         'views/stock.xml',
         'views/purchase_order.xml',

         'views/menu_items.xml',
    ],
    "demo": [],
    "qweb": [
        # "static/src/xml/company_dropdown.xml",
        "static/src/xml/calender_view.xml",
        "static/src/xml/attachment_preview.xml",
    ],
    "auto_install": False,
    "installable": True,
}
