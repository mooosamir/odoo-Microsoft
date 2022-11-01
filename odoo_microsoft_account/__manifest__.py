# See LICENSE file for full copyright and licensing details.
{
    'name': 'Microsoft Azure - Odoo SSO Integration',
    'version': '13.0',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.com',
    'depends': ['auth_oauth'],
    'data': [
        'views/res_config.xml',
        'views/oauth_provider.xml',
        'data/auth_oauth_data.xml',
    ],
    'images': ['static/description/microsoft_azure.png'],
    'external_dependencies': {'python': ['simplejson']},
    'installable': True,
    'auto_install': False,
    'price': 129,
    'currency': 'EUR'
}
