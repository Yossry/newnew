from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = ['crm.lead']
    company_id = fields.Many2one('res.company', string="Region", domain="[('is_region', '=', True)]",
                                 default=lambda self: self._get_child_companies())
    industry_id = fields.Many2one('res.partner.industry', string="Industry")
    program_id = fields.Many2one('program', string="Program")
    expiration = fields.Selection([('expired', 'Expired'), ('not expired', 'Not Expired')])
    course_ids = fields.Many2many('course', string='Courses')
    study_format = fields.Selection(
        [('multiple', 'Multiple Formats'), ('live', 'Live Class'), ('liveonline', 'Live Online'),
         ('self', 'Self-Study'), ('online', 'Online'), ('inhouse', 'In House'), ('private', 'Private Tutoring')],
        string='Study Format')
    event_ids = fields.Many2many('event.event', string='Events')
    event_id = fields.Many2one('event.event', 'Event')
    product_ids = fields.Many2many('product.template', string='Products')
    reporting_period = fields.Many2one('term', 'Targeted Term')
    exam_id = fields.Many2one('exam', string='Exam Window')
    factor_of_decision = fields.Many2one('factor.decision', 'Factor of decision')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    middle_name = fields.Char(string='Middle Name')
    program_ids = fields.Many2many('program', string='Programs')
    stage = fields.Selection(
        [('fourtyeight', '48 Hours'), ('gptoweek', 'Up To 1 Week'), ('htop1months', 'Up To 90 Days'),
         ('overthree', 'Over 3 Months')])
    days = fields.Integer(string='Days', compute="_compute_days")
    exam = fields.Boolean(related='company_id.exam')
    cpf = fields.Boolean(related='company_id.cpf')
    quotation_revenue = fields.Float(string='Quotation Revenue')
    simulated_revenue = fields.Float(string='Simulated Revenue')
    event_ticket_id = fields.Many2one('event.event.ticket')
    call_count = fields.Integer(compute="compute_nb_visits")
    visit_count = fields.Integer(compute="compute_nb_visits")
    call_ids = fields.One2many('calendar.event', 'opportunity_id', string='Office Calls',
                               domain="[('is_call','=',True)]")
    visit_ids = fields.One2many('calendar.event', 'opportunity_id', string='Offline Visits',
                                domain="[('is_visit','=',True)]")

    @api.onchange('first_name', 'last_name', 'middle_name')
    def _fill_lead_name(self):
        lead_name = ''
        if (self.first_name):
            lead_name += self.first_name + ' '
        if (self.last_name):
            lead_name += self.last_name

        if self.middle_name:
            lead_name += self.middle_name
        return {'value': {'name': lead_name, 'contact_name': lead_name}}

    @api.onchange('company_id', 'program_id', 'study_format')
    def _clear_courses(self):
        return {'value': {'course_ids': [(5, 0, 0)]}}

    @api.depends('create_date')
    def _compute_days(self):
        for record in self:
            now = datetime.datetime.now()
            if (record.create_date):
                date = datetime.datetime.strptime(record.create_date, '%Y-%m-%d')
                leadDate = now - date
                record.days = leadDate.days

    @api.model
    def create(self, vals):
        record = super(CrmLead, self).create(vals)

        self.env['event.sale.forecast'].search([('opportunity_id', '=', record.id)]).unlink()
        expectedRevenue = 0
        # Get All Events
        for event in record.event_ids:
            event_price = 0
            if event.event_ticket_ids:
                for ticket in event.event_ticket_ids:
                    event_price += ticket.price
                event_price = event_price / len(event.event_ticket_ids)

            self.env['event.sale.forecast'].create({
                'event_id': event.id,
                'opportunity_id': record.id,
                'partner_id': record.partner_id.id if record.partner_id else False,
                'price_unit': event_price,
                'probability': record.probability,
                'amount': event_price * (record.probability / 100)
            })

        record['simulated_revenue'] = (record.planned_revenue * record.probability) / 100

        return record

    def write(self, vals):
        res = super(CrmLead, self).write(vals)

        for order in self.order_ids:
            if order.state in ['sale', 'done']:
                raise ValidationError("This opportunity has an invoiced order, you can't change it")

        self.env['event.sale.forecast'].search([('opportunity_id', '=', self.id)]).unlink()
        expectedRevenue = 0
        # Get All Events
        for event in self.event_ids:
            event_price = 0
            if event.event_ticket_ids:
                for ticket in event.event_ticket_ids:
                    event_price += ticket.price
                event_price = event_price / len(event.event_ticket_ids)

            self.env['event.sale.forecast'].create({
                'event_id': event.id,
                'opportunity_id': self.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'price_unit': event_price,
                'probability': self.probability,
                'amount': event_price * (self.probability / 100)
            })

        simulated_revenue = (self.planned_revenue * self.probability) / 100
        self.env.cr.execute(
            "UPDATE crm_lead set simulated_revenue = " + str(simulated_revenue) + " where id = " + str(self.id))
        return res

    def _get_child_companies(self):
        company = self.env.company
        child_company = self.env['res.company'].search([('parent_id', '=', company.id)], limit=1)
        if child_company:
            return child_company.id
        else:
            return company.id

    @api.onchange('email_from')
    def _onchange_email(self):
        if self.email_from:
            if self.type == 'opportunity':
                partner = self.env['res.partner'].search([('email', '=', self.email_from)], limit=1)
                if partner:
                    self.partner_id = partner.id

    def compute_nb_visits(self):
        for record in self:
            calls = self.env['calendar.event'].search([('opportunity_id', '=', record.id), ('is_call', '=', True)])
            visits = self.env['calendar.event'].search([('opportunity_id', '=', record.id), ('is_visit', '=', True)])
            record['call_count'] = len(calls)
            record['visit_count'] = len(visits)

    def show_related_calls(self):
        calls = self.env['calendar.event'].search([('opportunity_id', '=', self.id), ('is_call', '=', True)])
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Calls'),
            'view_mode': 'tree,form',
            'res_model': 'calendar.event',
            'domain': [('id', 'in', calls.ids)],
            'target': 'current',
            'context': {'default_opportunity_id': self.id, 'default_is_call': True,
                        'form_view_ref': 'education.calendar_event_call_vist_form'}
        }

        return res

    def show_related_visits(self):
        visits = self.env['calendar.event'].search([('opportunity_id', '=', self.id), ('is_visit', '=', True)])
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Offline visits'),
            'view_mode': 'tree,form',
            'res_model': 'calendar.event',
            'domain': [('id', 'in', visits.ids)],
            'target': 'current',
            'context': {'default_opportunity_id': self.id, 'default_is_visit': True,
                        'form_view_ref': 'education.calendar_event_call_vist_form'}
        }

        return res
