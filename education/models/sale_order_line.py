from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    track_id = fields.Many2one('event.track')
    event_id = fields.Many2one('event.event', string='Event')
    term_id = fields.Many2one('term', string='Term')
    session_id = fields.Many2one('event.track', string='Session')
    course_id = fields.Many2one('course','Course')
    event_track_seats_availability = fields.Selection(
        related='session_id.event_id.state',
        string='Seats Availavility',
        readonly=True
    )
    event_session_seats_availability = fields.Selection(
        related='event_id.state',
        string='Seats Availavility',
        readonly=True,
    )
    event_session_seats_available = fields.Integer(
        related='event_id.seats_available',
        string='Available Seats',
        readonly=True,
    )
    event_sessions_count = fields.Integer(
        comodel_name='event.track',
        related='event_id.track_count',
        readonly=True,
    )
    registration_ids = fields.One2many(
        'event.registration', 
        'sale_order_line_id',
        string='Attendees',
        readonly=True)

    """@api.onchange('track_id', 'session_id')
    def onchange_track_id(self):
        val = {}
        #if not self.order_id._session_seats_available():
        #    raise ValidationError(_(
        #        "Not enough seats. Change quantity or session"))
        if self.session_id:
        	tax_ids = []
        	for tax in self.session_id.tax_ids:
        		tax_ids.append(tax.id)
        	val['value'] = {
        		'name': self.session_id.display_name + '\r' + str(self.session_id.date),
        		'price_unit': self.session_id.price,
        		'tax_id': [(6, 0, tax_ids)]
        	}
        return val
            
    
            
    @api.onchange()
    def product_uom_change(self):
        if not self.order_id._track_seats_available():
            raise ValidationError(
                _("Not enough seats. Change quantity or session"))
            return super().product_uom_change()

    @api.onchange('event_id')
    def _onchange_event_id(self):
        if self.event_sessions_count == 1:
            self.track_id = self.event_id.track_ids[0]
            return super()._onchange_event_id()
            
            def get_sale_order_line_multiline_description_sale(self, product):
                name = super().get_sale_order_line_multiline_description_sale(product)
                if self.event_ticket_id and self.track_id:
                    name += '\n' + self.track_id.display_name
                    return name




    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: r.company_id == line.order_id.company_id)
            #raise ValidationError(taxes)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes

    def _get_display_price(self, product):
        if self.event_ticket_id and self.event_id:
            return self.order_id.pricelist_id._compute_price_event(self.event_id, self.event_ticket_id, self.order_id.currency_id)
        else:
            return super()._get_display_price(product)

    def _prepare_invoice_line(self):

        self.ensure_one()
        return {
        'display_type': self.display_type,
        'sequence': self.sequence,
        'name': self.name,
        'product_id': self.product_id.id,
        'product_uom_id': self.product_uom.id,
        'quantity': self.qty_to_invoice,
        'discount': self.discount,
        'price_unit': self.price_unit,
        'tax_ids': [(6, 0, self.tax_id.ids)],
        'analytic_account_id': self.order_id.analytic_account_id.id,
        'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        'sale_line_ids': [(4, self.id)],
        'company_id': self.company_id.id,
        'term_id': self.term_id.id if self.term_id else False,
        }

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        return True"""

