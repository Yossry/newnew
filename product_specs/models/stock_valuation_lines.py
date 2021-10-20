# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests


class StockValuation(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    currency_id = fields.Many2one('res.currency', related='cost_id.company_id.currency_id')

    def _compute_currency(self):
        for record in self:
            if record.cost_id.vendor_bill_id:
                record['currency_id'] = record.cost_id.vendor_bill_id.currency_id.id
            else:
                record['currency_id'] = record.cost_id.company_id.currency_id.id
