# -*- coding: utf-8 -*-

from odoo import api, fields, models
import pytz
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.depends('payment_ids', 'lines.price_subtotal_incl', 'lines.discount')
    def _compute_amount_all(self):
        for order in self:
            amount_tax = total_discount = cost = 0.0
            currency = order.pricelist_id.currency_id
            amount_paid = sum(payment.amount for payment in order.payment_ids)
            # amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.statement_ids)
            amount_tax = currency.round(sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            amount_total = amount_tax + amount_untaxed
            for line in order.lines:
                total_discount += (line.qty * line.price_unit) * (line.discount / 100)
                cost += (line.qty * line.cost)
            amount_net = (amount_total - total_discount)
            order.update({
                'amount_paid': amount_paid,
                # 'amount_return': amount_return,
                'amount_tax': amount_tax,
                'amount_total': amount_total,
                'total_discount': total_discount,
                'amount_net': amount_net,
                'cost': cost,
            })

    def convert_timezone(self, from_tz, to_tz, date):
        from_tz = pytz.timezone(from_tz).localize(datetime.strptime(str(date), DATETIME_FORMAT))
        to_tz = from_tz.astimezone(pytz.timezone(to_tz))
        return to_tz.strftime(DATETIME_FORMAT)

    @api.depends('date_order')
    def _compute_order_date(self):
        for rec in self:
            order_date = self.convert_timezone('UTC', self.env.user.tz or 'UTC', rec.date_order)
            from_date = fields.Datetime.from_string(order_date)
            order_date = from_date.strftime('%Y-%m-%d')
            order_time = from_date.strftime("%H:%M:%S")
            rec.order_new_date = order_date
            rec.order_new_time = order_time
            rec.day = from_date.strftime("%A")
            rec.hour = from_date.strftime("%H")

    #analytic_account_id = fields.Many2one('account.analytic.account', related='session_id.config_id.account_analytic_id', string='Analytic Account', store=True)
    total_discount = fields.Float(compute='_compute_amount_all', string='Discount', store=True)
    order_new_date = fields.Date(compute='_compute_order_date', string='Order Date')
    order_new_time = fields.Char(compute='_compute_order_date', string='Time')
    hour = fields.Char(compute='_compute_order_date', string='Hour', store=True)
    day = fields.Char(compute='_compute_order_date', string='Day', store=True)
    amount_tax = fields.Float(compute='_compute_amount_all', string='Taxes', digits=0, store=True)
    amount_total = fields.Float(compute='_compute_amount_all', string='Total', digits=0, store=True)
    amount_net = fields.Float(compute='_compute_amount_all', string="Net Sales", digits=0, store=True)
    total_net = fields.Float(compute='_compute_amount_all', string="Net Sales111", digits=0, store=True)
    amount_paid = fields.Float(compute='_compute_amount_all', string='Paid', states={'draft': [('readonly', False)]}, readonly=True, digits=0, store=True)
    amount_return = fields.Float(compute='_compute_amount_all', string='Returned', digits=0, store=True)
    cost = fields.Float(compute='_compute_amount_all', string="Total Cost", digits=0, store=True)
    config_id = fields.Many2one('pos.config', related='session_id.config_id', store=True)
    driver_partner_id = fields.Many2one('res.partner')
    mobile = fields.Char(related='partner_id.phone', store=True, string='Mobile')
    margin_perc = fields.Float(compute='_product_margin_perc', string='Margin (%)')

    def _product_margin_perc(self):
        for order in self:
            margin_perc = 0.0
            all_margin = sum(line.margin_perc for line in order.lines)
            all_purchase = sum((line.cost * line.qty) for line in order.lines)
            if all_purchase > 0.0:
                margin_perc = (all_margin / all_purchase) * 100.0
            order.margin_perc = margin_perc


class account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'

    config_id = fields.Many2one('pos.config', related='pos_statement_id.config_id', store=True)
    #analytic_account_id = fields.Many2one('account.analytic.account', related='pos_statement_id.analytic_account_id', store=True)


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    product_type = fields.Selection(related='product_id.type', store=True)
    default_code = fields.Char(related='product_id.default_code', store=True)
    barcode = fields.Char(related='product_id.barcode')
    product_brand_id = fields.Many2one('product.brand', related='product_id.product_brand_id', string='Brand', store=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string="Category", store=True)
    pos_categ_id = fields.Many2one('pos.category', related='product_id.pos_categ_id', string="Point Of Sale Category", store=True)
    cost = fields.Float('Product Cost')
    standard_price = fields.Float(related='product_id.standard_price', store=True)
    lst_price = fields.Float(related='product_id.lst_price', store=True)
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', store=True)
    day = fields.Char(related='order_id.day', store=True)
    order_new_date = fields.Date(related='order_id.order_new_date', string='Order Date', store=True)
    order_new_time = fields.Char(related='order_id.order_new_time', string='Time', store=True)
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Customer', store=True)
    mobile = fields.Char(related='order_id.partner_id.mobile', string='Mobile', store=True)
    pos_categ_id = fields.Many2one('pos.category', related='product_id.pos_categ_id', store=True)
    hour = fields.Char(related='order_id.hour', string='Hour', store=True)
    config_id = fields.Many2one('pos.config', related="order_id.session_id.config_id", string="Point Of Sale", store=True)
    margin_perc = fields.Float(compute='_compute_margin_perc', string='Margin(%)',store=True)
    quantity_on_hand = fields.Float('Qty On Hand')

    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['cost'] = product.standard_price
        return super(PosOrderLine, self).create(vals)

    def _compute_margin_perc(self):
        for line in self:
            line.margin_perc = line.price_subtotal - (line.cost * line.qty)
