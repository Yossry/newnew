from odoo import api, fields, models

class FactorDecision(models.Model):
    _name = 'factor.decision'
    name = fields.Char('Name', required="1")