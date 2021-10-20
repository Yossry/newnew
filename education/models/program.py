from odoo import models, fields, api, _


class Program(models.Model):
    _name = 'program'
    _description = 'Program'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'format.address.mixin']
    name = fields.Char(string='Program', translate=True)
    course_ids = fields.One2many('course', 'program_id', string='Courses')
    description = fields.Char('Description')
    enrollment = fields.Text('Enrollment Agreement')
    company_id = fields.Many2one('res.company', string="Region")
    courses_count = fields.Integer(string="Courses", compute="_compute_count_courses", readonly=True)

    def action_view_courses(self):
        return {
            "name": _("Courses"),
            "type": 'ir.actions.act_window',
            "res_model": 'course',
            "view_mode": "tree,form",
            "domain": [('program_id', '=', self.id)]
        }

    def _compute_count_courses(self):
        for record in self:
            contracts = self.env['course'].search([('program_id', '=', self.id)])
            record['courses_count'] = len(contracts)
