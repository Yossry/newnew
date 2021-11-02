/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_order_return.pos_order_return', function(require) {
    "use strict";
    var pos_orders = require('pos_orders.pos_orders');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var QWeb = core.qweb;
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var PopupWidget = require('point_of_sale.popups');
    var _t = core._t;
    var SuperOrder = models.Order;
    var SuperOrderline = models.Orderline.prototype;
    var SuperPosModel = models.PosModel.prototype;
    var field_utils = require('web.field_utils');
    var utils = require('web.utils')
    var round_pr = utils.round_precision;
    var SuperPaymentScreen = screens.PaymentScreenWidget.prototype;



    models.load_fields('product.product', 'not_returnable');
    var order_model = null;
    var order_line_model = null;
    var model_list = models.PosModel.prototype.models
    for (var i = 0, len = model_list.length; i < len; i++) {
        if (model_list[i].model == "pos.order") {
            order_model = model_list[i];
            if (order_line_model)
                break;
        } else if (model_list[i].model == "pos.order.line") {
            order_line_model = model_list[i];
            if (order_model)
                break;
        }
    }
    order_model.fields.push('return_order_id', 'payment_ids', 'is_return_order', 'return_status', 'amount_total');
    order_model.domain = function(self) {
        var domain_list = [];
        if (self.config.order_loading_options == 'n_days') {
            var today = new Date();
            var validation_date = new Date(today.setDate(today.getDate() - self.config.number_of_days)).toISOString();
            domain_list = [
                ['date_order', '>', validation_date],
                ['state', 'not in', ['draft', 'cancel']],
                ['is_return_order', '=', false]
            ]
        } else if (self.config.order_loading_options == 'current_session')
            domain_list = [
                ['session_id', '=', self.pos_session.name],
                ['state', 'not in', ['draft', 'cancel']],
                ['is_return_order', '=', false]
            ];
        else
            domain_list = [
                ['state', 'not in', ['draft', 'cancel']],
                ['is_return_order', '=', false]
            ]
        return domain_list;
    };
    order_line_model.fields.push('line_qty_returned');

    models.load_models([{
        model: 'pos.payment',
        fields: ['id', 'name', 'payment_method_id', 'amount'],
        loaded: function(self, payments) {
            self.db.all_payments = payments;
            self.db.payment_by_id = {};
            payments.forEach(function(payment) {
                self.db.payment_by_id[payment.id] = payment;
                self.db.payment_by_id[payment.id]['journal_id'] = payment.payment_method_id
                delete self.db.payment_by_id[payment.id]['payment_method_id']
            });
        },
    }]);

    var MyMessagePopup = PopupWidget.extend({
        template: 'MyMessagePopup'
    });
    gui.define_popup({ name: 'my_message', widget: MyMessagePopup });

    var OrderReturnPopup = PopupWidget.extend({
        template: 'OrderReturnPopup',
        events: {
            'click .button.cancel': 'click_cancel',
            'click #complete_return': 'click_complete_return',
            'click #return_order': 'click_return_order',
        },
        click_return_order: function() {
            var self = this;
            var all = $('.return_qty');
            var return_dict = {};
            var return_entries_ok = true;
            $.each(all, function(index, value) {
                var input_element = $(value).find('input');
                var line_quantity_remaining = parseFloat(input_element.attr('line-qty-remaining'));
                var line_id = parseFloat(input_element.attr('line-id'));
                var qty_input = parseFloat(input_element.val());
                if (!$.isNumeric(qty_input) || qty_input > line_quantity_remaining || qty_input < 0) {
                    return_entries_ok = false;
                    input_element.css("background-color", "#ff8888;");
                    setTimeout(function() {
                        input_element.css("background-color", "");
                    }, 100);
                    setTimeout(function() {
                        input_element.css("background-color", "#ff8888;");
                    }, 200);
                    setTimeout(function() {
                        input_element.css("background-color", "");
                    }, 300);
                    setTimeout(function() {
                        input_element.css("background-color", "#ff8888;");
                    }, 400);
                    setTimeout(function() {
                        input_element.css("background-color", "");
                    }, 500);
                }

                if (qty_input == 0 && line_quantity_remaining != 0 && !self.options.is_partial_return)
                    self.options.is_partial_return = true;
                else if (qty_input > 0) {
                    return_dict[line_id] = qty_input;
                    if (line_quantity_remaining != qty_input && !self.options.is_partial_return)
                        self.options.is_partial_return = true;
                    else if (!self.options.is_partial_return)
                        self.options.is_partial_return = false;
                }
            });
            if (return_entries_ok)
                self.create_return_order(return_dict);
        },
        create_return_order: function(return_dict) {
            var self = this;
            var order = self.options.order;
            var orderlines = self.options.orderlines;
            var current_order = self.pos.get_order();
            if (Object.keys(return_dict).length > 0) {
                self.chrome.widget.order_selector.neworder_click_handler();
                var refund_order = self.pos.get_order();
                refund_order.is_return_order = true;
                refund_order.set_client(self.pos.db.get_partner_by_id(order.partner_id[0]));
                Object.keys(return_dict).forEach(function(line_id) {
                    var line = self.pos.db.line_by_id[line_id];
                    var product = self.pos.db.get_product_by_id(line.product_id[0]);
                    refund_order.add_product(product, { quantity: -1 * parseFloat(return_dict[line_id]), price: line.price_unit, discount: line.discount });
                    refund_order.selected_orderline.original_line_id = line.id;
                });
                if (self.options.is_partial_return) {
                    refund_order.return_status = 'Partially-Returned';
                    refund_order.return_order_id = order.id;
                } else {
                    refund_order.return_status = 'Fully-Returned';
                    refund_order.return_order_id = order.id;
                }
                self.pos.set_order(refund_order);
                self.gui.show_screen('payment');
            } else {
                self.$("input").css("background-color", "#ff8888;");
                setTimeout(function() {
                    self.$("input").css("background-color", "");
                }, 100);
                setTimeout(function() {
                    self.$("input").css("background-color", "#ff8888;");
                }, 200);
                setTimeout(function() {
                    self.$("input").css("background-color", "");
                }, 300);
                setTimeout(function() {
                    self.$("input").css("background-color", "#ff8888;");
                }, 400);
                setTimeout(function() {
                    self.$("input").css("background-color", "");
                }, 500);
            }
        },
        click_complete_return: function() {
            var self = this;
            var all = $('.return_qty');
            $.each(all, function(index, value) {
                var line_quantity_remaining = parseFloat($(value).find('input').attr('line-qty-remaining'));
                $(value).find('input').val(line_quantity_remaining);
            });
        },
        show: function(options) {
            options = options || {};
            var self = this;
            this._super(options);
            this.orderlines = options.orderlines || [];
            this.renderElement();
        },
    });
    gui.define_popup({ name: 'return_products_popup', widget: OrderReturnPopup });

    screens.ClientListScreenWidget.include({
        show: function() {
            var self = this;
            var current_order = self.pos.get_order();
            self._super();
            if (current_order != null && current_order.is_return_order) {
                self.gui.back();
            }
        }
    });

    screens.PaymentScreenWidget.include({

        events: _.extend({}, SuperPaymentScreen.events, {
            'click .button.cancel_refund_order': 'delete_return_order',
        }),

        delete_return_order: function() {
            $(".deleteorder-button").trigger("click");
        },
        payment_input: function(input) {
            var self = this;
            self._super(input);
            var order = self.pos.get_order()
            var change = order.get_change();
            var buffer_amount = parseFloat(this.inputbuffer);
            if (order.is_return_order && change > 0 && order.get_total_with_tax() < 0) {
                var amount = (buffer_amount - change);
                this.inputbuffer = amount.toString();
                amount = field_utils.parse.float(this.inputbuffer);
                order.selected_paymentline.set_amount(amount);
                this.order_changes();
                this.render_paymentlines();
                this.$('.paymentline.selected .edit').text(this.format_currency_no_symbol(amount));
            }
        },
        show: function() {
			var self = this;
			self._super();
			if(self.pos.get_order() && self.pos.get_order().is_return_order && self.pos.get_order().get_total_with_tax() < 0){
				this.el.querySelector('.payment-screen h1').textContent = 'Refund';
				$('.button.cancel_refund_order').show();
			}
			else if(self.pos.get_order() && self.pos.get_order().is_return_order && self.pos.get_order().get_total_with_tax() > 0){
				this.el.querySelector('.payment-screen h1').textContent = 'Payment';
				$('.button.cancel_refund_order').show();
			}
			else
				$('.button.cancel_refund_order').hide();

        }
    });

    screens.ProductScreenWidget.include({
        show: function(reset) {
            var self = this;
            var current_order = self.pos.get_order();
            $("#cancel_refund_order").on("click", function() {
                $(".deleteorder-button").trigger("click");
            });
            this._super(reset);
            if (current_order != null && current_order.is_return_order && !current_order.is_exchange_order) {
                $('.product').css("pointer-events", "none");
                $('.product').css("opacity", "0.4");
                $('.header-cell').css("pointer-events", "none");
                $('.header-cell').css("opacity", "0.4");
                $('#refund_order_notify').show();
                $('#cancel_refund_order').show();
                self.$('.numpad-backspace').css("pointer-events", "none");
                self.$('.numpad').addClass('return_order_button');
                self.$('.numpad button').addClass('return_order_button');
                self.$('.button.set-customer').addClass('return_order_button');
                self.$('#all_orders').addClass('return_order_button');

            } else if (current_order != null && current_order.is_return_order && current_order.is_exchange_order) {
                self.$('.button.set-customer').addClass('return_order_button');
                self.$('#all_orders').addClass('return_order_button');
            } else {
                $('.product').css("pointer-events", "");
                $('.product').css("opacity", "");
                $('.header-cell').css("pointer-events", "");
                $('.header-cell').css("opacity", "");
                $('#refund_order_notify').hide();
                $('#cancel_refund_order').hide();
                self.$('.numpad-backspace').css("pointer-events", "");
                self.$('.numpad').removeClass('return_order_button');
                self.$('.numpad button').removeClass('return_order_button');
                self.$('.button.set-customer').removeClass('return_order_button');
                self.$('#all_orders').removeClass('return_order_button');

            }
        }
    });

    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            var self = this;
            this.line_qty_returned = 0;
            this.original_line_id = null;
            SuperOrderline.initialize.call(this, attr, options);
        },
        export_as_JSON: function() {
            var self = this;
            var loaded = SuperOrderline.export_as_JSON.call(this);
            loaded.line_qty_returned = self.line_qty_returned;
            loaded.original_line_id = self.original_line_id;
            return loaded;
        },
        can_be_merged_with: function(orderline) {
            var self = this;
            if (self.pos.get_order() && self.pos.get_order().is_return_order && self.quantity < 0)
                return false;
            else
                return SuperOrderline.can_be_merged_with.call(this, orderline);
        }
    });

    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            var self = this;
            self.return_status = '-';
            self.is_return_order = false;
            self.return_order_id = false;
            SuperOrder.prototype.initialize.call(this, attributes, options);
        },
        get_due: function(paymentline) {
            var self = this;
            if (self.is_return_order && this.get_total_with_tax() < 0) {
                if (!paymentline) {
                    var due = (Math.abs(this.get_total_with_tax()) - this.get_total_paid());
                } else {
                    var due = Math.abs(this.get_total_with_tax());
                    var lines = this.paymentlines.models;
                    for (var i = 0; i < lines.length; i++) {
                        if (lines[i] === paymentline) {
                            break;
                        } else {
                            due -= lines[i].get_amount();
                        }
                    }
                }
                return round_pr(Math.max(0, due), this.pos.currency.rounding);
            } else
                return SuperOrder.prototype.get_due.call(self, paymentline);

        },
        get_change: function(paymentline) {
            var self = this;
            if (self.is_return_order && this.get_total_with_tax() < 0) {
                if (!paymentline) {
                    var change = this.get_total_paid() - Math.abs(this.get_total_with_tax());
                } else {
                    var change = -Math.abs(this.get_total_with_tax());
                    var lines = this.paymentlines.models;
                    for (var i = 0; i < lines.length; i++) {
                        change += lines[i].get_amount();
                        if (lines[i] === paymentline) {
                            break;
                        }
                    }
                }
                return round_pr(Math.max(0, change), this.pos.currency.rounding);
            } else
                return SuperOrder.prototype.get_change.call(self, paymentline);
        },
        export_as_JSON: function() {
            var self = this;
            var loaded = SuperOrder.prototype.export_as_JSON.call(this);
            var current_order = self.pos.get_order();
            if (self.pos.get_order() != null) {
                loaded.is_return_order = current_order.is_return_order;
                loaded.return_status = current_order.return_status;
                loaded.return_order_id = current_order.return_order_id;
            }
            return loaded;
        },
    });

    screens.NumpadWidget.include({
        clickAppendNewChar: function(event) {
            var self = this;
            if (!self.pos.get_order().is_return_order || (self.pos.get_order().is_exchange_order && self.pos.get_order().selected_orderline && !self.pos.get_order().selected_orderline.original_line_id))
                self._super(event);
        },
        clickSwitchSign: function() {
            var self = this;
            if (!self.pos.get_order().is_return_order || (self.pos.get_order().is_exchange_order && self.pos.get_order().selected_orderline && !self.pos.get_order().selected_orderline.original_line_id))
                self._super();

        },
        clickDeleteLastChar: function() {
            var self = this;
            if (!self.pos.get_order().is_return_order || (self.pos.get_order().is_exchange_order && self.pos.get_order().selected_orderline && !self.pos.get_order().selected_orderline.original_line_id))
                self._super();
        },
    });

    models.PosModel = models.PosModel.extend({
        set_order: function(order) {
            SuperPosModel.set_order.call(this, order);
            if (order != null && !order.is_return_order || order.is_exchange_order) {
                $("#cancel_refund_order").hide();
            } else {
                $("#cancel_refund_order").show();
            }
        },
    });

    pos_orders.include({
        line_select: function(event, $line, id) {
            var self = this;
            var order = self.pos.db.order_by_id[id];
            this.$('.wk_order_list .lowlight').removeClass('lowlight');
            if ($line.hasClass('highlight')) {
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.display_order_details('hide', order);
            } else {
                this.$('.wk_order_list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                self.selected_tr_element = $line;
                var y = event.pageY - $line.parent().offset().top;
                self.display_order_details('show', order, y);
            }
        },
        display_order_details: function(visibility, order, clickpos) {
            var self = this;
            var contents = this.$('.order-details-contents');
            var parent = this.$('.wk_order_list').parent();
            var scroll = parent.scrollTop();
            var height = contents.height();
            var orderlines = [];
            var statements = [];
            var payment_methods_used = [];
            if (visibility === 'show') {
                order.lines.forEach(function(line_id) {
                    orderlines.push(self.pos.db.line_by_id[line_id]);
                });
                if(order && order.payment_ids)
                    order.payment_ids.forEach(function(payment_id) {
                        var payment = self.pos.db.payment_by_id[payment_id];
                        statements.push(payment);
                        payment_methods_used.push(payment.journal_id[0]);
                    });
                contents.empty();
                contents.append($(QWeb.render('OrderDetails', { widget: this, order: order, orderlines: orderlines, statements: statements })));
                var new_height = contents.height();
                if (!this.details_visible) {
                    if (clickpos < scroll + new_height + 20) {
                        parent.scrollTop(clickpos - 20);
                    } else {
                        parent.scrollTop(parent.scrollTop() + new_height);
                    }
                } else {
                    parent.scrollTop(parent.scrollTop() - height + new_height);
                }
                this.details_visible = true;
                self.$("#close_order_details").on("click", function() {
                    self.selected_tr_element.removeClass('highlight');
                    self.selected_tr_element.addClass('lowlight');
                    self.details_visible = false;
                    self.display_order_details('hide', null);
                });
                self.$("#wk_refund").on("click", function() {
                    var order_list = self.pos.db.pos_all_orders;
                    var order_line_data = self.pos.db.pos_all_order_lines;
                    var order_id = this.id;
                    var message = '';
                    var non_returnable_products = false;
                    var original_orderlines = [];
                    var allow_return = true;
                    if (order.return_status == 'Fully-Returned') {
                        message = 'No items are left to return for this order!!'
                        allow_return = false;
                    }
                    var all_pos_orders = self.pos.get('orders').models || [];
                    var return_order_exist = _.find(all_pos_orders, function(pos_order) {
                        if (pos_order.return_order_id && pos_order.return_order_id == order.id)
                            return pos_order;

                    });
                    if (return_order_exist) {
                        self.gui.show_popup('my_message', {
                            'title': _t('Refund Already In Progress'),
                            'body': _t("Refund order is already in progress. Please proceed with Order Reference " + return_order_exist.sequence_number),
                        });
                    } else if (allow_return) {
                        order.lines.forEach(function(line_id) {
                            var line = self.pos.db.line_by_id[line_id];
                            var product = self.pos.db.get_product_by_id(line.product_id[0]);
                            if (product == null) {
                                non_returnable_products = true;
                                message = 'Some product(s) of this order are unavailable in Point Of Sale, do you wish to return other products?'
                            } else if (product.not_returnable) {
                                non_returnable_products = true;
                                message = 'This order contains some Non-Returnable products, do you wish to return other products?'
                            } else if (line.qty - line.line_qty_returned > 0)
                                original_orderlines.push(line);
                        });
                        if (original_orderlines.length == 0) {
                            self.gui.show_popup('my_message', {
                                'title': _t('Cannot Return This Order!!!'),
                                'body': _t("There are no returnable products left for this order. Maybe the products are Non-Returnable or unavailable in Point Of Sale!!"),
                            });
                        } else if (non_returnable_products) {
                            self.gui.show_popup('confirm', {
                                'title': _t('Warning !!!'),
                                'body': _t(message),
                                confirm: function() {
                                    self.gui.show_popup('return_products_popup', {
                                        'orderlines': original_orderlines,
                                        'order': order,
                                        'is_partial_return': true,
                                    });
                                },
                            });
                        } else {
                            self.gui.show_popup('return_products_popup', {
                                'orderlines': original_orderlines,
                                'order': order,
                                'is_partial_return': false,
                            });
                        }
                    } else {
                        self.gui.show_popup('my_message', {
                            'title': _t('Warning!!!'),
                            'body': _t(message),
                        });
                    }
                });
            }
            if (visibility === 'hide') {
                contents.empty();
                if (height > scroll) {
                    contents.css({ height: height + 'px' });
                    contents.animate({ height: 0 }, 400, function() {
                        contents.css({ height: '' });
                    });
                } else {
                    parent.scrollTop(parent.scrollTop() - height);
                }
                this.details_visible = false;
            }
        },
        show: function() {
            var self = this;
            this._super();
            var self = this;
            this.details_visible = false;
            this.selected_tr_element = null;
            self.$('.wk-order-list-contents').delegate('.wk-order-line', 'click', function(event) {
                // --------------code for POS Order Reprint-----------------------
                if (!(event.target && event.target.nodeName == 'BUTTON')) {
                    self.line_select(event, $(this), parseInt($(this).data('id')));
                }
                // --------------End code for POS Order Reprint-----------------------

            });
            var contents = this.$('.order-details-contents');
            contents.empty();
            var parent = self.$('.wk_order_list').parent();
            parent.scrollTop(0);
        },
    });
});