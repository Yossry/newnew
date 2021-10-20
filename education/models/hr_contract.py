from odoo import models, fields, api


class EmployeeContract(models.Model):
    _inherit = 'hr.contract'
    program_id = fields.Many2one('program', string="Program", required="1")
    course_id = fields.Many2one('course', string="Course", required=False)
    course_ids = fields.Many2many('course', string="Courses", required=1)
    event_type_id = fields.Many2one('event.type', string="Event Type")
    partner_id = fields.Many2one('res.partner', string="Account")
    display_partner_id = fields.Boolean('Display Account', compute='_compute_display_parter_id')
    # signed_agreement = fields.Many2one('documents.document', string="Signed Agreement")
    first_session_id = fields.Many2one('event.track', string='First session', compute="_compute_session")

    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        for contract in self.filtered(
                lambda c: c.state not in ['draft', 'cancel'] or c.state == 'draft' and c.kanban_state == 'done'):
            return True

    @api.onchange('event_type_id')
    def _onchange_event_type_id(self):
        val = {}
        if (self.event_type_id.study_format == 'inhouse'):
            val['value'] = {'display_partner_id': True}
        else:
            val['value'] = {'display_partner_id': False}
        return val

    def _compute_display_parter_id(self):
        for record in self:
            if (record.event_type_id.study_format == 'inhouse'):
                record.display_partner_id = True
            else:
                record.display_partner_id = False

    @api.onchange('employee_id', 'program_id', 'date_start')
    def _onchange_name(self):
        if (self.employee_id and self.program_id and self.date_start):
            if (self.partner_id):
                self.name = self.partner_id.name + ' - ' + self.employee_id.name + ' - ' + self.program_id.name + ' - ' + self.date_start.strftime(
                    '%d %B %Y')
            else:
                self.name = self.employee_id.name + ' - ' + self.program_id.name + ' - ' + self.date_start.strftime(
                    '%d %B %Y')

    def compute_courses(self, employee_id):
        courses = []
        contract_ids = self.env['hr.contract'].search([('employee_id', '=', employee_id.id)])
        for contract in contract_ids:
            if (contract.course_ids and contract.state == 'open'):
                for course in contract.course_ids:
                    courses.append(course.id)

            course_ids = [(6, 0, courses)]
            return course_ids

    @api.model
    def create(self, vals):
        record = super(EmployeeContract, self).create(vals)
        employee_id = self.env['hr.employee'].browse(vals.get('employee_id'))
        employee_id.write({
            'course_ids': self.compute_courses(employee_id),
        })
        if 'signed_agreement' in vals:
            print("x")
            # agreement = self.env['documents.document'].browse(vals['signed_agreement']).write(
            #     {'folder_id': employee_id.folder_id.id, 'employee_id': employee_id.id})
        return record

    def write(self, vals):
        record = super(EmployeeContract, self).write(vals)
        self.employee_id.write({
            'course_ids': self.compute_courses(self.employee_id)
        })
        return record

    @api.onchange('employee_id', 'program_id', 'course_ids')
    def onchange_start_date(self):
        if self.employee_id and self.course_ids and self.program_id:
            first_session = self.env['event.track'].search(
                [('employee_id', '=', self.employee_id.id), ('course_id', 'in', self.course_ids.ids)], limit=1,
                order='date asc')
            if first_session:
                self.date_start = first_session.date

            else:
                self.date_start = False

    @api.onchange('program_id')
    def onchange_program(self):
        if self.program_id:
            self.course_ids = False
            self.date_start = False

    def _compute_session(self):
        for record in self:
            record['first_session_id'] = False
            first_session = self.env['event.track'].search(
                [('employee_id', '=', record.employee_id.id), ('course_id', 'in', record.course_ids.ids)], limit=1,
                order='date asc')
            if first_session:
                record['first_session_id'] = first_session.id
