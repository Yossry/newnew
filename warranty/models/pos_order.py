# -*- coding: utf-8 -*-

import datetime
from dateutil import parser
from odoo import models, fields, api
import json
import requests
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        for order in self:
            for line in order.lines:
                if (line.line_warranty):
                    product_warranty = self.env['product.warranty'].search(
                        [('partner_id', '=', order.partner_id.id), ('product_id', '=', line.product_id.id)])
                    if (not product_warranty):
                        product_warranty = self.env['product.warranty'].create({
                            'partner_id': order.partner_id.id,
                            'product_id': line.product_id.id,
                            'name': order.name,
                            'start_date': order.date_order,
                            'warranty_type_id': line.line_warranty.id,
                        })
                    else:
                        product_warranty.write({
                            'partner_id': order.partner_id.id,
                            'product_id': line.product_id.id,
                            'name': order.name,
                            'start_date': order.date_order,
                            'warranty_type_id': line.line_warranty.id,
                        })
                    product_warranty._compute_expiry_date()

                    lot_id = self.env['pos.pack.operation.lot'].search([('pos_order_line_id', '=', line.id)], limit=1)
                    if (lot_id):
                        product_warranty.write({'lot_id': lot_id.id})
        return res
