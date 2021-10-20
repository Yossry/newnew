from odoo import api, fields, models


class ProductPriceListItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_template_id = fields.Many2one('product.template', 'Product')
    is_region = fields.Boolean(related='pricelist_id.company_id.is_region')
    local_price = fields.Float('Price in region')
    event_id = fields.Many2one('event.event', 'Event')
    applied_on = fields.Selection(selection_add=[('4_event', "Event")], ondelete={'4_event': 'set default'})

    def _get_pricelist_item_name_price(self):
        res = super(ProductPriceListItem, self)._get_pricelist_item_name_price()
        for item in self:
            if item.event_id and item.applied_on == '4_event':
                item.name = item.event_id.name

        return res
