# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'



    @api.depends('date_order')
    def _compute_order_date(self):
        for rec in self:
            from_date = fields.Datetime.from_string(rec.date_order)
            order_date = from_date.strftime('%Y-%m-%d')
            order_time = from_date.strftime("%H:%M:%S")
            rec.order_new_date = order_date
            rec.order_new_time = order_time
            rec.day = from_date.strftime("%A")
            rec.hour = from_date.strftime("%H")

    amount_disocunt = fields.Monetary(string='Amount Discount', store=True, readonly=True, compute='_amount_all')
    all_amount = fields.Monetary(string='Total Sales', store=True, readonly=True)
    cost = fields.Monetary(string='Cost', store=True, readonly=True)
    order_new_date = fields.Date(compute='_compute_order_date', string='Order Date')
    order_new_time = fields.Char(compute='_compute_order_date', string='Time')
    hour = fields.Char(compute='_compute_order_date', string='Hour', store=True)
    day = fields.Char(compute='_compute_order_date', string='Day', store=True)
    mobile = fields.Char(related='partner_id.phone', store=True, string='Mobile')
    margin_perc = fields.Float(compute='_product_margin_perc', string='Margin (%)')

    def _product_margin_perc(self):
        for order in self:
            margin_perc = 0.0
            currency = order.pricelist_id.currency_id
            all_margin = currency.round(sum(line.margin for line in order.order_line))
            all_purchase = currency.round(sum((line.purchase_price * line.product_uom_qty) for line in order.order_line))
            if all_purchase > 0.0:
                margin_perc = (all_margin / all_purchase) * 100.0
            order.margin_perc = margin_perc


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_type = fields.Selection(related='product_id.type', store=True)
    default_code = fields.Char(related='product_id.default_code', store=True)
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', string="Category", store=True)
    pos_categ_id = fields.Many2one('pos.category', related='product_id.pos_categ_id', string="Point Of Sale Category", store=True)
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Customer', store=True)
    barcode = fields.Char(related='product_id.barcode')
    cost = fields.Float('Cost')
    mobile = fields.Char(related='order_id.partner_id.mobile', string='Mobile', store=True)
    hour = fields.Char(related='order_id.hour', string='Hour', store=True)
    day = fields.Char(related='order_id.day', store=True)
    lst_price = fields.Float(related='product_id.lst_price', store=True)
    order_new_date = fields.Date(related='order_id.order_new_date', string='Order Date', store=True)
    order_new_time = fields.Char(related='order_id.order_new_time', string='Time', store=True)
    invoice_ids = fields.Many2many(related='order_id.invoice_ids', relation='account.invoice')
    margin_perc = fields.Float(compute='_product_margin_perc', string='Margin (%)')
    product_brand_id = fields.Many2one('product.brand', related='product_id.product_brand_id', store=True, string='Brand')
    location_id = fields.Many2one('stock.location',compute="_compute_location",store=True)
    product_name = fields.Char(related='product_id.name',store=True)
    qty_available = fields.Float(string='Qty Available',related='product_id.product_tmpl_id.qty_available',store=True)

    def _product_margin_perc(self):
        for line in self:
            to_cur = line.order_id.pricelist_id.currency_id
            margin_perc = 0.0
            if line.cost > 0.0 and line.product_uom_qty > 0.0:
                margin_perc = to_cur.round((line.margin / (line.cost * line.product_uom_qty)) * 100.0)
            line.margin_perc = margin_perc

    def _compute_location(self):
        for record in self:
            record['location_id'] = False
            stock_move = self.env['stock.move'].search([('sale_line_id','=',record.id)],limit=1)
            if stock_move:
                record['location_id'] = stock_move.location_id.id

            else:
                stock_picking = self.env['stock.picking'].search([('origin','=',record.order_id.name)],limit=1)
                record['location_id'] = stock_picking.location_id.id

    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['cost'] = product.standard_price
        return super(SaleOrderLine, self).create(vals)
