from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError
import base64
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    program_id = fields.Many2one('program', string="Program")
    session_ok = fields.Boolean(string='Is a Session Ticket', help="If checked this product automatically "
        "creates a session registration at the sales order confirmation.")

    pricelist_item_ids = fields.One2many('product.pricelist.item','product_tmpl_id',string='Company Prices',domain=lambda self:[('is_region','=',False)])

    region_pricelist_items = fields.One2many('product.pricelist.item','product_tmpl_id',string='Prices',domain=lambda self:[('is_region','=',True)])

    product_type = fields.Selection([('Standalone','Standalone'),('Package','Package'),('Add on','Add on')])

    image_id = fields.Char()

    product_tmpl_ids = fields.Many2many('product.template', 'product_related_rel', 'src_id', 'dest_id',string='Related Products')

    pack_product_ids = fields.Many2many('product.product','product_variant_rel','template_id','variant_id',string='Pack Products')

    company_prices = fields.One2many('company.price','product_tmpl_id',string="Company Prices",track_visibility='onchange',copy=True)
    region_prices = fields.One2many('company.price','product_tmpl_region_id',string="Region Prices",track_visibility='onchange',copy=True)
    registration_ids = fields.One2many('product.registration','product_tmpl_id',string='Registrations')
    registration_count = fields.Integer(compute="compute_registrations")

    attempt_count = fields.Float('Nb of attempts',compute="compute_attempt")
    passing_rate = fields.Float('Passing Rate (%)',compute="compute_attempt")

    def compute_registrations(self):
        for record in self:
            record['registration_count'] = len(record.registration_ids)

    @api.onchange('session_ok')
    def _onchange_session_ok(self):
        if self.session_ok:
            self.type = 'service'


    def generate_price(self):
        date = datetime.now().strftime('%Y-%m-%d')
        self.env['company.price'].search([('product_tmpl_region_id', 'in', self.ids)]).unlink()

        if self.company_prices:
            product_taxes = []
            for company_price in self.company_prices:
                regions = company_price.company_id.region_ids
                for region in regions:

                    taxes = []
                    for tax in company_price.tax_ids:
                        

                        related_tax = self.env['account.tax'].search([('company_id','=',region.id)],limit=1)
                        if not related_tax:
                            related_tax = self.env['account.tax'].search([('company_id','=',region.parent_id.id)],limit=1)

                        if related_tax:
                            taxes.append(related_tax.id)

                    regionPrice = self.env['company.price'].create({
                        'company_id': region.id,
                        'tax_ids': [(6, False, taxes)],
                        'product_tmpl_region_id': self.id,
                        'price': company_price.price,
                        })

                    regionPrice._compute_local_price()

                    pricelist = region.main_pricelist_id
                    if not pricelist:
                        raise UserError('Region %s does not have a main pricelist' % region.name)
                    item_vals = {}
                    item_vals['product_tmpl_id'] = self.id
                    item_vals['pricelist_id'] = pricelist.id
                    item_vals['applied_on'] = '1_product'
                    item_vals['compute_price'] = 'fixed'
                    item_vals['fixed_price'] = regionPrice.local_price
                    item_vals['min_quantity'] = 1

                    pricelist_item = self.env['product.pricelist.item'].search([('product_tmpl_id','=',self.id),('pricelist_id','=',pricelist.id)])
                    if not pricelist_item:
                        pricelist_item = self.env['product.pricelist.item'].create(item_vals)

                    else:
                        pricelist_item = self.env['product.pricelist.item'].write(item_vals)

        if self.region_prices:
            product_taxes = self.region_prices.mapped('tax_ids').ids
            if product_taxes:
                self.write({'taxes_id': [(6, 0, product_taxes)]})
    
    @api.onchange('pack_ids')
    def _onchange_packs(self):
        if self.pack_ids:
            products = []
            for pack in self.pack_ids:
                products.append(pack.product_id.id)

            self.pack_product_ids = [(6, 0, products)]


    def show_related_registrations(self):
        res = {
        'type': 'ir.actions.act_window',
        'name': _('Product Registrations'),
        'view_mode': 'tree,form',
        'res_model': 'product.registration',
        'domain' : [('id','in',self.registration_ids.ids)],
        'target': 'current',
        'context': {'default_product_tmpl_id': self.id}
        }
        return res

    def compute_attempt(self):
        for record in self:
            record['passing_rate'] = 0
            nb_attempt = 0
            attempts = record.registration_ids.mapped('attempt_ids')
            record['attempt_count'] = len(attempts)
            passed_attempts = attempts.filtered(lambda c: c.passing_status == 'passed')
            if len(attempts) > 0:
                record['passing_rate'] = (len(passed_attempts) * 100) / len(attempts)


class Product(models.Model):
    _inherit = 'product.product'

    @api.onchange('session_ok')
    def _onchange_session_ok(self):
        """ Redirection, inheritance mechanism hides the method on the model """
        if self.session_ok:
            self.type = 'service'

