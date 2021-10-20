from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Attendance(models.Model):
    _name = 'attendance'
    registration_id = fields.Many2one('event.registration', 'Registration')
    event_id = fields.Many2one('event.event', 'Event')
    session_id = fields.Many2one('event.track', 'Session')
    partner_id = fields.Many2one('res.partner', 'Contact')
    attended = fields.Boolean('Attended')

    @api.constrains('attended')
    def check_session_date(self):
        if self.attended:
            today = fields.Datetime.now()
            if self.session_id.date > today:
                raise ValidationError("You must wait the session starting day before doing this action.")

    def write(self, vals):
        res = super(Attendance, self).write(vals)
        if self.attended:
            attended = True
            event = self.event_id
            attendances = self.env['attendance'].search([('event_id', '=', event.id), ('id', '!=', self.id)])
            for attendance in attendances:
                if not attendance.attended:
                    attended = False
                    break

            if attended:
                events = self.partner_id.event_ids.ids + event.ids
                self.partner_id.write({'event_ids': [(6, 0, events)]})

        return res
