    odoo.define('aspl_gift_card.giftCardCreateScreen', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useRef, useState } = owl.hooks;


    class giftCardCreateScreen extends PosComponent {
        guidGenerator() {
            return (new Date().getUTCMilliseconds().toString() + new Date().getTime().toString());
        }
        expDateCal() {
            var date = new Date();
            if (this.env.pos.config.default_exp_date <= 0) {
                return ''
            }else{
                date.setMonth(date.getMonth() + this.env.pos.config.default_exp_date);
            }
            var new_date = date.getFullYear()+ "/" +(date.getMonth() + 1)+ "/" +date.getDate();
            moment(date).locale('en').format('MM/DD/yyyy')
            return moment(date).locale('en').format('MM/DD/YYYY')
        }
        constructor(){
            super(...arguments);
            if (this.env.pos.config.manual_card_number){
                this.state = useState({CardNumber:'', SelectCustomer:'', ExpireDate:this.expDateCal(), Amount:"", SelectCardType:"", Paid:''});
            }else{
                this.state = useState({CardNumber:this.guidGenerator(), SelectCustomer:'', ExpireDate:this.expDateCal(), Amount:"", SelectCardType:"", Paid:''});
            }
            this.card_no = useRef('CardNumber');
            this.select_customer = useRef('SelectCustomer');
            this.text_expire_date = useRef('ExpireDate');
            this.text_amount = useRef('Amount');
            this.SelectCardType = useRef('SelectCardType');
            this.Paid = useRef('Paid');
        }
        mounted() {
            this.select_customer;
        }
        onInputKeyDownNumberVlidation(e) {
           if(e.which != 110 && e.which != 8 && e.which != 0 && e.key != this.env.pos.db.decimalSeparator() && e.key != this.env.pos.db.decimalSeparator() && (e.which < 48 || e.which > 57 || e.shiftKey) && (e.which < 96 || e.which > 105) && (e.which < 37 || e.which > 40)) {
                e.preventDefault();
            }
        }
        back() {
            this.trigger('close-temp-screen');
        }
        async confirm() {
            var SelectedCustomer = $('option[value="'+$('#select_customer').val()+'"]').attr('id')
            if(this.state.CardNumber && this.state.CardNumber.toString().length >= 12){
                let cardExist = await this.isCardExist(this.state.CardNumber);
                if(cardExist !== undefined){
                    this.env.pos.db.notification('danger', _t('Card Number Already Exist!'));
                    return;
                }
            }
            if(this.state.CardNumber && this.state.CardNumber.toString().length < 12){
                this.env.pos.db.notification('warning', _t('Card Number Should be 12 Digit or more!'));
                return;
            }else if(!SelectedCustomer || this.state.SelectCustomer == ''){
                this.env.pos.db.notification('danger', _t('Please Select Customer!'));
                return;
            }else if(this.env.pos.config.default_exp_date <= 0 && (this.state.ExpireDate == '' || this.state.ExpireDate < moment().locale('en').format('YYYY-MM-DD'))){
                this.env.pos.db.notification('danger', _t('Please Enter Valid Expiry Date!'));
                return;
            }else {
                this.state.SelectCustomer = $('option[value="'+$('#select_customer').val()+'"]').attr('id')
                this.props.resolve({ confirmed: true, payload:{card_no: this.state.CardNumber, customer_id: this.state.SelectCustomer, expire_date: moment(this.state.ExpireDate).locale('en').format('YYYY-MM-DD'), card_value: this.state.Amount, card_type: this.state.SelectCardType,} });
                this.trigger('close-temp-screen');
            }
        }
        isCardExist(code){
            return this.rpc({
                model: 'aspl.gift.card',
                method: 'search_read',
                domain: [['card_no', '=', code]],
            }, {async: true}).then((result) => {
                if(result && result.length > 0){
                    return true;
                }else{
                    return;
                }
            })
        }
        clickNext() {
            this.confirm();
        }
    }

    giftCardCreateScreen.template = 'giftCardCreateScreen';

    Registries.Component.add(giftCardCreateScreen);

    return giftCardCreateScreen;
});
