# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Ventor Two Factor Authentication",
    "summary": """
        2FA implemented via Google Authenticator. Logging into the system requires
         additional key generated on your mobile device.
        """,
    "author": "VentorTech",
    "website": "https://ventor.tech",
    "category": "Uncategorized",
    "license": "LGPL-3",
    "version": "13.0.1.0.0",
    "images": [
        "static/description/Two_factor_authentification.png",
    ],
    "installable": True,
    "depends": [
        "web", "opt_custom"
    ],
    "data": [
        #"data/demo_data.xml",
        "security/two_factor_otp_auth.xml",
        "views/res_config_settings_views.xml",
        "data/email_template.xml",
        "data/ir_actions_server_data.xml",
        "views/res_users_view.xml",
        "templates/assets.xml",
        "templates/verify_code_template.xml",
        "templates/scan_code_template.xml",
    ],
    "external_dependencies": {
        "python": [
            "pyotp", 'twilio'
        ],
    },
}
