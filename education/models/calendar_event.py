from odoo import models, fields, _, api

class Calendar(models.Model):
    _inherit = 'calendar.event'
    opportunity_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type', 'in', ['opportunity','lead'])]")
    is_call = fields.Boolean()
    is_visit = fields.Boolean()
    name = fields.Char(string='Subject')