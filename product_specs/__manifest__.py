# -*- coding: utf-8 -*-
{
    'name': "Product Specs",

    'summary': """
    Add Specs For Each Product""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Media Engagers",
    'website': "http://www.mediaengagers.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','stock_landed_costs'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}