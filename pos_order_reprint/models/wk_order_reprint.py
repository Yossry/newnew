# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def get_report_data(self, kwargs):
        order = self.browse(kwargs['order_id'])
        account_tax_obj = self.env['account.tax']
        orderlines, paymentlines, tax_details = [], [], []
        change = amount_untaxed = total_discount = 0.0
        if order.lines:
            val2 = 0.0
            selected_tax = []
            cur = order.pricelist_id.currency_id
            for line in order.lines:
                val2 += line.price_subtotal
                order_line = {
                    'discount': line.discount,
                    'price': line.price_unit,
                    'price_display': line.price_subtotal,
                    'price_with_tax': line.price_subtotal_incl,
                    'price_without_tax': line.price_subtotal,
                    'product_name_wrapped': line.product_id.name,
                    'quantity': line.qty,
                    'tax': self._amount_line_tax(line, order.fiscal_position_id),
                    'unit_name': line.product_id.uom_id.name,
                }
                if line.tax_ids:
                    for tax in line.tax_ids:
                        if tax.id not in selected_tax:
                            amount = 0.0
                            selected_tax.append(tax.id)
                            for l in order.lines:
                                if l.tax_ids:
                                    temp_ids = [x.id for x in l.tax_ids]
                                    if tax.id in temp_ids:
                                        price = l.price_unit * (1 - (l.discount or 0.0) / 100.0)

                                        temp = account_tax_obj.browse([tax.id]).compute_all(price, cur, l.qty, product=l.product_id, partner=l.order_id.partner_id or False)

                                        amount += float(temp['total_included'] - temp['total_excluded'])
                            tax_details.append({ 'name': tax.name, 'amount': amount })
                if line.discount > 0.0:
                    total_discount += float(line.discount * line.price_unit) / 100.0
                orderlines.append(order_line)
            amount_untaxed = val2
        if order.payment_ids and order.payment_ids.payment_method_id:
            for stmt in order.payment_ids:
                _logger.info("-------------stmt-----------:%r",stmt)
                _logger.info("-------------stmt.payment_method_id-----------:%r",stmt.payment_method_id)
                if stmt.amount >= 0.0:
                    currency = stmt.currency_id or stmt.company_id.currency_id
                    name = "%s (%s)" % (stmt.payment_method_id.name, currency.name)
                    payment_line = {
                        'amount': stmt.amount,
                        'name': name
                    }
                    paymentlines.append(payment_line)
                else:
                    change = stmt.amount
        return {
            'paymentlines': paymentlines,
            'receipt': {
                'cashier': order.user_id.name,
                'change': change,
                'client': order.partner_id and order.partner_id.name or False,
                'date': order.date_order,
                'orderlines': orderlines,
                'paymentlines': paymentlines,
                'subtotal': amount_untaxed,
                'tax_details': tax_details,
                'total_discount': total_discount,
                'total_tax': order.amount_tax,
                'total_with_tax': order.amount_total,
                'pos_ref': order.pos_reference,
            },
            'taxincluded': False,
        }
   
    @api.model
    def order_formatLang(self,value,currency_obj=False):
        res = value
        if currency_obj and currency_obj.symbol:
            if currency_obj.position == 'after':
                res = u'%s\N{NO-BREAK SPACE}%s' % (res, currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res = u'%s\N{NO-BREAK SPACE}%s' % (currency_obj.symbol, res)
        return res



class PosConfig(models.Model):
    _inherit = 'pos.config'

    wk_reprint_type = fields.Selection([('posbox', 'POSBOX(Xml Report)'),
                                        ('ticket', 'Pos Ticket (Order Receipt)'),
                                        ('pdf','Browser Based (Pdf Report)')
                                        ], default='ticket', required=True, string='Order Reprint Type')

    # @api.one
    @api.constrains('wk_reprint_type','iface_print_via_proxy')
    def check_wk_reprint_type(self):
        if (self.wk_reprint_type == 'posbox'):
            if(self.iface_print_via_proxy == False):
                raise ValidationError("You can not print Xml Report unless you configure the Receipt Printer settings under Hardware Proxy/PosBox!!!")
