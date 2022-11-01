# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Outside Provider",
    "summary": """
        Outside Provider Profile
        """,
    "author": "Kandooit",
    "website": "",
    "category": "",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "images": [
        # "static/description/Two_factor_authentification.png",
    ],
    "installable": True,
    "depends": [
        "base","opt_custom",'opt_insurance', 'gws_google_maps',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/outside_doctor_view.xml",
        "views/frame_markup_formula.xml",
        "views/dashboard_views.xml",
        "views/hr_employee_view.xml",
        "views/role.xml",
        "views/assets.xml",
        # "views/patients_view.xml",
    ],
    'qweb': [
            "static/src/xml/dashboard.xml",
            "static/src/xml/import_doctor_view.xml",
            ],
}
