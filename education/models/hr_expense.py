from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError

class Expenses(models.Model):
    _inherit = "hr.expense"
    event_id = fields.Many2one('event.event','Event')
    term_id = fields.Many2one('term',string='Term')
