from odoo import models, fields, api


class ShippingPrice(models.Model):
    _name = 'shipping.price'
    _description = 'Shipping Price/Product/Company'
    product_id = fields.Many2one('product.template', string='Product', required="1")
    carrier_id = fields.Many2one('delivery.carrier', string='Delivery Carrier')
    company_id = fields.Many2one('res.company', string='Company', required="1")
    price = fields.Float('Price', required="1")