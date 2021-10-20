from odoo import models, fields

class irSequence(models.Model):
	_inherit = 'ir.sequence'
	number = fields.Integer('Number',default=1)