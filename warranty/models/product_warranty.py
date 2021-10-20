# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests
from odoo.exceptions import UserError


class ProductWarranty(models.Model):
    _name = 'product.warranty'

    name = fields.Char(string='Ref')
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    start_date = fields.Date(string='Start Date')
    expiry_date = fields.Date(string='Expiry Date', compute='_compute_expiry_date', store=True)
    lot_id = fields.Many2one('pos.pack.operation.lot', string='Lot')
    warranty_type_id = fields.Many2one('product.warranty.type', string='Warranty Type')

    @api.depends('warranty_type_id', 'start_date')
    def _compute_expiry_date(self):
        for record in self:
            if (record.warranty_type_id):
                vals = {}
                days = record.warranty_type_id.number_of_days
                date = datetime.datetime.strptime(str(record.start_date), '%Y-%m-%d')
                days = datetime.timedelta(days=days)
                expiry_date = (date + days).date()
                vals['expiry_date'] = str(expiry_date)
                self.update(vals)
