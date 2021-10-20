from odoo import models, fields


class Certificate(models.Model):
    _name = 'certificate'
    _description = 'Certificate'
    student_id = fields.Many2one('res.partner', string="Student")
    event_id = fields.Many2one('event.event', string="Event")
    registration_id = fields.Many2one('event.registration', string="Registration")
    company_id = fields.Many2one('res.company', string="Company")