from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError

class EventTicket(models.Model):
    _inherit = "event.event.ticket"
    mapped_item_ids = fields.Many2many('product.template', string="Mapped Items")
    tax_ids = fields.Many2many('account.tax', string="Taxes")
    amount_taxed = fields.Float('Amount Taxed', compute='_compute_amount_taxed')
    currency_id = fields.Many2one(related='event_id.company_id.currency_id')
    
    def _compute_amount_taxed(self):
        for ticket in self:
            if(ticket.tax_ids):
                ticket.amount_taxed = ticket.tax_ids.compute_all(ticket.price)['total_included']
            else:
                ticket.amount_taxed = ticket.price