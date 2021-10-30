odoo.define('flexipharmacy_ee.PaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');
    const { useState } = owl.hooks;
    const { isRpcError } = require('point_of_sale.utils');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    const AsplRetPaymentScreenInh = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
                this.state = useState({ remaining_wallet_amount: 0, serialPrint : false});
                this.payment_methods_config = this.env.pos.payment_methods.filter(method => this.env.pos.config.payment_method_ids.includes(method.id));
                this.get_remaining_wallet_amount()
            }
            async connectionCheck(){
                var self = this;
                try {
                    await rpc.query({
                        model: 'pos.session',
                        method: 'connection_check',
                        args: [this.env.pos.pos_session.id],
                    });
                    self.state.is_connected = true
                    self.env.pos.get_order().set_connected(true)
                } catch (error) {
                    if (isRpcError(error) && error.message.code < 0) {
                        self.env.pos.get_order().set_connected(false)
                        self.state.is_connected = false
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Cannot access order management screen if offline.'),
                        });
                    } else {
                        throw error;
                    }
                }            
            }
            get decimalSeparator() {
                return this.env.pos.db.decimalSeparator();
            }
            get thousandsSeparator() {
                return this.env.pos.db.decimalSeparator();
            }
            thousandsDecimalChanger(amount) {
                var converted_amount = amount.replace(this.decimalSeparator, '!').replace(this.thousandsSeparator, '').replace('!', '.')
                if (!isNaN(parseFloat(converted_amount)) && isFinite(converted_amount)){
                    return parseFloat(converted_amount)
                }
            }

            _serialPrint(){
                var order = this.env.pos.get_order();
                this.state.serialPrint = !this.state.serialPrint;
                order.set_print_serial(this.state.serialPrint);
            }
            addNewPaymentLine({ detail: paymentMethod }) {
                super.addNewPaymentLine(...arguments);
                if(this.env.pos.config.customer_display){
                    this.currentOrder.mirror_image_data();
                }
            }
            _updateSelectedPaymentline() {
                super._updateSelectedPaymentline(...arguments);
                if(this.env.pos.config.customer_display){
                    this.currentOrder.mirror_image_data();
                }
            }
            deletePaymentLine(event){
                super.deletePaymentLine(...arguments);
                if(this.env.pos.config.customer_display){
                    this.currentOrder.mirror_image_data();
                }
            }
            async showSignaturePopup(){
                const { confirmed ,payload: data } = await this.showPopup('SignaturePopup', {
                    title: this.env._t('Signature'),
                });
                if(confirmed){
                    var order = this.env.pos.get_order();
                    order.set_raw_sign(data['base30'][1] ? data['base30'] : false);
                    order.set_sign(data['base30'][1] ? data['base64'][1] : false);
                }
            }
            get is_payment_line(){
                var self = this
                var lines_type = {lines_type_wallet: false, lines_type_giftcard: false, lines_type_voucher: false}
                _.each(this.env.pos.get_order().get_paymentlines(), function(payment_line){
                    if (payment_line.payment_method && payment_line.payment_method.jr_use_for){
                        if(payment_line.payment_method.jr_use_for === 'wallet'){
                            lines_type['lines_type_wallet'] = true
                        }
                        if (payment_line.payment_method.jr_use_for === 'gift_card'){
                            lines_type['lines_type_giftcard'] = true
                        }
                        if (payment_line.payment_method.jr_use_for === 'gift_voucher'){
                            lines_type['lines_type_voucher'] = true
                        }
                    }
                });
                return lines_type
            }
            async get_remaining_wallet_amount() {
                var self = this
                if (this.env.pos.get_order() && this.env.pos.get_order().get_client() && this.env.pos.get_order().get_client().id){
                    await this.rpc({
                        model: "res.partner",
                        method: "search_read",
                        domain: [['id', '=', this.env.pos.get_order().get_client().id]],
                        fields:['remaining_wallet_amount']
                    }, {async: false}).then(function(results){
                        _.each(results, function(result){
                            self.state.remaining_wallet_amount = result.remaining_wallet_amount
                        });
                    });
                }
            }
            async createPaymentLine(paymentMethod)  {
                var self = this
                await this.connectionCheck()
                if (this.env.pos.get_order().get_connected()){
                    var lines = this.env.pos.get_order().get_paymentlines();
                    var order = this.env.pos.get_order();
                    if (paymentMethod == 'wallet'){
                        for ( var i = 0; i < lines.length; i++ ) {
                            if(lines[i].payment_method.jr_use_for == 'wallet'){
                                this.deletePaymentLine({ detail: { cid: lines[i].cid } });
                            }
                        }
                        var order = this.env.pos.get_order();
                        if(order.getNetTotalTaxIncluded() <= 0){
                            return
                        }
                        this.useWalletForPayment(self, lines, order)
                    }
                    if (paymentMethod == 'giftCard'){
                        for ( var i = 0; i < lines.length; i++ ) {
                            if(lines[i].payment_method.js_gift_card == 'giftCard'){
                                this.deletePaymentLine({ detail: { cid: lines[i].cid } });
                            }
                        }
                        var order = this.env.pos.get_order();
                        if(order.getNetTotalTaxIncluded() <= 0){
                            return
                        }
                        this.useGiftCardForPayment(self, lines, order)
                    }
                    if (paymentMethod == 'giftVoucher'){
                        for ( var i = 0; i < lines.length; i++ ) {
                            if(lines[i].payment_method.js_gift_voucher == 'giftVoucher'){
                                this.deletePaymentLine({ detail: { cid: lines[i].cid } });
                            }
                        }
                        var order = this.env.pos.get_order();
                        if(order.getNetTotalTaxIncluded() <= 0){
                            return
                        }
                        this.useGiftVoucherForPayment(self, lines, order)
                    }
                    this.render();  
                }else{
                    this.env.pos.get_order().set_connected(false)
                }
            }
            async useGiftVoucherForPayment(self, lines, order)  {
                const {confirmed, payload} = await this.showPopup('giftVoucherRedeemPopup', {
                    title: this.env._t('Gift Voucher'),
                });

                if (confirmed){
                    var self = this;
                    var order = self.env.pos.get_order();
                    var client = order.get_client();
                    var redeem_amount = payload.card_amount;
                    var code = payload.card_no;
                    var voucher_id = payload.voucher_id;
                    if( Number(redeem_amount) > 0){
                        if(Number(redeem_amount)){
                            var vals = {
                                'voucher_id':payload.voucher_id,
                                'voucher_code':code,
                                'order_name': order.name,
                                'order_amount': order.get_total_with_tax(),
                                'voucher_amount':redeem_amount,
                                'used_date': moment().locale('en').format('YYYY-MM-DD'),
                                'user_id': order.user_id,
                                'customer_id': client.id,
                            }
                            if(order.get_rounding_applied() && order.get_rounding_applied() > 0){
                                vals['order_amount'] = order.get_total_with_tax() + order.get_rounding_applied()
                                
                            }
                            var product = self.env.pos.db.get_product_by_id(self.env.pos.config.gift_voucher_journal_id)
                            if(self.env.pos.config.gift_voucher_journal_id[0]){
                                var cashregisters = null;
                                for ( var j = 0; j <  self.env.pos.payment_methods.length; j++ ) {
                                    if( self.env.pos.payment_methods[j].id === self.env.pos.config.gift_voucher_journal_id[0]){
                                        cashregisters = self.env.pos.payment_methods[j];
                                    }
                                }
                            }
                            if (vals){
                                if (cashregisters){
                                    order.add_paymentline(cashregisters);
                                    order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                    order.set_redeem_giftvoucher(vals);
                                } 
                            }
                            this.trigger('close-popup');
                        }else{
                            self.env.pos.db.notification('danger',_t('Please enter amount below card value.'));
                        }
                    }else{
                        self.env.pos.db.notification('danger',_t('Please enter valid amount.'));
                    }
                }
            }
            async useGiftCardForPayment(self, lines, order)  {
                const { confirmed,payload } = await this.showPopup('giftCardRedeemPopup', {
                    title: this.env._t('Gift Card'),
                });
                if (confirmed){
                    var self = this;
                    var order = self.env.pos.get_order();
                    var client = order.get_client();
                    var redeem_amount = this.env.pos.db.thousandsDecimalChanger(payload.card_amount);
                    var code = payload.card_no;
                    self.redeem = payload.redeem
                    if( Number(redeem_amount) > 0){
                        if(self.redeem && self.redeem.card_value >= Number(redeem_amount) ){
                            if(self.redeem.customer_id[0]){
                                var vals = {
                                    'redeem_card_no':self.redeem.id,
                                    'redeem_card':$('#text_gift_card_no').val(),
                                    'redeem_card_amount': redeem_amount,
                                    'redeem_remaining':self.redeem.card_value - redeem_amount,
                                    'card_customer_id': client ? client.id : self.redeem.customer_id[0],
                                    'customer_name': client ? client.name : self.redeem.customer_id[1],
                                };
                            } else {
                                var vals = {
                                    'redeem_card_no':self.redeem.id,
                                    'redeem_card': code,
                                    'redeem_card_amount': redeem_amount,
                                    'redeem_remaining':self.redeem.card_value - redeem_amount,
                                    'card_customer_id': order.get_client() ? order.get_client().id : false,
                                    'customer_name': order.get_client() ? order.get_client().name : '',
                                };
                            }

                            var product = self.env.pos.db.get_product_by_id(self.env.pos.config.enable_journal_id)
                            if(self.env.pos.config.enable_journal_id[0]){
                                var cashregisters = null;
                                for ( var j = 0; j <  self.env.pos.payment_methods.length; j++ ) {
                                    if( self.env.pos.payment_methods[j].id === self.env.pos.config.enable_journal_id[0]){
                                        cashregisters = self.env.pos.payment_methods[j];
                                    }
                                }
                            }
                            if (vals){
                                if (cashregisters){
                                    order.add_paymentline(cashregisters);
                                    order.selected_paymentline.set_amount( Math.max(redeem_amount),0 );
                                    order.selected_paymentline.set_giftcard_line_code(code);
                                    order.set_redeem_giftcard(vals);
                                } 
                            }
                            this.trigger('close-popup');
                        }else{
                            self.env.pos.db.notification('danger',_t('Please enter amount below card value.'));
                        }
                    }else{
                        self.env.pos.db.notification('danger',_t('Please enter valid amount.'));
                    }
                }
            }
            async useWalletForPayment(self, lines, order)  {
                var defined_amount = 0.00
                if (this.currentOrder.get_due() < self.state.remaining_wallet_amount){
                    defined_amount = this.currentOrder.get_due()
                }
                if (self.state.remaining_wallet_amount < this.currentOrder.get_due()){
                    defined_amount = self.state.remaining_wallet_amount
                }
                const { confirmed,payload:wallet_amount } = await this.showPopup('WalletPopup', {
                    title: this.env._t('Pay with Wallet'),
                    confirmText: this.env._t('Use'),
                    customer: this.env.pos.get_order().get_client().name,
                    defined_amount: this.env.pos.format_currency_no_symbol(defined_amount),
                });
                if (confirmed){
                    if (wallet_amount.amount != 0){
                        if(order.get_client()){
                            var params = {
                                model: "res.partner",
                                method: "search_read",
                                domain: [['id', '=', order.get_client().id]],
                                fields:['remaining_wallet_amount']
                            }
                            // $('div.js_use_wallet').addClass('highlight');
                            this.rpc(params, {async: false})
                                .then(function(results){
                                _.each(results, function(result){
                                    var price = 0;
                                    if(0 != result.remaining_wallet_amount){
                                        var amount = self.env.pos.db.thousandsDecimalChanger(wallet_amount.amount)
                                        if( amount > result.remaining_wallet_amount || amount > order.get_due()){
                                            alert('You are not allow to use wallet amount Morethen remaining amount !!!');
                                        }else{
                                            order.set_used_amount_from_wallet(Math.abs(amount));
                                            order.set_type_for_wallet('change');
                                            var payment_method = _.find(self.env.pos.payment_methods, function(cashregister){
                                                return cashregister.id === self.env.pos.config.wallet_payment_method_id[0] ? cashregister : false;
                                            });
                                            if(payment_method){
                                                order.add_paymentline(payment_method);
                                                order.selected_paymentline.set_amount(amount);
                                                self.env.pos.load_new_partners()
                                                self.state.is_wallet = true
                                                self.render();
                                                return
                                            }
                                        }
                                    
                                    }else{
                                        alert('Wallet Is Empty !!!');
                                    }
                                });
                            });
                        }else{
                            self.env.pos.db.notification('danger',"Please select customer!");
                        }
                    }else{
                        alert('Wallet Is Empty !!!');
                    }
                }
            }
            async payment_back()  {
                var product_ids = [this.env.pos.config.wallet_product[0],this.env.pos.config.gift_card_product_id[0]]
                if(this.env.pos.get_order().get_orderlines().length != 0){
                    if(this.env.pos.config.wallet_product && this.env.pos.get_order().get_orderlines()[0].product.id == this.env.pos.config.wallet_product[0]){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('You do not go back'),
                            body: this.env._t(
                                'Would you like to discart this order?'
                            ),
                        });
                        if (confirmed) {
                            this.env.pos.get_order().destroy({ reason: 'abandon' });
                            posbus.trigger('order-deleted');
                            this.showScreen('ProductScreen')
                        }
                        
                    }else if(this.env.pos.config.gift_card_product_id[0] && this.env.pos.get_order().get_orderlines()[0].product.id == this.env.pos.config.gift_card_product_id[0]){
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('You do not go back'),
                            body: this.env._t(
                                'Would you like to discart this order?'
                            ),
                        });
                        if (confirmed) {
                            this.env.pos.get_order().destroy({ reason: 'abandon' });
                            posbus.trigger('order-deleted');
                            this.showScreen('ProductScreen')
                        }
                    }else{
                        this.showScreen('ProductScreen')
                    }
                }else{
                    this.showScreen('ProductScreen')
                }
            }
            async validateOrder(isForceValidate)  {
                var self = this
                var flage = false
                if(this.props.order_id){
                    var orders_list = this.env.pos.db.get_draft_orders_list();
                    orders_list = _.without(orders_list, _.findWhere(orders_list, { id: this.props.order_id }));
                    this.env.pos.db.add_draft_orders(orders_list);
                }
                const change = this.currentOrder.get_change();
                if(this.currentOrder.get_change() && this.env.pos.config.enable_wallet && this.currentOrder.get_client() && (this.currentOrder.get_type_for_wallet() != 'change')){
                    const {confirmed, skip, getPayload} = await this.showPopup('PaymentWalletPopup', {
                        title: this.env._t('Add to Wallet'),
                        change: this.env.pos.format_currency(this.currentOrder.get_change()),
                        nextScreen: this.nextScreen,
                        order: this,
                    });
                    if (confirmed){
                        return super.validateOrder();
                    }else if(skip){
                        return super.validateOrder();
                    }
                }else{
                    return super.validateOrder();
                }
                return super.validateOrder();
            }
        };

    Registries.Component.extend(PaymentScreen, AsplRetPaymentScreenInh);

    return PaymentScreen;
});
