odoo.define('education.product_configurator', function (require) {
var ProductConfiguratorWidget = require('sale.product_configurator');

/**
 * Extension of the ProductConfiguratorWidget to support event product configuration.
 * It opens when an event product_product is set.
 *
 * The event information include:
 * - session_id
 * - event_ticket_id
 *
 */
ProductConfiguratorWidget.include({
    /**
     * @returns {boolean}
     *
     * @override
     * @private
     */
    _isConfigurableLine: function () {
        return this.recordData.session_ok || this._super.apply(this, arguments);
    },

    /**
     * @param {integer} productId
     * @param {String} dataPointID
     * @returns {Promise<Boolean>} stopPropagation true if a suitable configurator has been found.
     *
     * @override
     * @private
     */
    _onProductChange: function (productId, dataPointId) {
      var self = this;
      return this._super.apply(this, arguments).then(function (stopPropagation) {
          if (stopPropagation) {
              return Promise.resolve(true);
          } else {
              return self._checkForSession(productId, dataPointId);
          }
      });
    },

    /**
     * This method will check if the productId needs configuration or not:
     *
     * @param {integer} productId
     * @param {string} dataPointID
     * @returns {Promise<Boolean>} stopPropagation true if the product is an event ticket.
     *
     * @private
     */
    _checkForSession: function (productId, dataPointId) {
        var self = this;
        return this._rpc({
            model: 'product.product',
            method: 'read',
            args: [productId, ['session_ok']],
        }).then(function (result) {
            if (result && result[0].session_ok) {
                self._openSessionConfigurator({
                        default_product_id: productId
                    },
                    dataPointId
                );
                return Promise.resolve(true);
            }
            return Promise.resolve(false);
        });
    },

    /**
     * Opens the event configurator in 'edit' mode.
     *
     * @override
     * @private
     */
    _onEditLineConfiguration: function () {
        if (this.recordData.session_ok) {
            var defaultValues = {
                default_product_id: this.recordData.product_id.data.id,
            };

            if (this.recordData.session_id) {
                defaultValues.default_session_id = this.recordData.session_id.data.id;
            }

            this._openSessionConfigurator(defaultValues, this.dataPointID);
        } else {
            this._super.apply(this, arguments);
        }
    },

    /**
     * Opens the event configurator to allow configuring the SO line with events information.
     *
     * When the window is closed, configured values are used to trigger a 'field_changed'
     * event to modify the current SO line.
     *
     * If the window is closed without providing the required values 'session_id' and
     * 'event_ticket_id', the product_id field is cleaned.
     *
     * @param {Object} data various "default_" values
     * @param {string} dataPointId
     *
     * @private
     */
    _openSessionConfigurator: function (data, dataPointId) {
        var self = this;
        this.do_action('education.session_configurator_action', {
            additional_context: data,
            on_close: function (result) {
	            console.log(data);
                if (result && !result.special) {
                    self.trigger_up('field_changed', {
                        dataPointID: dataPointId,
                        changes: result.sessionConfiguration,
                        onSuccess: function () {
                            // Call post-init function.
                            self._onLineConfigured();
                        }
                    });
                } else {
                    if (!self.recordData.session_id) {
                        self.trigger_up('field_changed', {
                            dataPointID: dataPointId,
                            changes: {
                                product_id: false,
                                name: 'Test'
                            },
                        });
                    }
                }
            }
        });
    }
});


return ProductConfiguratorWidget;

});
