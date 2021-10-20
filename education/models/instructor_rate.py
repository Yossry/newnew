
from odoo import models, fields


class InstructorRate(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin']
    _name = 'instructor.rate'
    _description = 'Instructor Rate'
    name = fields.Char(string='Name', track_visibility='onchange')
    instructor_id = fields.Many2one('hr.employee', string='Instructor')
    course_id = fields.Many2one('course', string='Course')
    rate = fields.Float(string='Rate')
    company_id = fields.Many2one('res.company', domain="[('is_region', '=', True)]")
    currency_id = fields.Many2one('res.currency', string='Currency')
    rate_id = fields.Many2one('res.partner') 
    local_rate = fields.Float('Local Rate')
