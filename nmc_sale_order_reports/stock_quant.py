# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('quantity')
    def check_quantity(self):
        for quant in self:
            if float_compare(quant.quantity, 1, precision_rounding=quant.product_uom_id.rounding) > 0 and quant.lot_id and quant.product_id.tracking == 'serial':
                print('')
