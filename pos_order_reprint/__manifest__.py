# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "POS Order Reprint",
  "summary"              :  """The module allows you to reprint the receipt from customer’s previous orders in the POS session.""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-POS-Order-Reprint.html",
  "description"          :  """Odoo POS Order Reprint
POS receipt reprint
Print customer order
POS receipt
POS view orders
View previous orders
View all orders POS""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_order_reprint&custom_url=/pos/auto",
  "depends"              :  ['pos_orders'],
  "data"                 :  [
                             'views/pos_config.xml',
                             'views/template.xml',
                             'reports/order_report.xml',
                             'reports/order_reprint_paperrformat.xml',
                             'reports/report_file.xml',
                            ],
  "qweb"                 :  ['static/src/xml/pos_order_reprint.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  22,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}