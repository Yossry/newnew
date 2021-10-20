

from odoo import models, fields


class AccountTax(models.Model):
	_inherit = 'account.tax'
	company_id = fields.Many2one(string="Region", domain="[('is_region', '=', True)]",default=lambda self: self._get_child_companies())
	name = fields.Char('Tax Name')
	description = fields.Char('Label On Invoices')
	active = fields.Boolean('Active')
	type_tax_use = fields.Selection([('sale', 'Sales'),('purchase', 'Purchase'),
            ('none', 'None')] , string='Tax Scope')

	parent_company_id = fields.Many2one(related='company_id.parent_id')

	def _get_child_companies(self):
		company = self.env.company
		child_company = self.env['res.company'].search([('parent_id','=',company.id)],limit=1)
		if child_company:
			return child_company.id
		else:
			return company.id