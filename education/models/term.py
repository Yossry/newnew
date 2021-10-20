from odoo import models, fields


class Term(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin']
    _name = 'term'
    _description = 'Term'
    name = fields.Char('Targeted Term', translate=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')