from odoo import models, fields


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    session_id = fields.Many2one('event.track')