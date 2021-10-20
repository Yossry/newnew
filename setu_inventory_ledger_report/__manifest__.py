# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Inventory Ledger Report',
    'version': '13.0',
    'price': 149,
    'currency': 'EUR',
    'category': 'stock',
    'summary': """	
        Inventory Ledger Report / Stock Card
        - Date wise real time inventory calculation along with opening & closing. Stock ledger report helps user to get summary as well as detailed of each days inventory movemenents. 
          stock movement report, stock rotation report.
        - Detailed and Summary report available
        - Date wise calculated opening stock and closing stock
        - Date wise detailed data for each movement
        - Capture  all possible inventory movements and separately visible all IN transactions and OUT transactions in report. (Date wise / Summary)
		""",
    'website': 'https://www.setuconsulting.com',
    'support': 'support@setuconsulting.com',
    'description': """
        Inventory Ledger Report
        It’s necessary to know inventory movements each day with all possible movements for each product for each warehouse or company and it’s very difficult to manage.
        So we introduced a solution for that and built an Inventory Ledger Report where users can track each day's transactions or summary of all dates together with real calculated opening and closing. 
        This app helps you to track the inventory for specific periods or up to a certain date.
    """,
    'author': 'Setu Consulting',
    'license': 'OPL-1',
    'sequence': 25,
    'depends': ['stock','base'],
    'images': ['static/description/banner.gif'],
    'data': [
        'views/setu_inventory_ledger_report.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    'live_test_url': 'http://95.111.225.133:5929/web/login',
    'pre_init_hook': 'pre_init',
}
