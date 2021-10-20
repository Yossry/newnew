from odoo import models, fields, api
from datetime import datetime


class CompanyTopicPrice(models.Model):
    _name = 'company.topic.price'
    _description = 'Topic Pricing/Company'
    price = fields.Float('Price')
    course_region_id = fields.Many2one('course')
    company_id = fields.Many2one(
        'res.company',
        string="Company"
    )
    tax_ids = fields.Many2many('account.tax')
    topic_id = fields.Many2one('course.topic')
    topic_region_id = fields.Many2one('course.topic')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.ref('base.USD').id)
    company_currency = fields.Many2one(related='company_id.currency_id', string='Company Currency', store=True)
    local_price = fields.Float('Local Price', compute="_compute_local_price", store=False)

    @api.depends('price')
    def _compute_local_price(self):
        date = datetime.now().strftime('%Y-%m-%d')
        for topic in self:
            if (topic.company_id):
                topic.local_price = self.env.ref('base.USD')._convert(topic.price, topic.company_id.currency_id,
                                                                      topic.company_id, date)
            else:
                topic.local_price = 0

    @api.onchange('company_id')
    def _onchange_company(self):
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
