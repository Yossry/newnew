from odoo import models, fields


class Indusry(models.Model):
    _name = 'industry'
    _description = 'Industry'
    name = fields.Char('Industry')
