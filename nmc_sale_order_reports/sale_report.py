# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api



class SaleReport(models.Model):
	_inherit='sale.report'

	product_brand_id = fields.Many2one('product.brand','Brand',readonly=True)
	cost = fields.Float('Product Cost',readonly=True)
	location_id = fields.Many2one('stock.location','Location',readonly=True)
	product_name = fields.Char('Product Name',readonly=True)
	qty_available = fields.Float(string='Qty Available',readonly=True)
	total_cost = fields.Float(string='Total Cost',readonly=True)

	def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
		fields['product_brand_id'] = ', l.product_brand_id as product_brand_id'
		fields['cost'] = ', l.cost as cost'
		fields['location_id'] = ', l.location_id as location_id'
		fields['product_name'] = ', l.product_name as product_name'
		fields['qty_available'] = ', l.qty_available as qty_available'
		fields['total_cost'] = ", SUM(l.cost * l.product_uom_qty / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS total_cost"

		groupby += ', l.product_brand_id, l.cost, l.location_id, l.product_name, l.qty_available'

		return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)