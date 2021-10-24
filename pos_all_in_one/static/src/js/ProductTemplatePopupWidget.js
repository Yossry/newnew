
odoo.define('pos_all_in_one.ProductTemplatePopupWidget', function(require){
	'use strict';

	const Popup = require('point_of_sale.ConfirmPopup');
	const Registries = require('point_of_sale.Registries');
	const PosComponent = require('point_of_sale.PosComponent');	

	class ProductTemplatePopupWidget extends Popup {

		go_back_screen() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}
	}
	
	ProductTemplatePopupWidget.template = 'ProductTemplatePopupWidget';

	Registries.Component.add(ProductTemplatePopupWidget);

	return ProductTemplatePopupWidget;

});