# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class pos_config(models.Model):
	_inherit = 'pos.config'

	allow_pos_product_operations = fields.Boolean(string='Allow Product Operations')
	allow_edit_product  = fields.Boolean(string='Allow user to edit/create product from pos')

class ProductProduct(models.Model):
	_inherit = 'product.product'
		
	@api.model
	def create_from_ui(self, product):
		# image is a dataurl, get the data after the comma
		product_id = product.pop('id', False)
		prod = self.browse(product_id)
		if product_id:
			if prod.product_tmpl_id.attribute_line_ids:
				if product.get('list_price') != '':
					if '.' in product.get('list_price'):
						prod.mapped('product_template_attribute_value_ids.price_extra')
						len_variant = len(prod.mapped('product_template_attribute_value_ids.price_extra'))
						for i in prod.mapped('product_template_attribute_value_ids'):
							divided_price = (float(product.get('list_price'))/len_variant);
							i.write({'price_extra' : divided_price});
						
						product['list_price'] = prod.list_price

					else:
						product['price_extra'] = product.get('list_price').replace(',','.')
						AttributePrice = self.env['product.template.attribute.value']
						prices = AttributePrice.search([
							('product_attribute_value_id','in',prod.product_template_attribute_value_ids.ids),
					
						])
						updated = prices.mapped('ptav_product_variant_ids');
						
						len_variant = len(prod.mapped('product_template_attribute_value_ids.price_extra'));
						
						for i in prod.mapped('product_template_attribute_value_ids'):
							divided_price = (int(product['price_extra'])/len_variant);
							i.write({'price_extra' : divided_price});

						product['list_price'] = prod.list_price;
						

				else:
						product['lst_price'] = prod.lst_price
			else:
				if product.get('list_price',False):
					product['lst_price'] = product.get('list_price')
				else:
					product['lst_price'] = prod.lst_price
		else:
			if '.' in product.get('list_price'):
				product['list_price'] = product.get('list_price')
			else:
				product['list_price'] = product.get('list_price').replace(',','.')

		if product.get('cost_price',False):
			if '.' in product.get('cost_price'):        
				product['cost_price'] = product.get('cost_price')       
			else:       
				product['cost_price'] = product.get('cost_price').replace(',','.')
		else:
			product['cost_price'] = prod.standard_price

		if product.get('pos_categ_id',False):
			product['pos_categ_id'] =product.get('pos_categ_id')
		

		product['available_in_pos'] = True
		str_b = False

		if product.get('image_1920',False):
			str_b = product.get('image_1920').strip("data:image/png;base64,")
			product['image_1920'] ="i"+str_b
			if product_id:  # Modifying existing product
				if product.get('cost_price'):
					standard_price = product.pop('cost_price',0.0)
					product.update({
						'standard_price' : float(standard_price)
					})
				self.browse(product_id).write(product)
			else:
				product_id = self.create({
					'name':product.get('name'),
					'available_in_pos' : True,
					'barcode':product.get('barcode'),
					'lst_price':product.get('list_price'),
					'standard_price':product.get('cost_price'),
					'pos_categ_id' :product.get('pos_categ_id'),
					'image_1920':"i"+str_b
				})
		else:
			if product_id:  # Modifying existing product
				if product.get('cost_price') or product.get('cost_price') == 0 :
					standard_price = product.pop('cost_price',0.0)
					product.update({
						'standard_price' : float(standard_price)
					})
					self.browse(product_id).write(product)
				else:
					self.browse(product_id).write(product)
			else:
				product_id = self.create({
					'name':product.get('name'),
					'available_in_pos' : True,
					'barcode':product.get('barcode'),
					'lst_price':product.get('list_price'),
					'standard_price':product.get('cost_price'),
					'pos_categ_id' :product.get('pos_categ_id')
				})
		return product_id
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: