# -*- coding: utf-8 -*-

{
    'name': 'NMC Sale Order Reports',
    'version': '1.0',
    'Author': 'Sismatix Co.',
    'website': 'http://sismatix.com/',
    'description': '''
    ''',
    'depends': ['point_of_sale','product_brand','sale_enterprise','stock'],
    'data': [
        'views/pos_extra_custom_view.xml',
        'views/sale_order_view.xml',
        'views/pos_order_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
