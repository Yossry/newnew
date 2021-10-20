
from odoo import models, fields


class InstructorMajor(models.Model):
    _name = 'instructor.major'
    name = fields.Char('Major')