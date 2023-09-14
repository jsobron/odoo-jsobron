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
        #'views/credit_report_template.xml',  
        #'views/report_credit_report.xml',  
    ],
    'demo':[],

    'installable': True,
    'auto_install': True,
    'application': True,
    'license': 'LGPL-3',
}
