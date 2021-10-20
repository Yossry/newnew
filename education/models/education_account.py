from odoo import models, fields


class EducationAccount(models.Model):
    _name = 'education.account'
    partner_id = fields.Many2one('res.partner')
    major_id = fields.Many2one('majors',string="Major")
    level_id = fields.Many2one('education.level','Highest Education Level')
    university_id = fields.Many2one('university',string="University/Institute")
