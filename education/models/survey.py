from odoo import models, fields


class Survey(models.Model):
    _inherit = "survey.survey"
    survey_type = fields.Selection(
        [
            ('marketing', 'Marketing'),
            ('instructor', 'Instructor Review'),
            ('exam', 'Exam'),
            ('event', 'Event Review'),
            ('end', 'End Of Event Review')
        ],
        string='Survey Type')
    instructor_id = fields.Many2one(
        'hr.employee',
        string="Instructor",
        domain="[('is_instructor', '=', True)]"
    )
    event_id = fields.Many2one('event.event', string="Event")
    session_id = fields.Many2one('event.track', string="Session")
    survey_id = fields.Many2one('res.partner')
    title = fields.Char('Title')
    survey_id = fields.Many2one('event.event')
