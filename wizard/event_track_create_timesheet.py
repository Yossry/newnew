# -*- coding: utf-8 -*-

import logging
import re
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, MissingError

class EventTrackCreateTimesheet(models.TransientModel):
    _name = 'event.track.create.timesheet'
    _description = 'Session Timesheet Wizard'
    check_in = fields.Datetime('Start Date')
    check_out = fields.Datetime('End Date')
    session_id = fields.Many2one('event.track',string="Session")
    employee_id = fields.Many2one('hr.employee',string="Instructor")
    
    def save_timesheet(self):
        values = {
            'session_id': self.session_id.id,
            'check_in': self.check_in,
            'check_out': self.check_out,
            'employee_id': self.employee_id.id,

            
        }
        return self.env['hr.attendance'].create(values)