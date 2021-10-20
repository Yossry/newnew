
from odoo import api, models
from odoo.exceptions import UserError


class Payment(models.Model):
	_inherit = "account.payment"

	def post(self):
		#raise UserError('test')
		res = super(Payment, self).post()
		code = 'account.payment'
		ref = False
		name = False
		if(self.payment_type=='inbound'):
			ref = 'RC-'

		elif(self.payment_type=='outbound'):
			ref = 'RF-'

		company_sequence = False
		parent_sequence = False

		if(not self.company_id.document_sequence):
			company_sequence = self.env['ir.sequence'].search([('company_id','=',self.company_id.id),('code','=',code),('prefix','=','RC')],limit=1)
			name = ref + self.company_id.code+'-'+str(company_sequence.number)
			company_sequence.write({'number': company_sequence.number + 1})

		else:
			parent_sequence = self.env['ir.sequence'].search([('company_id','=',self.company_id.parent_id.id),('code','=',code),('prefix','=','RC')],limit=1)
			if(parent_sequence):
				name = ref+self.company_id.parent_id.code+'-'+str(parent_sequence.number)
				parent_sequence.write({'number': parent_sequence.number + 1})

		self.write({'name': name})

		move_id = self.env['account.move.line'].search([('payment_id','=',self.id)],limit=1).move_id
		move_id.write({'name': name, 'company_id': self.company_id.id})

		return res

	@api.onchange('amount', 'currency_id')
	def _onchange_amount(self):
		journal = self.env['account.journal'].search([('company_id','=',self.company_id.id),('type','=','bank')],limit=1)
		if journal:
			self.journal_id = journal.id


	@api.onchange('journal_id')
	def _onchange_journal(self):
		if self.journal_id:
			self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
			# Set default payment method (we consider the first to be the default one)
			payment_methods = self.payment_type == 'outbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
			self.payment_method_id = payment_methods and payment_methods[0] or False
			# Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
			payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'outbound'
			return {
				'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
		return {}


	@api.onchange('currency_id')
	def _onchange_currency(self):
		if self.currency_id and self.journal_id and self.payment_date:
			advance_amount = abs(self._compute_payment_amount(self.currency_id, self.journal_id, self.payment_date))
			self.advance_amount = advance_amount
		else:
			self.advance_amount = 0.0

		if self.journal_id:  # TODO: only return if currency differ?
			return

		# Set by default the first liquidity journal having this currency if exists.
		domain = [('type', 'in', ('bank', 'cash')),
				  ('currency_id', '=', self.currency_id.id),
				  ('company_id', '=', self.company_id.id), ]
		journal = self.env['account.journal'].search(domain, limit=1)
		if journal:
			return {'value': {'journal_id': journal.id}}

	@api.onchange('payment_type')
	def _onchange_payment_type(self):
		if not self.reconciled_invoice_ids and not self.partner_type:
			if self.payment_type == 'inbound':
				self.partner_type = 'customer'

			elif self.payment_type == 'outbound':
				self.partner_type = 'supplier'

		elif self.payment_type not in ('inbound', 'outbound'):
			self.partner_type = False

		res = self._onchange_journal()
		if not res.get('domain', {}):
			res['domain'] = {}

		jrnl_filters = self._compute_journal_domain_and_types()
		journal_types = jrnl_filters['journal_types']
		journal_types.update(['bank'])
		return res

		