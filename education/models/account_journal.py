from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"
    company_id = fields.Many2one('res.company')
    name = fields.Char('Journal Name')
    bank_acc_number = fields.Char('Account Number')
    swift_code = fields.Char('Swift Code')
    iban = fields.Char('Iban')