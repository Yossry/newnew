odoo.define('pos_order_reprint.pos_order_reprint', function(require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var pos_orders = require('pos_orders.pos_orders');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;

    var ReprintTicketScreenWidget = screens.ScreenWidget.extend({
        template: 'ReprintTicketScreenWidget',
        show: function() {
            var self = this;
            self._super();
            $('.button.back.wk_reprint_back').on("click", function() {
                self.gui.show_screen('wk_order');
            });
            $('.button.back.wk_reprint_home').on("click", function() {
                self.gui.show_screen('products');
            });
            $('.button.print').click(function() {
                var test = self.chrome.screens.receipt;
                setTimeout(function() {
                    self.chrome.screens.receipt.lock_screen(false);
                }, 1000);
                if (!test['_locked']) {
                    self.chrome.screens.receipt.print_web();
                    self.chrome.screens.receipt.lock_screen(true);
                }
            });
        }
    });
    gui.define_screen({ name: 'reprint_ticket', widget: ReprintTicketScreenWidget });

    pos_orders.include({
        show: function() {
            var self = this;
            self._super();
            
            self.$('.wk-order-list-contents').delegate('.wk_print_content', 'click', function(event){
                var order_id = parseInt(this.id);
                if(self.pos.config.wk_reprint_type != 'pdf'){
                    rpc.query({
                        model:'pos.order',
                        method:'get_report_data',
                        args: [{ 'order_id': order_id }]
                    })
                    .then(function(result) {
                        var cashier = self.pos.cashier || self.pos.user;
                        var company = self.pos.company;
                        result['pos'] = self.pos;
                        result['receipt']['header'] = self.pos.config.receipt_header || '';
                        result['receipt']['footer'] = self.pos.config.receipt_footer || '';
                        result['receipt']['curr_user'] = cashier ? cashier.name : null;
                        result['receipt']['shop'] = self.pos.shop;
                        result['receipt']['pos'] = self.pos;
                        result['receipt']['company'] = {
                            email: company.email,
                            website: company.website,
                            company_registry: company.company_registry,
                            contact_address: company.partner_id[1],
                            vat: company.vat,
                            name: company.name,
                            phone: company.phone,
                            logo: self.pos.company_logo_base64,
                        };
                        var wk_pos_order = self.pos.db.order_by_id[order_id];
                        result['receipt']['date'] = {
                            localestring: wk_pos_order?wk_pos_order.date_order:result['receipt']['date'],
                        };

                        if (self.pos.config.wk_reprint_type == 'ticket') {
                            console.log("result.receipt",result.receipt)
                            console.log("result.receipt",self)
                            $('.pos-receipt-container').html(QWeb.render('webkul_pos_ticket', {
                                widget: self,
                                receipt: result.receipt,
                            }));
                            self.gui.show_screen("reprint_ticket");
                        } else {
                            var receipt = QWeb.render('webkulXmlReceipt', result);
                            self.pos.proxy.print_receipt(receipt);
                        }
                    });
                }
                else{
                    setTimeout(function(){
                        self.chrome.do_action('pos_order_reprint.reprint_report',{additional_context:{ 
                            active_ids:[order_id],
                        }})
                        .guardedCatch(function(err){
                            self.gui.show_popup('error',{
                                'title': _t('The order could not be printed'),
                                'body': _t('Check your internet connection and try again.'),
                            });
                        });
                    },500)
                }
            });
            
        },
    });
});
