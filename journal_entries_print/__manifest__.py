# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################


{
    'name': 'Journal Entries Print',
    'version': '14',
    'category': 'account',
    'sequence': 9,
    'summary': 'Journal Entries Print',
    'description': """
    this module use for print journal Entries in PDF report"
    """,
    'author': "Laxicon Solution",
    'website': "http://laxicon.in",
    'depends': ['account','account_reports'],
    'license': 'AGPL-3',
    'data': [
            'report/report_menu.xml'
            ],

    'demo': [],
    "images": [
        'static/description/icon.png'
    ],
    'price': 00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
}
