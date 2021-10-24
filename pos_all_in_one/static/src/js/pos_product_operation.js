odoo.define('pos_all_in_one.pos_prod_op', function (require) {
	"use strict";

	var models = require('point_of_sale.models');
	models.load_fields('product.product', ['image_1920']);

	models.load_models({
		model: 'pos.category',
		fields: ['id', 'name', 'parent_id', 'child_id', 'write_date'],
		domain: function(self) {
		},
		loaded: function(self, pos_category) {
			
			self.pos_category = pos_category;
		},

	});

	models.PosModel = models.PosModel.extend({
		prepare_new_products_domain: function(){
			return [['write_date','>', this.db.get_partner_write_date()]];
		},

		load_new_products: function(){
			var self = this;
			return new Promise(function (resolve, reject) {
				// var fields = _.find(self.models, function(model){ return model.label === 'load_products'; }).fields;
				var domain = []
				self.rpc({
					model: 'product.product',
					method: 'search_read',
					args: [domain],
				}, {
					timeout: 3000,
					shadow: true,
				})
				.then(function (products) {
				if (self.db.add_products(products)) {   // check if the products we got were real updates
					resolve();
				} else {
					reject('Failed in updating products.');
				}
			}, function (type, err) { reject(); });
			});
		},
	});
});