# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api



class PosReport(models.Model):
	_inherit='report.pos.order'

	product_brand_id = fields.Many2one('product.brand','Brand',readonly=True)
	cost = fields.Float('Product Cost',readonly=True)
	margin_perc = fields.Float('Margin',readonly=True)

	def _group_by(self):
		return super(PosReport, self)._group_by() + ',l.product_brand_id, l.cost'

	def _select(self):
		return super(PosReport, self)._select() + ',l.product_brand_id AS product_brand_id, l.cost as cost, SUM(l.margin_perc / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) AS margin_perc'