odoo.define('pos_all_in_one.POSProductScreen', function (require) {
	'use strict';

	const { debounce } = owl.utils;
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const { useListener } = require('web.custom_hooks');
	const { onChangeOrder } = require('point_of_sale.custom_hooks');
	const field_utils = require('web.field_utils');
	var rpc = require('web.rpc');

	class POSProductScreen extends PosComponent {
		constructor() {
			super(...arguments);
			this.state = {
				query: null,
				selectedPosOrder: this.props.client,
			};
			useListener('click-showDetails', this.showDetails);
			let product_dict = this.env.pos.db.product_by_id;
			this.refresh_orders();
			this.updateProductList = debounce(this.updateProductList, 70);
			let data = Object.keys(product_dict).map(function(k) {
				return product_dict[k];
			});
			this.orders = data || [];
		}

		get AddNewProduct(){
			let product_dict = this.env.pos.db.product_by_id;
			let data = Object.keys(product_dict).map(function(k) {
				return product_dict[k];
			});
			this.orders = data || [];

		}

		cancel() {
			this.props.resolve({ confirmed: false, payload: false });
			this.trigger('close-temp-screen');
		}

		get currentOrder() {
			return this.env.pos.get_order();
		}

		get pos_orders() {
			let self = this;
			let query = this.state.query;
			if(query){
				query = query.trim();
				query = query.toLowerCase();
			}
			if (query && query !== '') {
				return this.search_orders(this.orders,query);
			} else {
				return this.orders;
			}
		}

		search_orders(orders,query){
			let self = this;
			let selected_orders = [];
			let search_text = query;			
			orders.forEach(function(odr) {
				if (search_text) {
					if (((odr.display_name.toLowerCase()).indexOf(search_text) != -1)) {
						selected_orders.push(odr);
					}
					 if(odr.barcode != false){
						if(odr.barcode.indexOf(search_text) != -1){
							selected_orders.push(odr);
						}
					}
				}
			});
			return selected_orders;
		}

		get_orders_fields(){
			var fields = ['name','display_name','default_code','barcode','image_1920','lst_price','standard_price',
				'categ_id','pos_categ_id','taxes_id','to_weight','uom_id','description_sale','tracking',
				'description','product_tmpl_id','write_date','available_in_pos','attribute_line_ids'];
			return fields;
		}

		refresh_orders(){
			var self = this;
			var fields = this.get_orders_fields();

			self.rpc({
					model: 'product.product',
					method: 'search_read',
					args: [null,fields],
			}, {
				timeout: 3000,
				shadow: true,}).then(function(output) {
				let data = Object.keys(output).map(function(k) {
					return output[k];
				});
				self.orders = data || [];
				self.state.query = '';
				self.render();

			});
			// this.AddNewProduct
			$('.input-search-orders').val('');
			this.state.query = '';
			this.render();
		}

		create_order(event){
			this.showPopup('ProductDetailsCreate', {
				products : {values: null}
			})
		}

		updateProductList(event) {
			this.state.query = event.target.value;
			const pos_orders = this.pos_orders;
			if (event.code === 'Enter' && pos_orders.length === 1) {
				this.state.selectedPosOrder = pos_orders[0];
			} else {
				this.render();
			}
		}

		clickPosOrder(event) {
			let order = event.detail.order;
			if (this.state.selectedPosOrder === order) {
				this.state.selectedPosOrder = null;
			} else {
				this.state.selectedPosOrder = order;
			}
			this.render();
		}

		showDetails(event){
			let self = this;
			let o_id = parseInt(event.detail.id);
			let orders =  self.orders;
			let orders1 = [event.detail];
			
			self.showPopup('POSProductDetail', {
				'order': event.detail, 
			});
		}
	}


	POSProductScreen.template = 'POSProductScreen';
	POSProductScreen.hideOrderSelector = true;
	Registries.Component.add(POSProductScreen);
	return POSProductScreen;
});
