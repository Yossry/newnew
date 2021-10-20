from odoo import  fields, models,api, _
from odoo.exceptions import UserError


class EventRegistration(models.Model):
    _inherit = 'event.registration'
    attempt_ids = fields.One2many('attempt','registration_id',string="Attempts")
    session_id = fields.Many2one('event.track', string='Session', required=False)
    attempt_date = fields.Date('Attempt Date')
    passing_status = fields.Selection(
        [
        ('passed', 'Passed'),
        ('failed', 'Failed')
        ],
        string='Passing Status')
    score = fields.Float('Score')
    event_id = fields.Many2one(track_visibility='onchange',required=False)


    
    def write(self, vals):
        res = super(EventRegistration, self).write(vals)

        if self.state == 'open':
            if self.event_id and not self.session_id:
                for session in self.event_id.track_ids:
                    attendance = self.env['attendance'].sudo().search([('registration_id','=',self.id),('session_id','=',session.id),('event_id','=',self.event_id.id),('partner_id','=',self.partner_id.id)])
                    if not attendance:
                        attendance = self.sudo().env['attendance'].create({
                            'registration_id': self.id,
                            'event_id': self.event_id.id,
                            'session_id': session.id,
                            'partner_id': self.partner_id.id
                            })

            elif self.session_id:
                attendance = self.env['attendance'].sudo().search([('registration_id','=',self.id),('session_id','=',session.id),('partner_id','=',self.partner_id.id)])
                if not attendance:
                    attendance = self.env['attendance'].sudo().create({
                        'registration_id': self.id,
                        'session_id': self.session_id.id,
                        'partner_id': self.partner_id.id
                        })


        elif self.state == 'cancel':
            today = fields.Datetime.now()
            attendances = self.env['attendance'].sudo().search([('registration_id','=',self.id),('session_id.date','>',today)]).unlink()


        return res

    

    """def button_reg_close(self):
        for registration in self:
            today = fields.Datetime.now()
            if registration.event_id.date_begin <= today and registration.event_id.state == 'confirm':
                if registration.event_id and not registration.session_id:
                    for session in self.event_id.track_ids:
                        attendance = self.env['attendance'].search([('registration_id','=',registration.id),('session_id','=',session.id),('event_id','=',registration.event_id.id),('partner_id','=',registration.partner_id.id)])
                        if not attendance:
                            attendance = self.env['attendance'].create({
                                'registration_id': registration.id,
                                'event_id': registration.event_id.id,
                                'session_id': registration.session_id.id if registration.session_id else False,
                                'partner_id': registration.partner_id.id if registration.partner_id else False
                                }) 

                res = {
                'type': 'ir.actions.act_window',
                'name': _('Attendance'),
                'view_mode': 'tree',
                'res_model': 'attendance',
                'domain' : [('id','=',attendance.id)],
                'target': 'current',
                }

                return res

            elif registration.event_id.state == 'draft':
                raise UserError(_("You must wait the event confirmation before doing this action."))

            else:
                raise UserError(_("You must wait the event starting day before doing this action."))"""



