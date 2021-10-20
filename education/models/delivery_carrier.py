from odoo import models, fields, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    product_ids = fields.One2many('shipping.price', 'carrier_id', string="Products")
    delivery_type = fields.Selection(selection_add=[('products', 'Based on Products')], ondelete={'products': 'set default'})

    def products_rate_shipment(self, order):
        carrier = self._match_address(order.partner_shipping_id)
        res = {}
        if not carrier:
            return {'success': False,
                    'price': 0.0,
                    'error_message': _('Error: this delivery method is not available for this address.'),
                    'warning_message': False}
        total_price = 0
        for line in order.order_line:
            shipping_cost = self.env['shipping.price'].search([
                ('product_id', '=', line.product_id.product_tmpl_id.id),
                ('company_id', '=', order.company_id.id),
                ('carrier_id', '=', self.id)])
            if (shipping_cost):
                total_price += shipping_cost.price * line.product_uom_qty
        res['price'] = total_price
        if total_price:
            return {
                'success': True,
                'price': total_price,
                'error_message': False,
                'warning_message': False
            }
        res['carrier_price'] = res['price']
        if total_price == 0:
            res['warning_message'] = _('The shipping is free since none of the items is mapped to a shipping')
            res['price'] = 0.0

        if res['success'] and self.free_over and order._compute_amount_total_without_delivery() >= self.amount:
            res['warning_message'] = _('The shipping is free since the order amount exceeds %.2f.') % (self.amount)
            res['price'] = 0.0
        return res
