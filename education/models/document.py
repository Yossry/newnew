from odoo import models, fields

class Document(models.Model):
    _inherit = 'documents.document'
    partner_id = fields.Many2one('res.partner', string='Partner')
    program_attachment_id = fields.Many2one('program.attachment')
    company_id = fields.Many2one('res.company',string="Region")
    employee_id = fields.Many2one('hr.employee',string='Instructor',domain="[('is_instructor','=',True)]")
    attachment_id = fields.Many2one('program.attachment')
   

