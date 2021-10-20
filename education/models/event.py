from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError


class Event(models.Model):
    _inherit = "event.event"
    state = fields.Selection(
        [('draft', 'Draft'), ('cancel', 'Cancelled'), ('confirm', 'Registration Open'), ('done', 'Done')],
        default='draft')
    program_id = fields.Many2one('program', string="Program", required="1")
    location_id = fields.Many2one('event.track.location', "Class Room", domain="[('region_id', '=', company_id)]")
    course_id = fields.Many2one('course', string="Course")
    term_id = fields.Many2one('term', string="Targeted Term")
    event_type_id = fields.Many2one('event.type', string="Type")
    period_id = fields.Many2one('event.period', string="Event Period")
    class_room_id = fields.Many2one('event.track.location', string="Class Room")
    hide_from_website = fields.Boolean('Hide From Website')
    company_id = fields.Many2one(string="Region", domain="[('is_region', '=', True)]",
                                 default=lambda self: self._get_child_companies())
    organizer_ids = fields.Many2many('hr.employee',
                                     string="Instructor",
                                     readonly="1",
                                     compute='_compute_instructors')
    currency_id = fields.Many2one('res.currency', string="Currency")
    user_id = fields.Many2one(string="Facilitator")
    survey_ids = fields.One2many('survey.survey', 'survey_id')
    meta_key_words = fields.Text('Meta Keywords')
    description = fields.Text('Description')
    mapped_item_ids = fields.One2many('mapped.items', 'items')
    schedule_ids = fields.One2many('event.schedule', 'schedule_id')
    order_line_ids = fields.One2many('sale.order.line', 'event_id', string="Sale Order Lines")
    certificates_count = fields.Integer(
        string='Certificates count',
        compute='_compute_certificates_count')
    unconfirmed_qty = fields.Integer(
        string='Unconfirmed Qty',
        compute='_compute_unconfirmed_qty',
        store=True)

    forecasted_sale_ids = fields.One2many('event.sale.forecast', 'event_id', string='Projected Sales')
    target = fields.Float('Target')
    actual_sales = fields.Float('Actual Sales', compute="_compute_actual_sales", store=False)
    total_opportunities = fields.Integer('Total Opportunities', store=False, compute="compute_total_opportunities")

    actual_vs_target = fields.Float('Actucal vs Target(%)', compute="_compute_actual_vs_target", store=False)

    attendance_count = fields.Integer('Attendance Count', compute="compute_attendance")

    total_revenue = fields.Float('Total Revenue', compute="compute_total_revenue")
    total_expenses = fields.Float('Total Expenses', compute="compute_total_expenses")
    total_instructor_rates = fields.Float(string='Total Instructor Rates', compute="compute_total_instructor_rates")
    total = fields.Float('Total', compute="compute_total")

    expense_ids = fields.One2many('hr.expense', 'event_id', string='Expenses')

    date_tz = fields.Selection(related='company_id.date_tz')

    avg_attendance = fields.Float('Avg attendance (%)', compute="compute_attendance")
    nb_attendance = fields.Float('Nb of Attended', compute="compute_attendance")

    auto_confirm = fields.Boolean(copy=False)
    currency_usd = fields.Many2one('res.currency', compute="compute_currency_usd")

    attempt_count = fields.Float('Nb of attempts', compute="compute_attempt")
    passing_rate = fields.Float('Passing Rate (%)', compute="compute_attempt")

    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        for event in self:
            if event.date_end and event.date_begin:
                if event.date_end < event.date_begin:
                    raise ValidationError(_('The closing date cannot be earlier than the beginning date.'))

    def compute_currency_usd(self):
        for record in self:
            record['currency_usd'] = self.env.ref('base.USD').id

    def action_view_certificates(self):
        return {
            "name": _("Certificates"),
            "type": 'ir.actions.act_window',
            "res_model": 'certificate',
            "view_mode": "tree",
            "domain": [('event_id', '=', self.id)]
        }

    def generate_certificates(self):
        registrations = self.env['event.registration'].search([('event_id', '=', self.id), ('state', '=', 'open')])
        for reg in registrations:
            self.env['certificate'].create({
                'student_id': reg.partner_id.id,
                'event_id': reg.event_id.id,
                'registration_id': reg.id,
                'company_id': self.company_id.id
            })

    def generate_sessions(self):
        facilitator = self.user_id
        course = self.course_id
        company = self.company_id
        startDate = self.date_begin
        endDate = self.date_end
        classRoom = self.location_id
        sessionsNaming = []
        topics = course.topic_ids
        topics_data = {}
        for topic in topics:
            for x in range(topic.nb_sessions):
                tax_ids = []
                topic_price = 0
                company_topic_price = self.env['company.topic.price'].search(
                    [('company_id', '=', company.id), ('topic_region_id', '=', topic.id)])
                if (company_topic_price):
                    topic_price = company_topic_price.price
                    for tax in company_topic_price.tax_ids:
                        tax_ids.append(tax.id)
                topics_data[topic.id] = {
                    'name': topic.name,
                    'price': topic_price,
                    'tax_ids': [(6, False, tax_ids)]
                }
                sessionsNaming.append(topic.id)
        nbSessions = course.nb_sessions
        generatedSessions = 0
        schedules = self.schedule_ids
        DateFrom = False
        if (not schedules):
            raise ValidationError(_(
                "Please fill the schedules before generating sessions"))
        if (self.track_count == 0):
            while generatedSessions < nbSessions:
                for schedule in schedules:
                    day = schedule.day
                    fromHour = schedule.schedule_from
                    toHour = schedule.schedule_to
                    duration = schedule.schedule_to - schedule.schedule_from
                    instructor = schedule.instructor_id
                    DateFrom = self.env['event.event'].getDateTime(startDate, day, fromHour)
                    DateTo = self.env['event.event'].getDateTime(startDate, day, toHour)
                    startDate = str(self.env['event.event'].getDate(startDate, day, toHour))
                    sessionId = False
                    try:
                        sessionId = sessionsNaming[generatedSessions]
                    except:
                        sessionId = False
                    if (sessionId):
                        session = self.env['event.track'].create({
                            'employee_id': instructor.id,
                            'name': topics_data[sessionId]['name'],
                            'price': topics_data[sessionId]['price'],
                            'tax_ids': topics_data[sessionId]['tax_ids'],
                            'date': DateFrom,
                            'duration': duration,
                            'location_id': classRoom.id,
                            'event_id': self.id,
                            'track_from': fromHour,
                            'to': toHour,
                            'user_id': facilitator.id,
                            'day': day,
                            'company_id': company.id,
                            'partner_id': instructor.address_id.id,
                            'partner_name': instructor.address_id.name,
                            'partner_email': instructor.address_id.email,
                            'partner_phone': instructor.address_id.phone,
                            'partner_biography': instructor.address_id.website_description
                        })
                    generatedSessions = generatedSessions + 1
            if DateFrom:
               self.write({'date_end': DateFrom})

    def _compute_instructors(self):
        instructorArray = []
        for session in self.track_ids:
            instructor = session.employee_id
            instructorArray.append(instructor.id)
        self.organizer_ids = [(6, 0, instructorArray)]

    @api.onchange('location_id')
    def _onchange_class_room_id(self):
        val = {}
        address_id = False
        if (self.location_id.location_id):
            address_id = self.location_id.location_id.id
        val['value'] = {'address_id': address_id}
        return val

    @api.onchange('course_id')
    def on_change_course(self):
        if self.course_id:
            course = self.course_id
            self.update({'event_mail_ids': [(5, 0, 0)]})
            if course.course_mail_ids:
                mails = course.course_mail_ids
                communication_ids = {}
                for mail in mails:
                    self.update({
                        'event_mail_ids': [(0, 0, {
                            'notification_type': mail.notification_type,
                            'interval_unit': mail.interval_unit,
                            'interval_type': mail.interval_type,
                            'template_id': mail.template_id.id})]
                    })

    @api.onchange('program_id')
    def _onchange_program_id(self):
        val = {}
        val['value'] = {'course_id': False}
        return val

    @api.onchange('course_id', 'company_id', 'period_id', 'term_id', 'date_begin')
    def _onchange_course(self):
        if (self.course_id):
            regionId = self.company_id.id
            course = self.course_id
            prices = course.region_prices
            val = {}
            value = {}
            tickets = []
            self.update({'event_ticket_ids': [(5, 0, 0)]})
            event_product_id = self.env.ref('event_sale.product_product_event').id
            region_prices = self.env['company.price'].search(
                [('course_region_id', '=', course.id), ('company_id', '=', self.company_id.id)])
            for region_price in region_prices:
                tax_ids = []
                if (region_price.tax_ids):
                    for tax_id in region_price.tax_ids:
                        tax_ids.append(tax_id.id)
                    tax_ids = [(6, 0, tax_ids)]
                else:
                    tax_ids = [(5, 0, 0)]
                for ticket in region_price.ticket_ids:
                    mapped_items = []
                    if (ticket.mapped_item_ids):
                        for mapped_item in ticket.mapped_item_ids:
                            mapped_items.append(mapped_item.id)
                        mapped_items = [(6, 0, mapped_items)]
                    else:
                        mapped_items = [(5, 0, 0)]
                    ticket_deadline = False
                    if (ticket.deadline and self.date_begin):
                        ticket_deadline = self.date_begin.date() - datetime.timedelta(ticket.deadline)

                    tickets.append((0, 0,
                                    {'name': ticket.name, 'product_id': event_product_id, 'price': ticket.local_price,
                                     'deadline': ticket_deadline, 'mapped_item_ids': mapped_items, 'tax_ids': tax_ids}))
            companyIds = []
            value.update(event_ticket_ids=tickets)
            value['event_ticket_ids'] = tickets
            event_name = ''
            if (course):
                event_name = course.name
            if (self.period_id):
                event_name = event_name + ' - ' + self.period_id.name
            if (self.term_id):
                event_name = event_name + ' - ' + self.term_id.name
            value['name'] = event_name
            for price in prices:
                companyIds.append(price.company_id.id)
                val['domain'] = {'company_id': [('id', 'in', companyIds)]}
            val['value'] = value
            return val

    def getDateTime(self, startDate, day, hourFrom):
        firstDate = startDate
        if (isinstance(firstDate, str)):
            firstDate = datetime.datetime.strptime(firstDate, '%Y-%m-%d')
        weekday = int(day)
        days_ahead = weekday - firstDate.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        day = firstDate + datetime.timedelta(days_ahead)
        fromHour = int(hourFrom)
        fromMinutes = int((hourFrom - fromHour) * 60)
        fromDate = day.replace(hour=fromHour, minute=fromMinutes)
        return fromDate

    def getDate(self, startDate, day, hourFrom):
        firstDate = startDate
        if (isinstance(firstDate, str)):
            firstDate = datetime.datetime.strptime(firstDate, '%Y-%m-%d')
        weekday = int(day)
        days_ahead = weekday - firstDate.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        day = firstDate + datetime.timedelta(days_ahead)
        fromHour = int(hourFrom)
        fromMinutes = int((hourFrom - fromHour) * 60)
        fromDate = day.replace(hour=fromHour, minute=fromMinutes)
        return fromDate.date()

    def _compute_certificates_count(self):
        for event in self:
            cer_obj =  self.env['certificate'].search_count([('event_id', '=', event.id)])
            if cer_obj:
               event.certificates_count = cer_obj
            else:
                event.certificates_count = 0

    def _compute_unconfirmed_qty(self):
        for event in self:
            event.unconfirmed_qty = int(sum(event.order_line_ids.filtered(
                lambda x: x.order_id.state in ('draft', 'sent')
            ).mapped('product_uom_qty')))

    @api.onchange('company_id')
    def _onchange_company_id(self):
        val = {}
        value = {}
        date_timezone = self.env.user.tz or 'UTC'
        if self.company_id:
            date_timezone = self.company_id.date_tz
            value['date_tz'] = date_timezone
            website_id = self.env['website'].search(
                ['|', ('company_id', '=', self.company_id.parent_id.id), ('company_id', '=', self.company_id.id)],
                limit=1)
            value['website_id'] = website_id.id
        val['value'] = value
        return val

    def compute_total_opportunities(self):
        for record in self:
            record.total_opportunities = len(record.forecasted_sale_ids)

    def _compute_actual_vs_target(self):
        for record in self:
            result = 0.0
            if (record.target != 0):
                result = (record.actual_sales / record.target) * 100
            record['actual_vs_target'] = result

    @api.depends('order_line_ids')
    def _compute_actual_sales(self):
        for record in self:
            actualSales = 0.0
            if (record.order_line_ids):
                for orderLine in record.order_line_ids:
                    actualSales = actualSales + orderLine.price_subtotal
            record['actual_sales'] = actualSales

    def compute_attendance(self):
        for record in self:
            record.avg_attendance = 0
            attendances = self.env['attendance'].sudo().search([('event_id', '=', record.id)])
            record.attendance_count = len(attendances)

            attended = self.env['attendance'].sudo().search([('event_id', '=', record.id), ('attended', '=', 1)])
            record.nb_attendance = len(attended)

            record.avg_attendance = 0
            if len(attended) > 0:
                record.avg_attendance = (len(attended) * 100) / len(attendances)

    def show_related_attendaces(self):
        attendances = self.env['attendance'].search([('event_id', '=', self.id)])
        if attendances:
            res = {
                'type': 'ir.actions.act_window',
                'name': _('Attendance'),
                'view_mode': 'tree',
                'res_model': 'attendance',
                'domain': [('id', 'in', attendances.ids)],
                'target': 'current',
            }

            return res

    def compute_total_expenses(self):
        for record in self:
            totalExpense = 0
            expenses = self.env['hr.expense'].search([('event_id', '=', record.id)])
            for expense in expenses:
                if (expense.company_id.id != record.company_id.id):
                    totalExpense = (totalExpense + expense.unit_amount) * record.company_id.currency_id.rate
                else:
                    totalExpense = totalExpense + expense.unit_amount

            record['total_expenses'] = totalExpense

    def compute_total_revenue(self):
        for record in self:
            totalRevenue = 0
            revenues = self.env['sale.order.line'].search([('event_id', '=', record.id)])
            for revenue in revenues:
                if (revenue.order_id.company_id.id != record.company_id.id):
                    totalRevenue = (
                                           totalRevenue + revenue.price_unit * revenue.product_uom_qty) * revenue.currency_id.rate

                else:
                    totalRevenue = totalRevenue + revenue.price_unit * revenue.product_uom_qty

            record['total_revenue'] = totalRevenue

    def compute_total_instructor_rates(self):
        for record in self:
            total = 0
            for instructor in record.organizer_ids:
                attendances = self.env['hr.attendance'].search([('employee_id', '=', instructor.id)])
                for attendance in attendances:
                    session = attendance.session_id
                    worked_days = self.env['hr.payslip.worked_days'].search([('name', '=', session.name)])
                    for day in worked_days:
                        total = total + day.amount

            record['total_instructor_rates'] = total

    def compute_total(self):
        for record in self:
            record['total'] = record.total_revenue - (record.total_expenses + record.total_instructor_rates)

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            if self.course_id.type_id:
                self.event_type_id = self.course_id.type_id.id

    @api.model
    def updateMenuItem(self):
        locations_menu = self.env.ref('website_event_track.menu_event_track_location')
        self.env.cr.execute("update ir_ui_menu set name = 'Class Rooms' where id = " + str(locations_menu.id))

    @api.model
    def create(self, vals):
        record = super(Event, self).create(vals)
        if record.course_id:
            if record.course_id.type_id:
                record['event_type_id'] = record.course_id.type_id.id

        return record

    def write(self, vals):
        if self.course_id:
            if self.course_id.type_id:
                vals['event_type_id'] = self.course_id.type_id.id
        return super(Event, self).write(vals)

    def _get_child_companies(self):
        company = self.env.company
        child_company = self.env['res.company'].search([('parent_id', '=', company.id)], limit=1)
        if child_company:
            return child_company.id
        else:
            return company.id

    @api.constrains('term_id', 'date_begin', 'date_end')
    def _check_date(self):
        if self.term_id:
            if self.date_begin:
                if self.date_begin.date() < self.term_id.start_date:
                    raise ValidationError("Event start date should not be less than the start date of the term")

            if self.date_end:
                if self.date_end.date() > self.term_id.end_date:
                    raise ValidationError("Event end date should not be greater than the end date of the term")

    def compute_attempt(self):
        for record in self:
            record['passing_rate'] = 0
            nb_attempt = 0
            attempts = record.registration_ids.mapped('attempt_ids')
            record['attempt_count'] = len(attempts)
            passed_attempts = attempts.filtered(lambda c: c.passing_status == 'passed')
            if len(attempts) > 0:
                record['passing_rate'] = (len(passed_attempts) * 100) / len(attempts)
