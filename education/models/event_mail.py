from odoo import models, fields


class EventMail(models.Model):
    _inherit = 'event.mail'
    course_id = fields.Many2one('course')

    