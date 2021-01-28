# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Accountant',
    'version': '1.0',
    'category': '',
    'depends': ['purchase','sale','purchase_requisition'],
    'data': [
        'security/accountant_security.xml',
        'security/ir.model.access.csv',
        'views/accountant_views.xml',
    ],
}
