from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    is_instructor = fields.Boolean('Is Instructor')
    instructor_date = fields.Date('Joining Date')
    instructor_company = fields.Char('Region')
    first_name = fields.Char('First Name')
    middle_name = fields.Char('Middle Name')
    last_name = fields.Char('Last Name')
    birth_date = fields.Date('Birth Date')
    age_group = fields.Selection(
        [
        ('18-21', '18-21'),
        ('22-25', '22-25'),
        ('25-29', '25-29'),
        ('30-35', '30-35'),
        ('35-45', '35-45'),
        ('45above', '45 and above')
        ],
        string='Age Bracket') 
    nationality = fields.Many2one('res.country', string="Nationality")
    primary_email = fields.Char('Primary Email')
    street = fields.Char('Address')
    vat = fields.Char('Tax Registration Number')
    avg_rate = fields.Float('Avg IHT Rate / Hr ($)')
    corporate = fields.Boolean('Corporate Instructor')
    event_type = fields.Many2one('event.type', string="Event Type")
    experience_years = fields.Integer('Years of Experience')
    function = fields.Char('Job Position')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')
    email = fields.Char('Email')
    website = fields.Char('Website')
    title = fields.Many2one('res.partner.title', string="Title")
    supplier_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines', domain=[('move_type', 'in', ['in_invoice','in_refund']),('state', 'in', ['posted'])])
    balance_invoice_ids = fields.One2many('account.move', 'partner_id', 'Customer move lines', domain=[('state', 'in', ['posted'])]) 
    event_ids = fields.Many2many('event.event',string='Attended Events')

    attendance_ids = fields.One2many('attendance','partner_id',string='Attendances')

    attendance_count = fields.Integer('Attendance Count',compute="compute_attendance")
    avg_attendance = fields.Float('Avg attendance (%)',compute="compute_attendance")
    nb_attendance = fields.Float('Nb of Attended',compute="compute_attendance")
    
    lang = fields.Selection(
        [
        ('ar_SY', 'Arabic/العربيّة'),
        ('en_US', 'English'),
        ('fr_FR', 'French/Français')
        ],
        string='Language')
    country_id = fields.Many2one('res.country', string="Country")
    martial_status =fields.Selection(
        [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
        ],
        string='Martial Status')
    reason = fields.Text('Reason')
    is_student = fields.Boolean('Is Student')
    account_type = fields.Selection(
        [('b2c', 'B2C'),
        ('b2b', 'B2B'),
        ('b2u', 'B2U')],
        string='Account Type', default='b2c')
    phone = fields.Char('Phone')
    primary_email = fields.Char('Email')
    course_id = fields.Many2one('course',string="Courses")
    gender = fields.Selection(
        [
        ('male', 'Male'),
        ('female', 'Female')
        ],
        string='Gender')
    address = fields.Char('Address')
    maker_decision = fields.Selection(
        [
        ('hrmanager', 'Hr Manager'),
        ('ceo', 'CEO'),
        ('cfo', 'CFO'),
        ('coo', 'COO'),
        ('cmo', 'CMO'),
        ('other', 'Other')
        ],
        string='Decision Maker')

    
    is_alumni = fields.Boolean('Is Alumni')
    account_owner = fields.Boolean('Account Owner')
    fax = fields.Char('Fax')
    postal_code = fields.Char('Postal Code')
    extension = fields.Char('Extension')
    second_email = fields.Char('Second Email')
    facebook = fields.Char('Facebook')
    twitter = fields.Char('Twitter')
    instagram = fields.Char('Instagram')
    linkedin = fields.Char('Linkedin')
    comment = fields.Text('Internal Notes')
    calculated_balance=fields.Float(string='Calculated Balance:',
        compute='_compute_balance')
    account_moves=fields.One2many('account.move.line','partner_id', string='Moves')
    number_of_orders = fields.Integer('Number Of Orders')
    customer_status = fields.Selection(
        [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('dormant', 'Dormant')
        ],
        string='Customer Status',compute="compute_activation",store=False)
    image = fields.Binary()
    years_of_experience = fields.Char('Years of experience')
    other_decision_maker = fields.Char('Other Decision Maker')
    number_departments = fields.Char('Num Departments')
    number_employees = fields.Char('Num Employees')
    is_decision_maker = fields.Boolean('Is Decision Maker')
    middle_name = fields.Char('Middle Name')
    customer = fields.Boolean('Is a Customer')
    supplier = fields.Boolean('Is a Supplier')
    instructor_status = fields.Selection(
        [
        ('potential', 'Potential'),
        ('active', 'Active'),
        ('dormant', 'Dormant'),
        ('archived', 'Archived'),
        ('suspended', 'Suspended')
        ],
        string='Instructor Status')
    image_small = fields.Binary()
    rates = fields.One2many('instructor.rate','rate_id',string="Rates")
    total_sessions = fields.Integer('Total Sessions',readonly="1")
    total_number_of_hours = fields.Integer('Total Hours',readonly="1")
    total_sessions_approved = fields.Integer("Approved Sessions",readonly="1")
    reporting_period = fields.Many2many('term', string="Targeted Terms",
        readonly="1")
    instructor_timesheets = fields.One2many('purchase.order','timesheet_id')
    company_id = fields.Many2one('res.company', string="Region", domain="[('is_region', '=', True)]")
    order_date = fields.Date('Date Order')
    reason_for_rejection = fields.Text('Reason For Rejection')
    rate_ids = fields.One2many('instructor.rate', 'rate_id')
    survey_ids = fields.One2many('survey.survey', 'survey_id')
    user_id = fields.Many2one('res.users', string="Saleperson")
    ref = fields.Char('Internal Reference')
    biography = fields.Char('Biography')
    program_ids = fields.Many2many('program', string="Associated Program")
    title = fields.Many2one('res.partner.title', string="Title")
    description_one = fields.Char('Description One')
    description_two = fields.Char('Description two')
    is_vendor = fields.Boolean()
    company_legal_name = fields.Char(string='Company Legal Name',translate=True)
    not_same_as_account = fields.Boolean(string='Different Address')
    resume_line_ids = fields.One2many('hr.resume.line', 'resume_id')
    employee_skill_ids = fields.One2many('hr.employee.skill', 'partner_id')
    is_company = fields.Boolean()
    education_ids = fields.One2many('education.account','partner_id') 
    type = fields.Selection(
        [
        ('contact', 'Contact'),
        ('invoice', 'Invoice Address'),
        ('delivery', 'Delivery Address'),
        ('other', 'Other Address'),
        ('private', 'Private Address'),
        ('training', 'Training Address')
        ],
        string='Address Type')
    is_representative = fields.Boolean('Is Representative')
    education_level = fields.Many2one('education.level','Education Level')
    university = fields.Char('University')
    date_activation = fields.Date('Activation Date',store=True)

    # name = fields.Char(index=True,readonly=False,required=True)


    _sql_constraints = [
    ('name_uniq', 'unique (name)', "Contact name already exists !"),
    ]

    def compute_attendance(self):
        for record in self:
            record.avg_attendance = 0
            attendances = self.env['attendance'].sudo().search([('partner_id','=',record.id)])
            record.attendance_count = len(attendances)

            attended = self.env['attendance'].sudo().search([('partner_id','=',record.id),('attended','=',1)])
            record.nb_attendance = len(attended)

            record.avg_attendance = 0
            if len(attended) > 0:
                record.avg_attendance = (len(attended) * 100) / len(attendances)

    def show_related_attendaces(self):
        attendances = self.env['attendance'].sudo().search([('partner_id','=',self.id)])
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




    def do_process_statement_filter(self):
        account_invoice_obj = self.env['account.move'] 
        statement_line_obj = self.env['bi.statement.line']
        account_payment_obj = self.env['account.payment']
        inv_list = []
        for record in self:
            from_date = record.statement_from_date 
            to_date = record.statement_to_date

            if from_date:
                final_initial_bal = 0.0 

                in_bal = account_invoice_obj.search([('partner_id','=',record.id), \
                    ('move_type', 'in', ['out_invoice','out_refund']), ('state', 'in', ['posted']), \
                    ('invoice_date_due', '<', from_date)])
                
                for inv in in_bal :
                    final_initial_bal += inv.amount_residual

                in_pay_bal = account_payment_obj.search([('partner_id','=',record.id), \
                    ('state', 'in', ['posted', 'reconciled']),('payment_date', '<', from_date), \
                    ('partner_type', '=', 'customer')])

                for pay in in_pay_bal :
                    if not pay.reconciled_invoice_ids:
                        final_initial_bal -= pay.amount

                if final_initial_bal:
                    record.write({'initial_bal':final_initial_bal})


            domain_payment = [('partner_type', '=', 'customer'), ('state', 'in', ['posted', 'reconciled']), ('partner_id', '=', record.id)]
            domain = [('state', 'in', ['posted']), ('partner_id', '=', record.id)]
            if from_date:
                domain.append(('invoice_date', '>=', from_date))
                domain_payment.append(('payment_date', '>=', from_date))
            if to_date:
                domain.append(('invoice_date', '<=', to_date))
                domain_payment.append(('payment_date', '<=', to_date))
                 
                 
            lines_to_be_delete = statement_line_obj.search([('partner_id', '=', record.id)])
            lines_to_be_delete.unlink()
            
            
            
            invoices = account_invoice_obj.search(domain)
            payments = account_payment_obj.search(domain_payment)
            if invoices:
                for invoice in invoices.sorted(key=lambda r: r.name):
                    vals = {
                            'partner_id':invoice.partner_id.id or False,
                            'state':invoice.state or False,
                            'invoice_date':invoice.invoice_date,
                            'invoice_date_due':invoice.invoice_date_due,
                            'result':invoice.result or 0.0,
                            'name':invoice.name or '',
                            'amount_total':invoice.amount_total or 0.0,
                            'credit_amount':invoice.credit_amount or 0.0,
                            'invoice_id' : invoice.id,
                    }
                    test = statement_line_obj.create(vals)
            if payments:
                for payment in payments.sorted(key=lambda r: r.name):
                    credit_amount = 0.0
                    debit_amount = 0.0
                    if not payment.reconciled_invoice_ids:
                        for move in payment.move_line_ids:
                            if move.account_id.internal_type == 'receivable':
                                if not move.full_reconcile_id:
                                    debit_amount = move.debit
                                    credit_amount = move.credit
                    else:
                        for move in payment.move_line_ids:
                            if move.account_id.internal_type == 'receivable':
                                if move.reconciled:
                                    pass
                                else:
                                    for matched_id in move.matched_debit_ids:
                                        debit_amount = matched_id.amount
                                        credit_amount = move.credit
                    if debit_amount != 0.0 or credit_amount != 0.0:
                        vals = {
                                    'partner_id':payment.partner_id.id or False,
                                    'invoice_date':payment.payment_date,
                                    'invoice_date_due':payment.payment_date,
                                    'result':debit_amount - credit_amount or 0.0,
                                    'name':payment.name or '',
                                    'amount_total':debit_amount or 0.0,
                                    'credit_amount': credit_amount or 0.0,
                                    'payment_id' : payment.id,
                        }
                        statement_line_obj.create(vals)

    def _compute_balance(self):
      for record in self:
        totalDebit = 0.0
        totalCredit = 0.0
        if(record.account_moves):
            accountMoves = record.account_moves
            for accountMove in accountMoves:
                totalDebit += accountMove.debit
                totalCredit += accountMove.credit
        record['calculated_balance'] = totalDebit-totalCredit
    @api.onchange('account_type')
    def _onchange_email(self):
        if(self.account_type=='b2c'):
            if(self.primary_email):
                email = self.primary_email
                return {
                'value': {'email': email},
                }

    @api.onchange('not_same_as_account')
    def _onchange_premises(self):
        if(self.not_same_as_account):
            return {
            'value': {'street': False, 'street2': False, 'country_id': False, 'state_id': False, 'city': False, 'zip': False},
            }

        else:
            contact = self.parent_id
            street=contact.street
            stree2=contact.street2
            city=contact.city
            country=contact.country_id.id if contact.country_id else False
            state=contact.state_id.id if contact.state_id else False
            zip_code = contact.zip
            return {
            'value': {'street': street, 'street2': stree2, 'country_id': country, 'state_id': state, 'city': city, 'zip': zip_code},
            }

    def compute_activation(self):
        for record in self:
            status = False
            """invoices = self.env['account.move'].search([('partner_id','=',record.id),('state','=','posted'),('type','=','out_invoice'),('amount_residual','>',0)])
            if(not invoices):
                status = 'pending'

            else:
                last_invoice = self.env['account.move'].search([('partner_id','=',record.id),('state','=','posted'),('type','=','out_invoice'),('amount_residual','>',0)],order="invoice_date desc",limit=1)
                invoice_date = last_invoice.invoice_date
                date = datetime.datetime.strptime(str(invoice_date), '%Y-%m-%d')
                now = datetime.date.today()

                difference = relativedelta(now, date)
                if(difference.years > 2):
                    status = 'dormant'

                elif(difference.years <= 2):
                    status = 'active'"""

            record['customer_status'] = status

    @api.onchange('first_name','last_name','middle_name','company_legal_name','account_type')
    def onchange_name(self):


        if self.account_type == 'b2b' or self.account_type == 'b2u':
            if self.company_legal_name:
                self.name = self.company_legal_name
        
        elif self.account_type == 'b2c':
            if self.first_name:
                self.name = self.first_name

            if self.first_name and self.last_name:
                self.name = self.first_name + ' ' + self.last_name

            if self.first_name and self.last_name and self.middle_name:
                self.name = self.first_name + ' ' + self.middle_name + ' ' + self.last_name



    @api.model
    def create(self, vals):
        record = super(ResPartner, self).create(vals)


        if record.account_type == 'b2b' or record.account_type == 'b2u':
            if record.company_legal_name:
                record['name'] = record.company_legal_name


        elif record.account_type == 'b2c':
            if record.first_name:
                record['name'] = record.first_name

            if record.first_name and record.middle_name:
                record['name'] = record.first_name + ' ' + record.middle_name

            if record.first_name and record.last_name:
                record['name'] = record.first_name + ' ' + record.last_name

            if record.first_name and record.last_name and record.middle_name:
                record['name'] = record.first_name + ' ' + record.middle_name + ' ' + record.last_name

        return record

    def write(self, vals):
        for record in self:
            if record.account_type == 'b2b' or record.account_type == 'b2u':
                if record.company_legal_name:
                    vals['name'] = record.company_legal_name

            elif record.account_type == 'b2c':
                if record.first_name:
                    vals['name'] = record.first_name

                if record.first_name and record.middle_name:
                    vals['name'] = record.first_name + ' ' + record.middle_name

                if record.first_name and record.last_name:
                    vals['name'] = record.first_name + ' ' + record.last_name

                if record.first_name and record.last_name and record.middle_name:
                    vals['name'] = record.first_name + ' ' + record.middle_name + ' ' + record.last_name

        return super(ResPartner, self).write(vals)

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if not self.parent_id:
            return

        result = {}
        partner = self._origin
        if partner.parent_id and partner.parent_id != self.parent_id:
            result['warning'] = {
            'title': _('Warning'),
            'message': _('Changing the company of a contact should only be done if it '
                'was never correctly set. If an existing contact starts working for a new '
                'company then a new contact should be created under that new '
                'company. You can use the "Discard" button to abandon this change.')}

        if partner.type == 'contactt' or self.type == 'contactt':
            address_fields = self._address_fields()
            if any(self.parent_id[key] for key in address_fields):
                def convert(value):
                    return value.id if isinstance(value, models.BaseModel) else value
                result['value'] = {key: convert(self.parent_id[key]) for key in address_fields}
        return result

    """@api.constrains('name')
    def _check_name(self):
        for contact in self:
            other_contact = self.search([('name','=',contact.name),('id','!=',contact.id),('name','!=',False)])
            if other_contact:
                raise ValidationError('Contact name already exists!')"""
    
    """@api.constrains('email')
    def _check_email(self):
        for contact in self:
            other_contact = self.search([('email','=',contact.email),('id','!=',contact.id),('email','!=',False)])
            if other_contact:
                raise ValidationError('Contact email already exists!')"""


    @api.onchange('country_id')
    def onchange_country(self):
        if self.country_id:
            if self.country_id.phone_code:
                self.phone = '+' + str(self.country_id.phone_code) + ' '
                self.mobile = '+' + str(self.country_id.phone_code) + ' '

