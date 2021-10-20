from odoo import models, fields

class Exam(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin']
    _name = 'exam'
    _description = 'Exam'
    name = fields.Char('Name', translate=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')