odoo.define('pos_all_in_one.ProductsWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductsWidget = require('point_of_sale.ProductsWidget');

	const BiProductsTemplateWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			constructor() {
				super(...arguments);
			}

			get productsToDisplay() {
				let self = this;
				let product_ids = super.productsToDisplay;
		        var list = [];
		        var temp = this.env.pos.product_templates;
		        var product_tmpl_lst = []
		        if (product_ids) {
		            for (var i = 0; i < temp.length; i++) {
		                for (var j = 0 ; j < product_ids.length ; j++){
		                    var prd_prod = product_ids[j]
		                    if(jQuery.inArray( prd_prod.product_tmpl_id, product_tmpl_lst ) == -1){
		                        if(prd_prod.product_tmpl_id == temp[i].id){
		                            var prd_list = temp[i].product_variant_ids.sort();
		                            list.push(prd_prod)
		                            product_tmpl_lst.push(temp[i].id)
		                        }
		                    }
		                }
		            }
		        }
	        	return list;
			}
		};

	Registries.Component.extend(ProductsWidget, BiProductsTemplateWidget);

	return ProductsWidget;

});