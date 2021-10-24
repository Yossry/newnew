odoo.define('pos_all_in_one.ClientListScreen', function(require) {
	'use strict';

	const ClientListScreen = require('point_of_sale.ClientListScreen');
	const Registries = require('point_of_sale.Registries');
	const core = require('web.core');
	const _t = core._t;

	const NewClientListScreen = ClientListScreen => class extends ClientListScreen {
		constructor() {
			super(...arguments);
			this.update_customers();
		}
		
		async update_customers() {
			await this.env.pos.load_new_partners();
		}

		register_payment() {
			var self = this;
			const partner_id = self.state.selectedClient;
			if (!partner_id) {

				self.showPopup('ErrorPopup', {
					'title': _t('Unknown customer'),
					'body': _t('You cannot Register Payment. Select customer first.'),
				});
				return false;
			}

			self.showPopup('RegisterPaymentPopupWidget', {'partner':self.state.selectedClient});
		}
	};

	Registries.Component.extend(ClientListScreen, NewClientListScreen);

	return ClientListScreen;

});