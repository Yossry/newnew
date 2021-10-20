from odoo import models, fields,api,_
from odoo.exceptions import UserError
from odoo.tools import date_utils


class Payslip(models.Model):
    _inherit = 'hr.payslip'
    journal_id = fields.Many2one(related=False,store=True,domain="[('company_id', '=', company_id),('type','=','bank')]")
    company_id = fields.Many2one(string="Region", domain="[('is_region', '=', True)]",default=lambda self: self._get_child_companies())

    def _get_worked_day_lines(self):
        res = []
        self.ensure_one()
        attendances = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('session_id.is_paid','=',False)])
        #raise UserError(attendances)
        for attendance in attendances:
            hours = attendance.worked_hours
            session = attendance.session_id
            course = session.course_id
            amount = 0
            contract = self.env['hr.contract'].search([('course_id','=',course.id),('employee_id','=',self.employee_id.id)],limit=1)
            if contract:
                amount = contract.wage * hours
                contract = contract.id


            attendance_line = {
            #'sequence': work_entry_type.sequence,
            'work_entry_type_id': self.env.ref('hr_work_entry.work_entry_type_attendance').id,
            'date': attendance.check_in,
            'contract_id': contract,
            'name': session.name,
            'number_of_hours': hours,
            'amount': amount,
            }
            res.append(attendance_line)
        return res

    @api.onchange('company_id')
    def onchange_company(self):
        if self.company_id:
            payslip_journal = self.env['account.journal'].search([('company_id','=',self.company_id.id),('type','=','bank'),('name','=','Instructor Payments')],limit=1)
            if payslip_journal:
                self.journal_id = payslip_journal.id

    def _get_child_companies(self):
        company = self.env.company
        child_company = self.env['res.company'].search([('parent_id','=',company.id)],limit=1)
        if child_company:
            return child_company.id
        else:
            return company.id

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return

            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s' % (payslip_name, self.employee_id.name or '')

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _("This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()
