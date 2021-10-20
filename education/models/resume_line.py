
from odoo import models, fields


class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'
    resume_id = fields.Many2one('res.partner')
    obtained_via = fields.Selection([('morgan', 'Morgan'),('competitor', 'Competitor'),('supplier', 'Directly with supplier')],string='Obtained Via')
    study_format = fields.Selection([('liveclass', 'Live Class'),('liveonline', 'Live Online'),('self', 'Self Study')],string='Study Format')
    language = fields.Many2one('res.lang','Language')
    lang_type = fields.Selection([('basic', 'Basic'),('intermediate', 'Intermediate'),('profficient', 'Profficient')],string='Language Type')
    program_id = fields.Many2one('program','Program')
    course_ids = fields.Many2many('course',string='Courses')
    topic_ids = fields.Many2many('course.topic',string='Topics')
    education = fields.Selection([('phd', 'PHD'),('ms', 'MS'),('mba', 'MBA'),('ba','BA'),('other','Other')],string='Education')
    major_id = fields.Many2one('instructor.major','Major')
    unversity_id = fields.Many2one('university','University')
    company = fields.Char(string='Company')
    job_title = fields.Char(string='Job Title')
    years_of_experience = fields.Char('Years of experience')
    skill_type = fields.Selection(related='line_type_id.skill_type',string='SKill Type')