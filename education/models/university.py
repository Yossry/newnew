
from odoo import models, fields


class University(models.Model):
    _name = 'university'
    name = fields.Char('University')