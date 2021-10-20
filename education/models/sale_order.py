from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import float_is_zero
from itertools import groupby


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    order_line = fields.One2many(
        'sale.order.line',
        'order_id',
        string='Order Lines',
        states={'cancel': [('readonly', True)], 'done': [('readonly', True)], 'locked': [('readonly', True)],
                'sale': [('readonly', True)]},
        copy=True,
        auto_join=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('locked', 'Locked'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Finalized'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    company_id = fields.Many2one(
        'res.company',
        'Region',
        domain="[('is_region','=',True)]",
        required=True,
        index=True,
        default=lambda self: self._get_child_companies(),
        states={'locked': [('readonly', True)], 'sale': [('readonly', True)]})

    partner_id = fields.Many2one(
        'res.partner', string='Account', readonly=True,
        states={'draft': [('readonly', False)]},
        required=True, change_default=True, index=True, tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )
    registration_ids = fields.One2many('event.registration', 'sale_order_id',
                                       string='Attendees', readonly=True)
    event_ids = fields.Many2many('event.event', string='Event',
                                 compute='_compute_event_ids',
                                 readonly=True)

    product_ids = fields.Many2many('product.product', string='Products', store=True)

    amount_discount = fields.Float(string='Total Discount', compute="get_amount_discount")

    event_id = fields.Many2one('event.event')

    product_filter_ids = fields.Char('Product ids', compute="compute_filters", store=True)
    event_filter_ids = fields.Char('Event ids', compute="compute_filters", store=True)

    @api.depends('order_line')
    def compute_filters(self):
        for record in self:
            products = str(self.order_line.mapped('product_id').ids)
            products = products.replace("[", "")
            products = products.replace("]", "")
            products = products.replace(" ", "")

            events = str(self.order_line.mapped('event_id').ids)
            events = events.replace("[", "")
            events = events.replace("]", "")
            events = events.replace(" ", "")

            record['product_filter_ids'] = products
            record['event_filter_ids'] = events

        name = False
        if (record.state == 'draft'):
            name = 'New'

        if (record.state != 'draft' and record.name == 'New'):
            code = 'sale.order'
            ref = 'SO'
            company_sequence = False
            parent_sequence = False

            if (not record.company_id.document_sequence):
                company_sequence = self.env['ir.sequence'].search(
                    [('company_id', '=', record.company_id.id), ('code', '=', code), ('prefix', '=', 'SO')], limit=1)
                name = ref + '-' + record.company_id.code + '-' + str(company_sequence.number)
                company_sequence.write({'number': company_sequence.number + 1})

            else:
                parent_sequence = self.env['ir.sequence'].search(
                    [('company_id', '=', record.company_id.parent_id.id), ('code', '=', code), ('prefix', '=', 'SO')],
                    limit=1)
                if (parent_sequence):
                    name = ref + '-' + record.company_id.parent_id.code + '-' + str(parent_sequence.number)
                    parent_sequence.write({'number': parent_sequence.number + 1})

        record['name'] = name

        return record

    def action_lock(self):

        code = 'sale.order'
        ref = 'SO'
        name = False
        company_sequence = False
        parent_sequence = False

        if (not self.company_id.document_sequence):
            company_sequence = self.env['ir.sequence'].search(
                [('company_id', '=', self.company_id.id), ('code', '=', code), ('prefix', '=', 'SO')], limit=1)
            name = ref + '-' + self.company_id.code + '-' + str(company_sequence.number)
            company_sequence.write({'number': company_sequence.number + 1})

            self.write({'name': name})

        else:
            parent_sequence = self.env['ir.sequence'].search(
                [('company_id', '=', self.company_id.parent_id.id), ('code', '=', code), ('prefix', '=', 'SO')],
                limit=1)
            if (parent_sequence):
                name = ref + '-' + self.company_id.parent_id.code + '-' + str(parent_sequence.number)
                parent_sequence.write({'number': parent_sequence.number + 1})

            self.write({'name': name})

        self.write({'state': 'locked'})

    def action_unlock(self):
        self.write({'state': 'draft'})

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        for so in self:
            # confirm registration if it was free (otherwise it will be confirmed once invoice fully paid)
            so.order_line._update_registrations(confirm=so.amount_total == 0, cancel_to_draft=False)

            receivable_account = so.partner_id.property_account_receivable_id
            receivable = self.env['account.account'].search(
                [('code', '=', receivable_account.code), ('company_id', '=', so.company_id.id),
                 ('user_type_id', '=', receivable_account.user_type_id.id)], limit=1)

            payable_account = so.partner_id.property_account_payable_id
            payable = self.env['account.account'].search(
                [('code', '=', payable_account.code), ('company_id', '=', so.company_id.id),
                 ('user_type_id', '=', payable_account.user_type_id.id)], limit=1)

            so.partner_id.write(
                {'property_account_receivable_id': receivable.id, 'property_account_payable_id': payable.id})

            for line in so.order_line:
                income_account = self.env['account.account'].search(
                    [('code', '=', '400000'), ('company_id', '=', so.company_id.id)], limit=1)
                line.product_id.write({'property_account_income_id': income_account.id})

        return res

    def action_confirm(self):
        for so in self:
            if any(so.order_line.filtered(lambda line: line.event_id)):
                return self.env['ir.actions.act_window'] \
                    .with_context(default_sale_order_id=so.id) \
                    .for_xml_id('education', 'action_sale_order_full_registration')

        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()
        })

        for line in self.order_line:
            if not line.event_id:
                template = line.product_id.product_tmpl_id
                registration = self.env['product.registration'].search(
                    [('partner_id', '=', self.partner_id.id), ('product_tmpl_id', '=', template.id)])
                if not registration:
                    registration = self.env['product.registration'].create({
                        'partner_id': self.partner_id.id,
                        'product_tmpl_id': template.id,
                        'date_open': self.date_order,
                        'sale_order_id': self.id,
                        'origin': self.name,
                        'sale_order_line_id': line.id,
                        'company_id': self.company_id.id,
                    })

                registration.onchange_partner_id()

        self._action_confirm()

    def action_confirm_order(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])

        self.write({
            'state': 'sale',
            'date_order': fields.Datetime.now()

        })
        self._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()

        return True

    @api.depends('order_line.event_id')
    def _compute_event_ids(self):
        for sale in self:
            sale.event_ids = sale.order_line.event_id

    def _session_seats_available(self):
        tracks = {}
        for line in self.mapped('order_line').filtered(lambda x:
                                                       x.event_track_seats_availability == 'limited'):
            tracks.setdefault(line.track_id, line.event_track_seats_available)
            tracks[line.track_id] -= line.product_uom_qty
            if tracks[line.track_id] < 0:
                return False
            return True

    def action_cancel(self):
        for line in self.order_line:
            if line.event_id:
                # raise UserError(self.env['event.registration'].search([('event_id','=',line.event_id.id),('sale_order_id','=',self.id)]))
                self.env['event.registration'].search(
                    [('event_id', '=', line.event_id.id), ('sale_order_id', '=', self.id)]).button_reg_cancel()

            if line.session_id:
                self.env['event.registration'].search(
                    [('event_id', '=', line.event_id.id), ('sale_order_id', '=', self.id)]).button_reg_cancel()

        return self.write({'state': 'cancel'})

    def get_amount_discount(self):
        for record in self:
            record.amount_discount = record.amount_undiscounted - record.amount_untaxed

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.pricelist_id = False

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.pricelist_id = False
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
            if warehouse:
                self.warehouse_id = warehouse.id

    @api.onchange('pricelist_id')
    def onchange_pricelist(self):
        if self.pricelist_id:
            event_regist = self.env.ref('event_sale.product_product_event_product_template').id
            session_regist = self.env.ref('education.product_product_session_product_template').id
            products = []
            products.append(event_regist)
            products.append(session_regist)
            for line in self.pricelist_id.item_ids:
                if line.product_tmpl_id:
                    products.append(line.product_tmpl_id.product_variant_id.id)

            self.product_ids = [(6, 0, products)]

    def _prepare_invoice(self):
        self.ensure_one()
        journal = self.env['account.move'].with_context(force_company=self.company_id.id,
                                                        default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'invoice_partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }

        return invoice_vals

    def _get_child_companies(self):
        company = self.env.company
        child_company = self.env['res.company'].search([('parent_id', '=', company.id)], limit=1)
        if child_company:
            return child_company.id

        else:
            return company.id

    def recompute_coupon_lines(self):
        for order in self:
            order._remove_reward_lines()
            order._apply_bundle_promotions()
            order._create_new_no_code_promo_reward_lines()
            # order._update_existing_reward_lines()

    def _remove_reward_lines(self):
        self.ensure_one()
        order = self
        order_lines = self.env['sale.order.line'].search(
            [('order_id', 'in', order.ids), ('is_reward_line', '=', 1)]).unlink()

    def _apply_bundle_promotions(self):
        self.ensure_one()
        order = self
        bundle = False
        qty = 1
        product_ids = self.order_line.mapped('product_id').ids
        templates = self.env['product.template'].search([('pack_product_ids', '=', product_ids)])
        for template in templates:
            if len(template.pack_product_ids) == len(product_ids):
                self.env['sale.order.line'].search([('product_id', 'in', product_ids), ('order_id', 'in', self.ids)],
                                                   limit=1).product_uom_qty
                self.env['sale.order.line'].search(
                    [('product_id', 'in', product_ids), ('order_id', 'in', self.ids)]).unlink()
                bundle = template
                break
        if bundle:
            bundle_order_line = self.env['sale.order.line'].search(
                [('order_id', '=', self.id), ('product_id', '=', bundle.id)])
            if not bundle_order_line:
                bundle_order_line = self.env['sale.order.line'].create({
                    'product_id': bundle.product_variant_id.id,
                    'order_id': self.id,
                    'product_uom': bundle.uom_id.id,
                    'product_uom_qty': qty,
                })

            bundle_order_line.product_id_change()

    def _create_invoices(self, grouped=False, final=False):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')

            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoice_vals_list = []
        for order in self:
            pending_section = None
            invoice_vals = order._prepare_invoice()
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue

                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None

                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(
                    _('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        if not grouped:
            new_invoice_vals_list = []
            for grouping_keys, invoices in groupby(invoice_vals_list,
                                                   key=lambda x: (x.get('partner_id'), x.get('currency_id'))):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']

                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])

                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })

                new_invoice_vals_list.append(ref_invoice_vals)

            invoice_vals_list = new_invoice_vals_list

        # raise UserError(str(invoice_vals_list))
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()

        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                                        values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                                        subtype_id=self.env.ref('mail.mt_note').id
                                        )
        return moves
