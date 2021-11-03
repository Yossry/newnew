# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api



class SaleReport(models.Model):
    _inherit='sale.report'
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['product_brand_id'] = ", l.product_brand_id AS product_brand_id"
        groupby += ', l.product_brand_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)