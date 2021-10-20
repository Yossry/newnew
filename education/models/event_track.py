from odoo import models, fields, _, api

class EventTrack(models.Model):
    _inherit = 'event.track'
    course_id = fields.Many2one('course', string="Course", related='event_id.course_id')
    user_id = fields.Many2one(string="Facilitator")
    active = fields.Boolean('Active', default=True)
    price = fields.Float('Price')
    tax_ids = fields.Many2many('account.tax')
    timesheet_timer_first_start = fields.Datetime()
    location_id = fields.Many2one('event.track.location', "Class Room")
    hide_from_website = fields.Boolean('Hide From Website')
    timesheet_timer_pause = fields.Datetime("Timesheet Timer Last Pause")
    employee_id = fields.Many2one('hr.employee', string='Instructor')
    stage_id = fields.Many2one(
        'event.track.stage', string='Stage', ondelete='SET NULL',
        index=True, copy=False,
        group_expand='_read_group_stage_ids',
        required=True, tracking=True)
    day = fields.Selection(
        [
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6','Sunday')
        ],
        string='Day',
        computed="true")  
    company_id = fields.Many2one('res.company', string="Company", domain="[('is_region', '=', True)]")
    seats_max = fields.Integer(string='Maximum Attendees Number', related='event_id.seats_max')
    seats_reserved = fields.Integer(
        string='Reserved Seats',
        store=True, readonly=True, compute='_compute_seats')
    seats_available = fields.Integer(
        string='Available Seats',
        store=True, readonly=True, compute='_compute_seats')
    seats_unconfirmed = fields.Integer(
        string='Unconfirmed Seat Reservations',
        store=True, readonly=True, compute='_compute_seats')
    seats_used = fields.Integer(
        string='Number of Participants',
        store=True, readonly=True, compute='_compute_seats')
    seats_expected = fields.Integer(
        string='Number of Expected Attendees',
        compute_sudo=True, readonly=True, compute='_compute_seats')
    # Registration fields
    registration_ids = fields.One2many(
        'event.registration', 'session_id', string='Attendees',
        readonly=False)
    session_id = fields.Many2one('event.track.location')
    is_instructor = fields.Boolean('Is Instructor')
    name = fields.Char('Session Name')
    date = fields.Datetime('Session Date')
    track_id = fields.Many2one('event.event',string="Session")
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    track_from = fields.Float('From')
    timesheet_timer_start = fields.Datetime('Timesheet Timer Start')
    allow_timesheets = fields.Boolean('Allow timesheets')
    display_timesheet_timer = fields.Boolean('Display Timesheet Time', compute='_compute_display_timer')
    total_hours_spent = fields.Float("Total Hours", compute='_compute_total_hours_spent', help="Computed as: Sum of timesheet hours related to this session")
    display_timsheets = fields.Boolean('Display Timesheets Button', compute='_compute_display_timsheets')
    display_start_button = fields.Boolean('Display Start Button', compute='_compute_display_start')
    display_stop_button = fields.Boolean('Display Start Button', compute='_compute_display_stop')
    to = fields.Float('To')
    subtask_effective_hours = fields.Float("Sub-tasks Hours Spent", compute='', store=True, help="Sum of actually spent hours on the subtask(s)")
    order_line_ids = fields.One2many('sale.order.line', 'track_id')
    unconfirmed_qty = fields.Integer(string='Unconfirmed Qty',
        compute='_compute_unconfirmed_qty',
        store=True)

    is_paid = fields.Boolean()

    attendance_ids = fields.One2many('attendance','session_id',string='Attendances')

    attendance_count = fields.Integer('Attendance Count',compute="compute_attendance")
    avg_attendance = fields.Float('Avg attendance (%)',compute="compute_attendance")
    nb_attendance = fields.Float('Nb of Attended',compute="compute_attendance")

    def compute_attendance(self):
        for record in self:
            record.avg_attendance = 0
            attendances = self.env['attendance'].sudo().search([('session_id','=',record.id)])
            record.attendance_count = len(attendances)

            attended = self.env['attendance'].sudo().search([('session_id','=',record.id),('attended','=',1)])
            record.nb_attendance = len(attended)

            record.avg_attendance = 0
            if len(attended) > 0:
                record.avg_attendance = (len(attended) * 100) / len(attendances)

    def show_related_attendaces(self):
        attendances = self.env['attendance'].search([('session_id','=',self.id)])
        if attendances:
            res = {
            'type': 'ir.actions.act_window',
            'name': _('Attendance'),
            'view_mode': 'tree',
            'res_model': 'attendance',
            'domain' : [('id','in',attendances.ids)],
            'target': 'current',
            }

            return res
        
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0
        for record in self:
            record.seats_unconfirmed = record.seats_reserved = record.seats_used = record.seats_available = 0
        # aggregate registrations by event and by state
        if self.ids:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT session_id, state, count(session_id)
                        FROM event_registration
                        WHERE session_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY session_id, state
                    """
            self.env['event.registration'].flush(['session_id', 'state'])
            self._cr.execute(query, (tuple(self.ids),))
            for session_id, state, num in self._cr.fetchall():
                session = self.browse(session_id)
                session[state_field[state]] += num
        # compute seats_available
        for record in self:
            if record.seats_max > 0:
                record.seats_available = record.seats_max - (record.seats_reserved + record.seats_used)
            record.seats_expected = record.seats_unconfirmed + record.seats_reserved + record.seats_used
                
    def _compute_display_timsheets(self):
        for record in self:
            total_worked = 0
            attendances = self.env['hr.attendance'].search([('session_id', '=', record.id)])
            if(attendances):
                record.display_timsheets = True
            else:
                record.display_timsheets = False
            
    def _compute_total_hours_spent(self):
        for record in self:
            total_worked = 0
            attendances = self.env['hr.attendance'].search([('session_id', '=', record.id)])
            for attendance in attendances:
                total_worked = total_worked + attendance.worked_hours
            record.total_hours_spent = total_worked
            
    def _compute_display_stop(self):
        for record in self:
            if record.start_date and not record.end_date:
                record.display_stop_button = True
            else:
                record.display_stop_button = False
                
    def _compute_display_start(self):
        for record in self:
            if not record.start_date and not record.end_date:
                record.display_start_button = True
            else:
                record.display_start_button = False
    
    def _compute_display_timer(self):
        for record in self:
            if record.start_date and not record.end_date:
                record.display_timesheet_timer = True
            else:
                record.display_timesheet_timer = False
            
                
    def _compute_unconfirmed_qty(self):
        for track in self:
            track.unconfirmed_qty = int(sum(track.order_line_ids.filtered(
                lambda x: x.order_id.state in ('draft', 'sent')
                ).mapped('product_uom_qty')))
    
    def action_timer_start(self):
        self.ensure_one()
        if not self.start_date:
            self.write({
                'start_date': fields.Datetime.now()
            })
        return self.write({'timesheet_timer_start': fields.Datetime.now()})
        
    def action_timer_stop(self):
        self.ensure_one()
        start_time = self.timesheet_timer_start
        if start_time:  # timer was either running or paused
            self.write({
                'end_date': fields.Datetime.now()
            })
        check_out = fields.Datetime.now()
        session_id = self.id
        check_in = self.start_date
        employee_id = self.employee_id.id
        self.write({'stage_id': self.env.ref('website_event_track.event_track_stage1').id})
        return self._action_create_timesheet(session_id, check_in, check_out, employee_id)
        
    def _action_create_timesheet(self, session_id, check_in, check_out, employee_id ):
        return {
            "name": _("Confirm Attendance"),
            "type": 'ir.actions.act_window',
            "res_model": 'event.track.create.timesheet',
            "views": [[False, "form"]],
            "target": 'new',
            "context": {
                **self.env.context,
                'active_id': self.id,
                'active_model': 'event.track',
                'default_session_id': session_id,
                'default_check_in': check_in,
                'default_check_out': check_out,
                'default_employee_id': employee_id,
            }
        }
    
    def action_view_timesheets(self):
        return {
            "name": _("Timesheet"),
            "type": 'ir.actions.act_window',
            "res_model": 'hr.attendance',
            "views": [[False, "tree"]],
            "domain": [('session_id', '=', self.id)]
        }
        
    @api.onchange('company_id')
    def _onchange_company(self):
        val = {}
        domain = {}
        value = {}
        taxes = []
        taxes_parent = []
        available_taxes = []
        if(self.company_id):
            taxes = self.env['account.tax'].search(
                [
                    ('company_id', '=', self.company_id.id),
                    ('type_tax_use', '=', 'sale')
                ])
            for tax in taxes:
                available_taxes.append(tax.id)
            if(self.company_id.parent_id):
                taxes_parent = self.env['account.tax'].search(
                    [('company_id', '=', self.company_id.parent_id.id),
                    ('type_tax_use', '=', 'sale')])
                for tax in taxes_parent:
                    available_taxes.append(tax.id)
        domain['tax_ids'] = [('id', 'in', available_taxes)]
        val['domain'] = domain
        val['value'] = {'tax_ids': False}
        return val
        
    def action_view_registrations(self):
        return {
            "name": _("Registrations"),
            "type": 'ir.actions.act_window',
            "res_model": 'event.registration',
            "view_mode": "kanban,tree,form,calendar,graph,cohort",
            "context": {'search_default_session_id': self.id, 'default_session_id': self.id, 'search_default_expected': True}
        }