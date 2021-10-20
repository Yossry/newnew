from odoo import models, fields


class EventPeriod(models.Model):
    _name = 'event.period'
    _description = 'Period'
    name = fields.Char('Name', translate=True)
