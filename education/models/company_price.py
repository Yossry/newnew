from odoo import models, fields, api
from datetime import datetime


class CompanyPrice(models.Model):
    _name = 'company.price'
    _description = 'Course Pricing/Company'
    ticket_ids = fields.One2many('course.ticket.price', 'ticket_id')
    course_id = fields.Many2one('course')
    course_region_id = fields.Many2one('course')
    product_tmpl_id = fields.Many2one('product.template', 'Product')
    product_tmpl_region_id = fields.Many2one('product.template', 'Product')
    name = fields.Char('Ticket Name')
    company_id = fields.Many2one(
        'res.company',
        string="Company"
    )
    tax_ids = fields.Many2many('account.tax', domain="[('company_id','=',company_id)]")
    deadline = fields.Integer('Sales End')
    price = fields.Float('Price')
    ticket_id = fields.Many2one('company.price')
    topic_id = fields.Many2one('course.topic')
    is_company = fields.Boolean('Is Company')
    local_price = fields.Float('Local Price', compute="_compute_local_price", store=False)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.USD').id)
    company_currency = fields.Many2one('res.currency', related='company_id.currency_id', string='Local Currency',
                                       store=True)

    @api.depends('price')
    def _compute_local_price(self):
        date = datetime.now().strftime('%Y-%m-%d')
        for company_price in self:
            if (company_price.company_id):
                company_price.local_price = self.env.ref('base.USD')._convert(company_price.price,
                                                                              company_price.company_currency,
                                                                              company_price.company_id, date)
            else:
                company_price.local_price = 0

    @api.onchange('company_id')
    def _onchange_company(self):
        self._compute_local_price()
        val = {}
        domain = {}
        value = {}
        taxes = []
        taxes_parent = []
        available_taxes = []
        if (self.company_id):
            taxes = self.env['account.tax'].search(
                [
                    ('company_id', '=', self.company_id.id),
                    ('type_tax_use', '=', 'sale')
                ])
            for tax in taxes:
                available_taxes.append(tax.id)
            if (self.company_id.parent_id):
                taxes_parent = self.env['account.tax'].search(
                    [('company_id', '=', self.company_id.parent_id.id),
                     ('type_tax_use', '=', 'sale')])
                for tax in taxes_parent:
                    available_taxes.append(tax.id)
        domain['tax_ids'] = [('id', 'in', available_taxes)]
        val['domain'] = domain
        val['value'] = {'tax_ids': False}
        return val
