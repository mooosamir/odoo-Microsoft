{
    'name': "IVIS Integration",
    'description': "Module for RES Integration",
    'version': '1.0',
    'author': 'IVIS',
    'depends': ["base", "opt_custom"],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/res_integration.xml',
        'data/data.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
