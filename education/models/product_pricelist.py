from odoo import api, fields, models

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'

    product_tmpl_id = fields.Many2one('product.template','Product')
    is_region = fields.Boolean(related='company_id.is_region')
    company_id = fields.Many2one(required=False)
    
    @api.model
    def create(self, vals):
      record = super(ProductPriceList, self).create(vals)
      record.currency_id.write({'companies_ids': record.currency_id.compute_companies()})
      return record

    def write(self, vals):
      record = super(ProductPriceList, self).write(vals)
      self.currency_id.write({'companies_ids': self.currency_id.compute_companies()})
      return super(ProductPriceList, self).write(vals)


    def _compute_price_event(self,event, ticket, currency):
      date = fields.Date.today()
      price = currency._convert(ticket.price, self.currency_id, event.company_id, date, round=False)
      item = self.env['product.pricelist.item'].search(['|',('date_end','>',date),('date_end','=',False),('pricelist_id','in',self.ids),('event_id','=',event.id),('applied_on','=','4_event')],order='id desc', limit=1)
      if item.compute_price == 'fixed':
        price = currency._convert(item.fixed_price, self.currency_id, event.company_id, date, round=False)

      elif item.compute_price == 'percentage':
        price = price - (price * item.percent_price/100)

      return price
        






