from odoo import  fields, models, _
from odoo.exceptions import UserError


class SaleForcast(models.Model):
    _name = 'event.sale.forecast'
    event_id = fields.Many2one('event.event','Event')
    partner_id = fields.Many2one('res.partner','Account')
    probability = fields.Float('Probability')
    price_unit = fields.Float('Price Unit')
    amount = fields.Float('Projected Sales')
