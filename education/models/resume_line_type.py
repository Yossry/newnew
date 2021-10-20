
from odoo import models, fields


class ResumeLineType(models.Model):
    _inherit = 'hr.resume.line.type'
    skill_type = fields.Selection([('certification', 'Certification'),('language', 'Language'),('specialization', 'Specialization'),('education', 'Education'),('experience','Experience')],string='SKill Type')

