from odoo import models, fields, api, _
from datetime import datetime

class CourseTicketPrice(models.Model):
    _name ='course.ticket.price'
    _description = 'Course Ticket Price'
    name = fields.Char('Ticket Name')
    company_id = fields.Many2one('res.company', string="Region", domain="[('is_region', '=', True)]")
    tax_ids = fields.Many2many('account.tax', widget='many2many_tags')
    deadline = fields.Integer('Sales End (Before event start date)')
    price = fields.Float('Price')
    ticket_id = fields.Many2one('company.price')
    mapped_item_ids = fields.Many2many('product.template', string="Mapped Items")
    domain = fields.Char('Domain')
    currency_id = fields.Many2one('res.currency',default=lambda self: self.env.ref('base.USD').id)
    company_currency = fields.Many2one('res.currency',related='company_id.currency_id',string='Local Currency',store=True)
    is_region = fields.Boolean(related='company_id.is_region')
    local_price = fields.Float('Local Price', compute="_compute_local_price", store=False)
    
    @api.depends('price')
    def _compute_local_price(self):
        date = datetime.now().strftime('%Y-%m-%d')
        for course_ticket in self:
            if(course_ticket.company_id):
                course_ticket.local_price = self.env.ref('base.USD')._convert(course_ticket.price,course_ticket.company_currency,course_ticket.company_id,date)
            else:
                course_ticket.local_price = 0