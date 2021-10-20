from odoo import models, fields


class EmployeeSkill(models.Model):
    _inherit = 'hr.employee.skill'
    partner_id = fields.Many2one('res.partner')
