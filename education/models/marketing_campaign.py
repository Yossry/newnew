from odoo import models, fields


class MarketingCampaign(models.Model):
    _inherit = 'marketing.campaign'
    term_id = fields.Many2one('term',string="Term")
    program_ids = fields.Many2many('program',string="Programs")
    course_ids = fields.Many2many('course',string = "Courses")
    budget= fields.Integer(string='Budget')
    spent = fields.Float('Spent',readonly="1")
    tag_ids = fields.Many2many('utm.tag',string = "Tags")
    description = fields.Html('Description')