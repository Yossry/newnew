from odoo import models, fields,api
from odoo.exceptions import UserError


class PayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    date = fields.Date('Date')
    name = fields.Char(string='Description',store=True,readonly=False,related=False)
    contract_id = fields.Many2one('hr.contract','Contract',store=True,related=False)
