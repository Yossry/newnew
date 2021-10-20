from odoo import models, fields


class EventPrice(models.Model):
    _name = 'event.price'
    _description = 'Event Price'
    course_id = fields.Many2one('course', string='Course')
    company_id = fields.Many2one('res.company', string="Region", domain="[('is_region', '=', True)]")
    price = fields.Float(string="Price")
    currency_id = fields.Many2one('res.currency', string='Currency')
    price_in_region = fields.Float(string='Price In Region')
    topic_id = fields.Many2one('course.topic')
