from odoo import  fields, models,api, _
from odoo.exceptions import UserError


class ProductRegistration(models.Model):

    _inherit = ['mail.thread.cc', 'mail.thread.blacklist', 'mail.activity.mixin',
    'utm.mixin', 'format.address.mixin', 'phone.validation.mixin']
    _name = 'product.registration'
    name = fields.Char('Attendee Name')
    product_tmpl_id = fields.Many2one('product.template',string='Product')
    partner_id = fields.Many2one('res.partner','Contact')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    attempt_ids = fields.One2many('attempt','product_registration_id',string="Attempts")
    sale_order_id = fields.Many2one('sale.order',string='Source Sales Order')
    origin = fields.Char(string='Origin')
    date_open = fields.Datetime('Registration Date')
    date_closed = fields.Datetime('Attended Date')
    sale_order_line_id = fields.Many2one('sale.order.line',string='Sale Order Line')
    company_id = fields.Many2one('res.company',string='Region',domain="[('is_region','=',True)]")
    total_score = fields.Float(compute="compute_total_score")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.email = self.partner_id.email
            self.name = self.partner_id.name
            self.phone = self.partner_id.phone
            self.mobile = self.partner_id.mobile

    def compute_total_score(self):
        for record in self:
            record['total_score'] = sum(record.attempt_ids.mapped('score'))




