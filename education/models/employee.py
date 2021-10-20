from odoo import models, fields, api, _
from datetime import date


class Employees(models.Model):
    _inherit = "hr.employee"
    company_id = fields.Many2one('res.company', sting="Company")
    medic_exam = fields.Date('Medical Exam')
    vehicle = fields.Char('Company Vehicle')
    vehicle_distance = fields.Integer(string="Home-Work Dist.")
    place_of_birth = fields.Char('Place of Birth')
    manager = fields.Boolean('Is a Manager')
    resource_calendar_id = fields.Many2one('resource.calendar', string="Working Hours")
    course_ids = fields.Many2many('course', compute="_compute_courses", store=True)
    is_instructor = fields.Boolean()
    joining_date = fields.Date('Joining Date', compute="_compute_joining_date")
    instructor_status = fields.Selection(
        [('draft', 'Potential'), ('active', 'Active'), ('dormant', 'Dormant'), ('suspended', 'Suspended')],
        compute="_compute_status", store=True, default='draft')
    social_twitter = fields.Char('Twitter Account')
    social_facebook = fields.Char('Facebook Account')
    social_linkedin = fields.Char('LinkedIn Account')
    social_youtube = fields.Char('Youtube Account')
    social_instagram = fields.Char('Instagram Account')
    biography = fields.Html('Biography')
    instructor_job_position = fields.Char()
    age_group = fields.Selection(
        [('18-21', '18-21'), ('22-25', '22-25'), ('25-29', '25-29'), ('30-35', '30-35'), ('35-45', '35-45'),
         ('45above', '45 and above')], string="Age Group")
    is_student = fields.Boolean('Ex student', compute="_compute_student")
    registration_number = fields.Char(company_dependent=True, string='Tax Registration Number')
    recruiting_city_id = fields.Many2one('res.company', domain="[('is_region','=',True)]", string='Recruiting City')

    def show_related_documents(self):
        ctx = {}
        print("x")
        # ctx['default_employee_id'] = self.id
        # ctx['default_folder_id'] = self.folder_id.id if self.folder_id else False
        # res = {
        #     'type': 'ir.actions.act_window',
        #     'name': _('Documents'),
        #     'view_mode': 'tree,kanban,form',
        #     'res_model': 'documents.document',
        #     'domain': [('id', 'in', self.document_ids.ids)],
        #     'target': 'current',
        #     'context': ctx,
        # }
        #
        # return res

    def _compute_courses(self):
        for record in self:
            courses = []
            for contract in record.contract_ids:
                if (contract.course_ids and contract.state == 'open'):
                    for course in contract.course_ids:
                        courses.append(course.id)
            if (courses):
                record.course_ids = [(6, 0, courses)]
            else:
                record.course_ids = [(5, 0, 0)]

    def _compute_joining_date(self):
        for record in self:
            first_contract = self.env['hr.contract'].search([('employee_id', '=', record.id)], order="date_start asc",
                                                            limit=1)
            if first_contract:
                record['joining_date'] = first_contract.date_start

            else:
                record['joining_date'] = False

    def _compute_status(self):
        for record in self:
            instructor_status = False
            if not record.active:
                instructor_status = 'suspended'


            elif not record.contract_ids:
                instructor_status = 'draft'

            else:
                open_contract = self.env['hr.contract'].search(
                    [('employee_id', '=', record.id), ('state', '=', 'open')], limit=1)
                if open_contract:
                    instructor_status = 'active'

                else:
                    states = []
                    contracts = self.env['hr.contract'].search([('employee_id', '=', record.id)])
                    for contract in contracts:
                        states.append(contract.state)

                    if 'cancel' in states or 'close' in states:
                        instructor_status = 'dormant'

                    else:
                        instructor_status = 'draft'

            record.instructor_status = instructor_status

    @api.onchange('address_id')
    def _onchange_address(self):
        if not self.is_instructor:
            self.work_phone = self.address_id.phone
            self.mobile_phone = self.address_id.mobile
        else:
            self.work_phone = False
            self.mobile_phone = False

    def _compute_student(self):
        self.is_student = False
        if self.address_home_id:
            invoices = self.env['account.move'].search(
                [('partner_id', '=', self.address_home_id.id), ('invoice_date', '<', self.create_date),
                 ('state', '=', 'posted')])
            if invoices:
                self.is_student = True

    @api.onchange('birthday')
    def onchange_birthday(self):
        today = date.today()
        if self.birthday:
            age = today.year - self.birthday.year - (
                        (self.birthday.month, today.day) < (self.birthday.month, self.birthday.day))
            age_group = '18-21'
            if age >= 18 and age <= 21:
                age_group = '18-21'

            elif age > 21 and age <= 25:
                age_group = '22-25'

            elif age > 25 and age <= 29:
                age_group = '25-29'

            elif age > 30 and age <= 35:
                age_group = '30-35'

            elif age > 35 and age <= 45:
                age_group = '35-45'

            elif age > 45:
                age_group = '45above'

            self.age_group = age_group

    @api.onchange('country_id')
    def onchange_country(self):
        if self.country_id:
            if self.country_id.phone_code:
                self.work_phone = '+' + str(self.country_id.phone_code) + ' '
                self.mobile_phone = '+' + str(self.country_id.phone_code) + ' '

class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    timesheet_manager_id = fields.Many2one('res.users', string='Timesheet',
        help="User responsible of timesheet validation. Should be Timesheet Manager.")
