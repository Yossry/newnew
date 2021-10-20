from odoo import models, fields


class Universities(models.Model):
    _name = 'university'
    name = fields.Char('University or institute')