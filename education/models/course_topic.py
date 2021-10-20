from odoo import models, fields


class CourseTopic(models.Model):
    _name = 'course.topic'
    name = fields.Char('Name')
    nb_sessions = fields.Integer('Nb Sessions')
    course_id = fields.Many2one('course')
    company_price_ids = fields.One2many('company.topic.price', 'topic_id', string="Company Prices")
    region_price_ids = fields.One2many('company.topic.price', 'topic_region_id', string="Region Prices")
    sequence = fields.Integer('Priority')

    def generate_price(self):
        companyTopicPrices = self.company_price_ids
        self.env['company.topic.price'].search([('topic_region_id', '=', self.id)]).unlink()
        for companyTopicPrice in companyTopicPrices:
            if (companyTopicPrice.company_id.region_ids):
                for region in companyTopicPrice.company_id.region_ids:
                    taxes = []
                    for tax in companyTopicPrice.tax_ids:
                        taxes.append(tax.id)
                    regionPrice = self.env['company.topic.price'].create({
                        'company_id': region.id,
                        'tax_ids': [(6, False, taxes)],
                        'topic_region_id': self.id,
                        'price': companyTopicPrice.price
                    })
            else:
                regionPrice = self.env['company.topic.price'].create({
                    'company_id': companyTopicPrice.company_id.id,
                    'tax_ids': [(6, False, taxes)],
                    'topic_region_id': self.id,
                    'price': companyTopicPrice.price
                })
