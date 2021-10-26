# -*- coding:utf-8 -*-
{
    'name': 'Kuwait - Accounting',
    'category': 'Localization',
    'author': "Media Engagers",
    'depends': [ 'base','account','base_iban','base_vat',],
    'description': """
This is the module to manage the accounting chart for Kuwait in Odoo.
======================
    """,

    'website': 'https://www.mediaengagers.com',
    'data': [
	    'data/account_chart_template_data.xml',
        'data/account.account.template.csv',
        'data/l10n_lb_chart_data.xml',
    ],
}
