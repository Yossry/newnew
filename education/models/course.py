from odoo import models, fields, _, api, tools
from datetime import datetime


class Course(models.Model):
    _name = 'course'
    _description = 'Course'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin']
    name = fields.Char(string='Course', translate=True, track_visibility='onchange')
    event_ids = fields.One2many('event.event', 'course_id', string="Events")
    nb_sessions = fields.Integer(string='Nb Sessions', compute="_compute_nb_sessions", readonly=True)
    meta_key_words = fields.Text(string='Meta Keywords')
    program_id = fields.Many2one('program', string='Program', required="1", track_visibility='onchange')
    active = fields.Boolean(string='Active', track_visibility='onchange', default=True)
    image = fields.Binary(string='Image')
    description = fields.Char(string='Description', translate=True)
    requirements = fields.Char(string='Requirements', translate=True)
    subject_area = fields.Char(string='Subject Area', translate=True)
    language_id = fields.Many2one('res.lang', string='Language', track_visibility='onchange')
    average_attendance = fields.Float('Average Attendance')
    hide_from_website = fields.Boolean('Hide From Website')
    video_link = fields.Char('Video Exam Link')
    type_id = fields.Many2one('event.type', string="Type", track_visibility='onchange')
    instructor_count = fields.Integer(string="Instructors", compute="_compute_count_instructors")
    study_format = fields.Selection(related='type_id.study_format')
    company_prices = fields.One2many(
        'company.price',
        'course_id',
        string="Company Prices",
        track_visibility='onchange',
        copy=True
    )
    region_prices = fields.One2many(
        'company.price',
        'course_region_id',
        string="Region Prices",
        track_visibility='onchange',
        copy=True
    )
    region_ids = fields.Many2many('res.company', string="Regions", compute="_compute_regions", store=True)
    topic_ids = fields.One2many('course.topic', 'course_id', track_visibility='onchange', copy=True)
    course_mail_ids = fields.One2many('course.mail', 'course_id', track_visibility='onchange')
    done = fields.Boolean('Sent')
    is_online = fields.Boolean('Online')

    @api.depends('region_prices')
    def _compute_regions(self):
        for record in self:
            regions = []
            for price_line in record.region_prices:
                regions.append(price_line.company_id.id)
            if (regions):
                record.region_ids = [(6, 0, regions)]
            else:
                record.region_ids = [(5, 0, 0)]

    @api.onchange('type_id')
    def on_change_type(self):
        self.update({'course_mail_ids': [(5, 0, 0)]})
        if self.type_id:
            if self.type_id.event_type_mail_ids and self.type_id.use_mail_schedule:
                mails = self.type_id.event_type_mail_ids
                for mail in mails:
                    self.update({
                        'course_mail_ids': [(0, 0, {
                            'notification_type': mail.notification_type,
                            'interval_unit': mail.interval_unit,
                            'interval_type': mail.interval_type,
                            'template_id': mail.template_id.id})]
                    })

    def generate_price(self):
        regionIds = []
        self.region_ids = False
        date = datetime.now().strftime('%Y-%m-%d')
        companyPrices = self.company_prices
        self.env['company.price'].search([('course_region_id', '=', self.id)]).unlink()
        for companyPrice in companyPrices:
            if companyPrice.company_id.region_ids:
                for region in companyPrice.company_id.region_ids:
                    taxes = []
                    for tax in companyPrice.tax_ids:
                        related_tax = self.env['account.tax'].search([('company_id', '=', region.id)], limit=1)
                        if not related_tax:
                            related_tax = self.env['account.tax'].search([('company_id', '=', region.parent_id.id)],
                                                                         limit=1)
                        if related_tax:
                            taxes.append(related_tax.id)

                    regionPrice = self.env['company.price'].create({
                        'company_id': region.id,
                        'tax_ids': [(6, False, taxes)],
                        'course_region_id': self.id
                    })

                    for ticketPrice in companyPrice.ticket_ids:
                        mappedItems = []
                        company_price = self.env.ref('base.USD')._convert(ticketPrice.price,
                                                                          region.main_pricelist_id.currency_id,
                                                                          companyPrice.company_id, date)
                        for product in ticketPrice.mapped_item_ids:
                            mappedItems.append(product.id)

                        self.env['course.ticket.price'].create({
                            'company_id': region.id,
                            'ticket_id': regionPrice.id,
                            'deadline': ticketPrice.deadline,
                            # 'tax_ids': [(6, False, taxes)],
                            'mapped_item_ids': [(6, False, mappedItems)],
                            'price': ticketPrice.price,
                            # 'local_price': company_price,
                            'domain': ticketPrice.domain,
                            'name': ticketPrice.name
                        })
            else:
                taxes = []
                for tax in companyPrice.tax_ids:
                    taxes.append(tax.id)
                regionPrice = self.env['company.price'].create({
                    'company_id': companyPrice.company_id.id,
                    'tax_ids': [(6, False, taxes)],
                    'course_region_id': self.id
                })

                for ticketPrice in companyPrice.ticket_ids:
                    mappedItems = []
                    company_price = self.env.ref('base.USD')._convert(ticketPrice.price,
                                                                      companyPrice.company_id.currency_id,
                                                                      companyPrice.company_id, date)
                    for product in ticketPrice.mapped_item_ids:
                        mappedItems.append(product.id)

                    self.env['course.ticket.price'].create({
                        'company_id': companyPrice.company_id.id,
                        'ticket_id': regionPrice.id,
                        'deadline': ticketPrice.deadline,
                        'tax_ids': [(6, False, taxes)],
                        'mapped_item_ids': [(6, False, mappedItems)],
                        'price': company_price,
                        'domain': ticketPrice.domain,
                        'name': ticketPrice.name
                    })

    def action_view_instructors(self):
        return {
            "name": _("Instructors"),
            "type": 'ir.actions.act_window',
            "res_model": 'hr.employee',
            "view_mode": "tree,form",
            "domain": [('course_ids', 'in', self.id)]
        }

    def _compute_count_instructors(self):
        for record in self:
            contracts = self.env['hr.employee'].search([('course_ids', 'in', self.id)])
            record['instructor_count'] = len(contracts)

    def _compute_nb_sessions(self):
        for record in self:
            nbSessions = 0
            for topic in record.topic_ids:
                nbSessions = nbSessions + topic.nb_sessions
            record['nb_sessions'] = nbSessions
