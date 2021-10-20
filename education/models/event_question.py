from odoo import models, fields, api
import datetime

class EventQuestion(models.Model):
    _inherit = "event.question"
    course_id = fields.Many2one('course', string="Course")