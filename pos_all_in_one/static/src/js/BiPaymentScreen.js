odoo.define('pos_all_in_one.BiPaymentScreen', function(require) {

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');

	const session = require('web.session');
	const PosComponent = require('point_of_sale.PosComponent');

	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;

	const BiPaymentScreen = PaymentScreen => class extends PaymentScreen {
		constructor() {
			super(...arguments);
			useListener('click-update_amount', this._UpdateAmountt);
			useListener('click-cur-switch', this._UpdateDetails);
		}

		mounted() {
			$('#details').hide()
		}

		async selectClient() {
			let order = this.env.pos.get_order();
			let self = this;
			if(order.redeem_done){
				this.showPopup('ErrorPopup',{
					'title': this.env._t('Cannot Change Customer'),
					'body': this.env._t('Sorry, you redeemed product, please remove it before changing customer.'),
				}); 
			}else{
				const currentClient = this.currentOrder.get_client();
				const { confirmed, payload: newClient } = await this.showTempScreen(
					'ClientListScreen',
					{ client: currentClient }
				);
				if (confirmed) {
					this.currentOrder.set_client(newClient);
					this.currentOrder.updatePricelist(newClient);
				}
			}
		}


		_UpdateDetails() {
			if($("#cur-switch").prop('checked') == true)
			{
				$('#details').hide()
			}
			else
			{
				$('#details').show()
			}
		}

		_UpdateAmountt() {
			let self = this;
			let order = this.env.pos.get_order();
			let paymentlines = this.env.pos.get_order().get_paymentlines();
			let open_paymentline = false;
			let tot = order.get_curamount();
			let tot_amount = 0;
			let currency = this.env.pos.poscurrency;
			let user_amt = $('.edit-amount').val();
			let cur = $('.drop-currency').val();
			for(var j=0;j<paymentlines.length;j++){
				order.remove_paymentline(paymentlines[j])
			}

			order.add_paymentline(this.env.pos.payment_methods[0]);
			for(var i=0;i<currency.length;i++)
			{
				if(cur==currency[i].id)
				{
					for(var j=0;j<paymentlines.length;j++){
						tot_amount = user_amt*self.env.pos.company_currency.rate/currency[i].rate;
						paymentlines[j].amount =parseFloat(tot_amount.toFixed(2));
						paymentlines[j].amount_currency =parseFloat(tot.toFixed(2)) ;
						$('.show-payment').text(this.env.pos.format_currency_no_symbol(paymentlines[j].amount));
					}
				}
			}
			order.get_paymentlines();
			if (!order) {
				return;
			} else if (order.is_paid()) {
				$('.next').addClass('highlight');
			}else{
				$('.next').removeClass('highlight');
			}
			window.document.body.removeEventListener('keypress', self.keyboard_handler);
			window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
		}

		_ChangeConfig() {
			let config = false;
			let order= this.env.pos.get_order();
			if($('#Receipt').prop('checked') == true){
				order.set_inrecipt(true);
			}
			else{
				order.set_inrecipt(false);
			}   
		}

		_ChangeCurrency(ev) {
			let self = this;
			
			let currencies = this.env.pos.poscurrency;
			let cur = ev.target.value;
			let curr_sym;
			let order= this.env.pos.get_order();
			let pos_currency = this.env.pos.currency;
			for(var i=0;i<currencies.length;i++)
			{
				if(cur != pos_currency.id && cur==currencies[i].id)
				{
					let currency_in_pos = (currencies[i].rate/self.env.pos.currency.rate).toFixed(6);
					$('.currency_symbol').text(currencies[i].symbol);
					$('.currency_rate').text(currency_in_pos);
					$('.currency_name').text(currencies[i].name);
					curr_sym = currencies[i].symbol;

					let curr_tot =order.get_total_with_tax()*currency_in_pos;
					$('.currency_cal').text(parseFloat(curr_tot.toFixed(6)));
					order.set_curamount(parseFloat(curr_tot.toFixed(6)));
					order.set_symbol(curr_sym);
					order.set_curname(currencies[i].name);

					return curr_tot;
				}
				if(cur == pos_currency.id && cur==currencies[i].id){
					$('.currency_symbol').text(pos_currency.symbol);
					$('.currency_rate').text(1);
					$('.currency_name').text(pos_currency.name);
					curr_sym = pos_currency.symbol;

					let curr_tot =order.get_total_with_tax();
					$('.currency_cal').text(parseFloat(curr_tot.toFixed(2)));
					order.set_curamount(parseFloat(curr_tot.toFixed(2)));
					order.set_symbol(curr_sym);
					order.set_curname(pos_currency.name);

					return curr_tot;
				}
			}
		}
	}

	Registries.Component.extend(PaymentScreen, BiPaymentScreen);

	return PaymentScreen;
});