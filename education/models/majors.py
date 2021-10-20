from odoo import models, fields


class Majors(models.Model):
    _name = 'majors'
    name = fields.Char('Major')
    