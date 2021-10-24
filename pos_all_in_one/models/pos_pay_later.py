# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
from odoo.exceptions import Warning
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import random
import psycopg2
import base64
from odoo.http import request
from functools import partial
from odoo.tools import float_is_zero

from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import logging
from collections import defaultdict
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)



class POSConfigInherit(models.Model):
	_inherit = 'pos.config'
	
	allow_partical_payment = fields.Boolean('Allow Partial Payment')
	partial_product_id = fields.Many2one("product.product",string="Partial Payment Product", domain = [('type', '=', 'service'),('available_in_pos', '=', True)])

	@api.model
	def create(self, vals):
		res=super(POSConfigInherit, self).create(vals)
		product=self.env['product.product'].browse(vals['partial_product_id'])

		if vals['allow_partical_payment']==True:
			if product:
				if product.available_in_pos != True:
					raise ValidationError(_('Please enable available in POS for the Partial Payment Product'))

				if product.taxes_id:
					raise ValidationError(_('You are not allowed to add Customer Taxes in the Partial Payment Product'))

		return res


	def write(self, vals):
		res=super(POSConfigInherit, self).write(vals)
		for rec in self:
			if rec.allow_partical_payment == True:
				if rec.partial_product_id.available_in_pos != True:
					raise ValidationError(_('Please enable available in POS for the Partial Payment Product'))

				if rec.partial_product_id.taxes_id:
					raise ValidationError(_('You are not allowed to add Customer Taxes in the Partial Payment Product'))

		return res

class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	def _default_session(self):
		return self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)


	is_partial = fields.Boolean('Is Partial Payment')
	amount_due = fields.Float("Amount Due",compute="get_amount_due")

	@api.depends('amount_total','amount_paid')
	def get_amount_due(self):
		for order in self :
			if order.amount_paid - order.amount_total >= 0:
				order.amount_due = 0
				order.is_partial = False
			else:
				order.amount_due = order.amount_total - order.amount_paid
				
	def write(self, vals):
		for order in self:
			if order.name == '/' and order.is_partial :
				vals['name'] = order.config_id.sequence_id._next()
		return super(PosOrderInherit, self).write(vals)

	def _is_pos_order_paid(self):
		return float_is_zero(self._get_rounded_amount(self.amount_total) - self.amount_paid, precision_rounding=self.currency_id.rounding)

	def action_pos_order_paid(self):
		self.ensure_one()
		if not self.is_partial:
			return super(PosOrderInherit, self).action_pos_order_paid()
		if self.is_partial:
			if not self.config_id.cash_rounding:
				total = self.amount_total
			else:
				total = float_round(self.amount_total, precision_rounding=self.config_id.rounding_method.rounding, rounding_method=self.config_id.rounding_method.rounding_method)
			if  self._is_pos_order_paid():
				self.write({'state': 'paid'})
				if self.picking_ids:
					return True
				else :
					return self._create_order_picking()
			else:
				if not self.picking_ids :
					return self._create_order_picking()
				else:
					return False

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrderInherit, self)._order_fields(ui_order)
		process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
		if 'is_partial' in ui_order:
			res['is_partial'] = ui_order.get('is_partial',False) 
			res['amount_due'] = ui_order.get('amount_due',0.0) 
		return res

	@api.model
	def _process_order(self, order, draft, existing_order):
		"""Create or update an pos.order from a given dictionary.

		:param dict order: dictionary representing the order.
		:param bool draft: Indicate that the pos_order is not validated yet.
		:param existing_order: order to be updated or False.
		:type existing_order: pos.order.
		:returns: id of created/updated pos.order
		:rtype: int
		"""
		order = order['data']
		is_partial = order.get('is_partial')
		is_draft_order = order.get('is_draft_order')
		is_paying_partial = order.get('is_paying_partial')

		pos_session = self.env['pos.session'].browse(order['pos_session_id'])
		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
			order['pos_session_id'] = self._get_valid_session(order).id

		pos_order = False
		if is_paying_partial:
			pos_order = self.search([('pos_reference', '=', order.get('name'))])
		else:
			if not existing_order:
				pos_order = self.create(self._order_fields(order))
			else:
				pos_order = existing_order
				pos_order.lines.unlink()
				order['user_id'] = pos_order.user_id.id
				pos_order.write(self._order_fields(order))

		coupon_id = order.get('coupon_id', False)
		if coupon_id:
			coup_max_amount = order.get('coup_maxamount',False)
			pos_order.write({'coupon_id':  coupon_id})
			pos_order.coupon_id.update({
				'coupon_count': pos_order.coupon_id.coupon_count + 1,
				'max_amount': coup_max_amount
			})

		if pos_order.config_id.discount_type == 'percentage':
			pos_order.update({'discount_type': "Percentage"})
			pos_order.lines.update({'discount_line_type': "Percentage"})
		if pos_order.config_id.discount_type == 'fixed':
			pos_order.update({'discount_type': "Fixed"})
			pos_order.lines.update({'discount_line_type': "Fixed"})

		pos_order = pos_order.with_company(pos_order.company_id)
		self = self.with_company(pos_order.company_id)
		self._process_payment_lines(order, pos_order, pos_session, draft)
		if not draft:
			try:
				pos_order.action_pos_order_paid()
			except psycopg2.DatabaseError:
				# do not hide transactional errors, the order(s) won't be saved!
				raise
			except Exception as e:
				_logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

		pos_order._create_order_picking()


		create_invoice = False
		if order.get('to_invoice' , False) and pos_order.state == 'paid':
			if pos_order.amount_total > 0:	
				create_invoice = True
			elif pos_order.amount_total < 0:
				if pos_order.session_id.config_id.credit_note == "create_note":
					create_invoice = True
		if create_invoice:
			pos_order.action_pos_order_invoice()
			if pos_order.discount_type and pos_order.discount_type == "Fixed":
				invoice = pos_order.account_move
				for line in invoice.invoice_line_ids : 
					pos_line = line.pos_order_line_id
					if pos_line and pos_line.discount_line_type == "Fixed" and pos_line.discount != 100:
						line.write({'price_unit':pos_line.price_unit})
					else:
						line.write({'price_unit':pos_line.price_unit + line.discount,
						'discount': pos_line.discount })
					
		return pos_order.id


	def _process_payment_lines(self, pos_order, order, pos_session, draft):
		"""Create account.bank.statement.lines from the dictionary given to the parent function.

		If the payment_line is an updated version of an existing one, the existing payment_line will first be
		removed before making a new one.
		:param pos_order: dictionary representing the order.
		:type pos_order: dict.
		:param order: Order object the payment lines should belong to.
		:type order: pos.order
		:param pos_session: PoS session the order was created in.
		:type pos_session: pos.session
		:param draft: Indicate that the pos_order is not validated yet.
		:type draft: bool.
		"""
		prec_acc = order.pricelist_id.currency_id.decimal_places
		order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
		is_paying_partial = pos_order.get('is_paying_partial')
		is_partial = pos_order.get('is_partial')
		if not is_paying_partial or not is_partial:
			order_bank_statement_lines.unlink()
		for payments in pos_order['statement_ids']:
			if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
				order.add_payment(self._payment_fields(order, payments[2]))

		order.amount_paid = sum(order.payment_ids.mapped('amount'))
		if order.amount_paid >= order.amount_total :
			order.write({
				'is_partial' : False,
			})

		if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
			if not cash_payment_method:
				raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
				
			return_amount = 0
			if pos_order['currency_amount'] and  pos_order['currency_symbol']:
				session_currency = order.pricelist_id.currency_id
				ordr_currency = self.env['res.currency'].search([('name','=',pos_order['currency_name'])])
				if ordr_currency  != session_currency:
					return_amount = session_currency._convert(pos_order['amount_return'], ordr_currency, order.company_id, order.date_order)
			

			return_payment_vals = {
				'name': _('return'),
				'pos_order_id': order.id,
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Date.context_today(self),
				'payment_method_id': cash_payment_method.id,
				'account_currency': -return_amount or 0.0,
				'currency' : pos_order['currency_name'] or '',
			}
			order.add_payment(return_payment_vals)

class PosSessionInherit(models.Model):
	_inherit = 'pos.session'

	@api.model
	def create(self, vals):
		res = super(PosSessionInherit, self).create(vals)
		orders = self.env['pos.order'].search([('user_id', '=', request.env.uid),
			('state', '=', 'draft'),('session_id.state', '=', 'closed')])
		orders.write({'session_id': res.id})
		return res

	def _check_if_no_draft_orders(self):
		draft_orders = self.order_ids.filtered(lambda order: order.state == 'draft')
		do = []
		for i in draft_orders:
			if not i.is_partial :
				do.append(i.name)
		if do:
			raise UserError(_(
					'There are still orders in draft state in the session. '
					'Pay or cancel the following orders to validate the session:\n%s'
				) % ', '.join(do)
			)
		return True

	def _accumulate_amounts(self, data):
		# Accumulate the amounts for each accounting lines group
		# Each dict maps `key` -> `amounts`, where `key` is the group key.
		# E.g. `combine_receivables` is derived from pos.payment records
		# in the self.order_ids with group key of the `payment_method_id`
		# field of the pos.payment record.
		amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
		tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'base_amount_converted': 0.0}
		split_receivables = defaultdict(amounts)
		split_receivables_cash = defaultdict(amounts)
		combine_receivables = defaultdict(amounts)
		combine_receivables_cash = defaultdict(amounts)
		invoice_receivables = defaultdict(amounts)
		sales = defaultdict(amounts)
		taxes = defaultdict(tax_amounts)
		stock_expense = defaultdict(amounts)
		stock_return = defaultdict(amounts)
		stock_output = defaultdict(amounts)
		rounding_difference = {'amount': 0.0, 'amount_converted': 0.0}
		# Track the receivable lines of the invoiced orders' account moves for reconciliation
		# These receivable lines are reconciled to the corresponding invoice receivable lines
		# of this session's move_id.
		order_account_move_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
		rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
		order_ids = self.order_ids.filtered(lambda order: order.is_partial == False)
		for order in order_ids:
			# Combine pos receivable lines
			# Separate cash payments for cash reconciliation later.
			for payment in order.payment_ids:
				amount, date = payment.amount, payment.payment_date
				if payment.payment_method_id.split_transactions:
					if payment.payment_method_id.is_cash_count:
						split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment], {'amount': amount}, date)
					else:
						split_receivables[payment] = self._update_amounts(split_receivables[payment], {'amount': amount}, date)
				else:
					key = payment.payment_method_id
					if payment.payment_method_id.is_cash_count:
						combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key], {'amount': amount}, date)
					else:
						combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount}, date)

			if order.is_invoiced:
				# Combine invoice receivable lines
				key = order.partner_id
				if self.config_id.cash_rounding:
					invoice_receivables[key] = self._update_amounts(invoice_receivables[key], {'amount': order.amount_paid}, order.date_order)
				else:
					invoice_receivables[key] = self._update_amounts(invoice_receivables[key], {'amount': order.amount_total}, order.date_order)
				# side loop to gather receivable lines by account for reconciliation
				for move_line in order.account_move.line_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
					order_account_move_receivable_lines[move_line.account_id.id] |= move_line
			else:
				order_taxes = defaultdict(tax_amounts)
				for order_line in order.lines:
					line = self._prepare_line(order_line)
					# Combine sales/refund lines
					sale_key = (
						# account
						line['income_account_id'],
						# sign
						-1 if line['amount'] < 0 else 1,
						# for taxes
						tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),
						line['base_tags'],
					)
					sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']}, line['date_order'])
					# Combine tax lines
					for tax in line['taxes']:
						tax_key = (tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
						order_taxes[tax_key] = self._update_amounts(
							order_taxes[tax_key],
							{'amount': tax['amount'], 'base_amount': tax['base']},
							tax['date_order'],
							round=not rounded_globally
						)
				for tax_key, amounts in order_taxes.items():
					if rounded_globally:
						amounts = self._round_amounts(amounts)
					for amount_key, amount in amounts.items():
						taxes[tax_key][amount_key] += amount

				if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
					# Combine stock lines
					stock_moves = self.env['stock.move'].sudo().search([
						('picking_id', 'in', order.picking_ids.ids),
						('company_id.anglo_saxon_accounting', '=', True),
						('product_id.categ_id.property_valuation', '=', 'real_time')
					])
					for move in stock_moves:
						exp_key = move.product_id._get_product_accounts()['expense']
						out_key = move.product_id.categ_id.property_stock_account_output_categ_id
						amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
						stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
						if move.location_id.usage == 'customer':
							stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
						else:
							stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)

				if self.config_id.cash_rounding:
					diff = order.amount_paid - order.amount_total
					rounding_difference = self._update_amounts(rounding_difference, {'amount': diff}, order.date_order)

				# Increasing current partner's customer_rank
				partners = (order.partner_id | order.partner_id.commercial_partner_id)
				partners._increase_rank('customer_rank')

		if self.company_id.anglo_saxon_accounting:
			global_session_pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
			if global_session_pickings:
				stock_moves = self.env['stock.move'].sudo().search([
					('picking_id', 'in', global_session_pickings.ids),
					('company_id.anglo_saxon_accounting', '=', True),
					('product_id.categ_id.property_valuation', '=', 'real_time'),
				])
				for move in stock_moves:
					exp_key = move.product_id._get_product_accounts()['expense']
					out_key = move.product_id.categ_id.property_stock_account_output_categ_id
					amount = -sum(move.stock_valuation_layer_ids.mapped('value'))
					stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date)
					if move.location_id.usage == 'customer':
						stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount}, move.picking_id.date)
					else:
						stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date)
		MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)

		data.update({
			'taxes':                               taxes,
			'sales':                               sales,
			'stock_expense':                       stock_expense,
			'split_receivables':                   split_receivables,
			'combine_receivables':                 combine_receivables,
			'split_receivables_cash':              split_receivables_cash,
			'combine_receivables_cash':            combine_receivables_cash,
			'invoice_receivables':                 invoice_receivables,
			'stock_return':                        stock_return,
			'stock_output':                        stock_output,
			'order_account_move_receivable_lines': order_account_move_receivable_lines,
			'rounding_difference':                 rounding_difference,
			'MoveLine':                            MoveLine
		})
		return data