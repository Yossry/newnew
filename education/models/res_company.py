from odoo import models, fields, api
import pytz


class ResCompany(models.Model):
    _inherit = 'res.company'
    image = fields.Binary()
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code', required=True)
    report_footer = fields.Text('Report Footer', translate=True)
    disclaimer = fields.Text('Disclaimer', translate=True)
    currency_id = fields.Many2one('res.currency', string="Currency")
    fax = fields.Char('Fax')
    country_id = fields.Many2one('res.country', string="Country")
    show_in_invoice = fields.Boolean('Show In Invoice')
    show_in_quotation = fields.Boolean('Show In Quotation')
    show_in_credit_note = fields.Boolean('Show In Credit Note')
    show_in_refund = fields.Boolean('Show In Refund')
    show_in_payment = fields.Boolean('Show In Payment')
    show_in_payment_schedule = fields.Boolean('Schedule')
    region_ids = fields.One2many('res.company', 'parent_id')
    tax_ids = fields.One2many('account.tax', 'company_id')
    bank_account_ids = fields.One2many('account.journal', 'company_id', domain=lambda self: [('type', '=', 'bank'), (
    'name', '!=', 'Instructor Payments')])
    warehouse_ids = fields.One2many('stock.warehouse', 'company_id')
    is_region = fields.Boolean('Is Region', compute='_compute_is_region', store=True)
    date_tz = fields.Selection('_tz_get', string='Timezone', required=True,
                               default=lambda self: self.env.user.tz or 'UTC')
    pricelist_ids = fields.One2many('product.pricelist', 'company_id', string='Pricelists')
    document_sequence = fields.Boolean('Followed by parent company',
                                       help='if checked, the sequence of the company related document will follow the parent company')
    main_pricelist_id = fields.Many2one('product.pricelist', string='Main Pricelist', required=True)
    signature = fields.Binary('Signature')
    signature_name = fields.Char('Signer')
    exam = fields.Boolean('Make exam field mandatory in opportunity')
    cpf = fields.Boolean(string='CPF')
    invoice_name = fields.Char('Invoice name')
    credit_note_name = fields.Char('Credit note name')
    receipt_name = fields.Char('Receipt Name')
    refund_name = fields.Char('Refund Name')
    quotation_name = fields.Char('Quotation Name')
    soa_name = fields.Char('SOA Name')
    invoice_issuance = fields.Boolean('Invoice from parent company',
                                      help='if checked, the billing company would be the parent company')

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        val = {}
        logo = False
        currency_id = False
        date_tz = self.env.user.tz or 'UTC'
        if (self.parent_id):
            logo = self.parent_id.logo
            currency_id = self.parent_id.currency_id.id
            date_tz = self.parent_id.date_tz
        val['value'] = {
            'logo': logo,
            'currency_id': currency_id,
            'date_tz': date_tz,
        }
        return val

    @api.model
    def create(self, vals):
        record = super(ResCompany, self).create(vals)

        sale_order_sequence = self.env['ir.sequence'].create({
            'name': 'Sales Order',
            'implementation': 'standard',
            'prefix': 'SO',
            'padding': 5,
            'company_id': record.id,
            'code': 'sale.order',
            'active': 1,
        })

        account_move_sequence = self.env['ir.sequence'].create({
            'name': 'Invoices',
            'implementation': 'standard',
            'prefix': 'SI',
            'padding': 5,
            'company_id': record.id,
            'code': 'account.move',
            'active': 1,
        })

        account_payment_sequence = self.env['ir.sequence'].create({
            'name': 'Payments',
            'implementation': 'standard',
            'prefix': 'RC',
            'padding': 5,
            'company_id': record.id,
            'code': 'account.payment',
            'active': 1,
        })

        future_payment_sequence = self.env['ir.sequence'].create({
            'name': 'Future Payments',
            'implementation': 'standard',
            'prefix': 'FP',
            'padding': 5,
            'company_id': record.id,
            'code': 'account.move.line',
            'active': 1,
        })

        regions = self.env['res.company'].search([('parent_id', '=', record.id)])
        record.partner_id.write({'type': 'training'})
        if (record.parent_id):
            query = "UPDATE res_company set is_region=False where id = " + str(record.parent_id.id)
            self._cr.execute(query)
        if (regions):
            record.is_region = False
        else:
            record.is_region = True
        return record

    def write(self, vals):
        record = super(ResCompany, self).write(vals)
        regions = self.env['res.company'].search([('parent_id', '=', self.id)])
        self.partner_id.write({'type': 'training'})
        if (self.parent_id):
            query = "UPDATE res_company set is_region=False where id = " + str(self.parent_id.id)
            self._cr.execute(query)
        if (regions):
            vals['is_region'] = False
        else:
            vals['is_region'] = True
        return super(ResCompany, self).write(vals)

    def _compute_is_region(self):
        for record in self:
            regions = self.env['res.company'].search([('parent_id', '=', record.id)])
            if (regions):
                record.is_region = False
            else:
                record.is_region = True
