# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Jsobon",
    'version': '1.0',
    'summary': "Evaluacion tecnica Calyx Jsobron",
    'description': "Evaluacion tecnica Calyx Jsobron",
    'category': 'Admin',
    'depends': ['sales_team', 'payment', 'portal', 'utm'],
    'data': [
        'views/test.xml',   
    ],
    'demo':[],

    'installable': True,
    'auto_install': True,
    'application': True,
    'license': 'LGPL-3',
}
