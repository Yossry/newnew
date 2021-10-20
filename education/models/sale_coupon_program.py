

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class SaleCouponProgram(models.Model):
	_inherit = 'coupon.program'
	rule_events_domain = fields.Char('Based On Events',default=[['date_begin', '!=', False]])

	rule_sales_domain = fields.Char('Based On Sales',default=[['id', '=', False]])

	def _is_valid_event(self, event):
		if self.rule_events_domain:
			domain = safe_eval(self.rule_events_domain) + [('id', '=', event.id)]
			return bool(self.env['event.event'].search_count(domain))
		else:
			return True

	def _get_valid_events(self, events):
		if self.rule_events_domain:
			domain = safe_eval(self.rule_events_domain) + [('id', 'in', events.ids)]
			return self.env['event.event'].search(domain)

		return events


	def _is_valid_sale(self, sale):
		if self.rule_sales_domain:
			domain = safe_eval(self.rule_sales_domain) + [('id', '=', sale.id)]
			return bool(self.env['sale.order.line'].search_count(domain))
		else:
			return True

	def _get_valid_sales(self, sales):
		if self.rule_sales_domain:
			domain = safe_eval(self.rule_sales_domain) + [('id', 'in', sales.ids)]
			return self.env['sale.order.line'].search(domain)

		return sales

	def _filter_programs_on_events(self, order):
		product_valid_programs = self._filter_programs_on_products(order)
		order_lines = order.order_line.filtered(lambda line: line.event_id) - order._get_reward_lines()
		events = order_lines.mapped('event_id')
		events_qties = dict.fromkeys(events, 0)
		for line in order_lines:
			events_qties[line.event_id] += line.product_uom_qty

		valid_programs = self.filtered(lambda program: not program.rule_events_domain)
		for program in self - valid_programs:
			valid_events = program._get_valid_events(events)
			ordered_rule_events_qty = sum(events_qties[event] for event in valid_events)
			#if program.promo_applicability == 'on_current_order' and \
			   #program._is_valid_product(program.reward_product_id) and program.reward_type == 'product':
			   	#ordered_rule_events_qty -= program.reward_product_quantity

			if ordered_rule_events_qty >= program.rule_min_quantity:
				valid_programs |= program


		return valid_programs + product_valid_programs


	def _filter_programs_on_sales(self, order):
		event_valid_programs = self._filter_programs_on_events(order)
		order_lines = order.order_line - order._get_reward_lines()

		sales_qties = dict.fromkeys(order_lines, 0)
		for line in order_lines:
			sales_qties[line] += line.product_uom_qty

		#raise UserError(str(sales_qties))

		valid_programs = self.filtered(lambda program: not program.rule_sales_domain)
		for program in self - valid_programs:
			valid_sales = program._get_valid_sales(order_lines)

			ordered_rule_sales_qty = sum(sales_qties[line] for line in valid_sales)
			if ordered_rule_sales_qty >= program.rule_min_quantity:
				valid_programs |= program


		#raise UserError(valid_programs)
		return valid_programs + event_valid_programs

	@api.model
	def _filter_programs_from_common_rules(self, order, next_order=False):
		programs = self
		if not next_order:
			programs = programs and programs._filter_on_mimimum_amount(order)

		programs = programs and programs._filter_on_validity_dates(order)
		programs = programs and programs._filter_unexpired_programs(order)
		programs = programs and programs._filter_programs_on_partners(order)

		if not next_order:
			programs = programs and programs._filter_programs_on_sales(order)






		programs_curr_order = programs.filtered(lambda p: p.promo_applicability == 'on_current_order')

		programs = programs.filtered(lambda p: p.promo_applicability == 'on_next_order')
		if programs_curr_order:
			programs += programs_curr_order
			#raise UserError(str(programs) + ' test')

		#raise UserError(programs)
		return programs

	def _check_promo_code(self, order, coupon_code):
		message = {}
		applicable_programs = order._get_applicable_programs()
		if self.maximum_use_number != 0 and self.order_count >= self.maximum_use_number:
			message = {'error': _('Promo code %s has been expired.') % (coupon_code)}

		elif not self._filter_on_mimimum_amount(order):
			message = {'error': _('A minimum of %s %s should be purchased to get the reward') % (self.rule_minimum_amount, self.currency_id.name)}

		elif self.promo_code and self.promo_code == order.promo_code:
			message = {'error': _('The promo code is already applied on this order')}

		elif not self.promo_code and self in order.no_code_promo_program_ids:
			message = {'error': _('The promotional offer is already applied on this order')}

		elif not self.active:
			message = {'error': _('Promo code is invalid')}

		elif self.rule_date_from and self.rule_date_from > order.date_order or self.rule_date_to and order.date_order > self.rule_date_to:
			message = {'error': _('Promo code is expired')}

		elif order.promo_code and self.promo_code_usage == 'code_needed':
			message = {'error': _('Promotionals codes are not cumulative.')}

		elif self._is_global_discount_program() and order._is_global_discount_already_applied():
			message = {'error': _('Global discounts are not cumulative.')}

		elif self.promo_applicability == 'on_current_order' and self.reward_type == 'product' and not order._is_reward_in_order_lines(self):
			message = {'error': _('The reward products should be in the sales order lines to apply the discount.')}

		elif not self._is_valid_partner(order.partner_id):
			message = {'error': _("The customer doesn't have access to this reward.")}

		elif not self._filter_programs_on_events(order):
			message = {'error': _("You don't have the required product quantities on your sales order. If the reward is same product quantity, please make sure that all the products are recorded on the sales order (Example: You need to have 3 T-shirts on your sales order if the promotion is 'Buy 2, Get 1 Free'.")}

		else:
			if self not in applicable_programs and self.promo_applicability == 'on_current_order':
				message = {'error': _('At least one of the required conditions is not met to get the reward!')}

		return message
	
	def _compute_program_amount(self, field, currency_to):
		try:
			self.ensure_one()
			return self.currency_id._convert(getattr(self, field), currency_to, self.company_id, fields.Date.today())

		except:
			raise UserError('Please set a company for promotion ' + self.name)

