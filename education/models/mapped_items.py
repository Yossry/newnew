from odoo import models, fields


class MappedItems(models.Model):
    _name = 'mapped.items'
    _description = 'Mapped Items'
    items = fields.Many2one('event.event')
    product = fields.Many2one('product.template', string="Product")
    taxes = fields.Many2one('account.tax', string="Taxes")
    price = fields.Float('Price', readonly="1")
    price_after_tax = fields.Float('Price After Tax', readonly="1")
    currency = fields.Float('Currency')
