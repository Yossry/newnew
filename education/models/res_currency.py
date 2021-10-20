from odoo import models, fields, api

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    companies_ids = fields.Many2many('res.company', string="Companies", compute='compute_companies', store=True)
    
    def compute_companies(self):
        for record in self:
            ids = []
            pricelists = self.env['product.pricelist'].search([('currency_id', '=', record.id), ('company_id', '!=', False)])
            for pricelist in pricelists:
                ids.append(pricelist.company_id.id)
            record.companies_ids = [(6, 0, ids)]
            return [(6, 0, ids)]