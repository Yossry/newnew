odoo.define('education.SessionConfiguratorFormController', function (require) {
"use strict";

var FormController = require('web.FormController');

/**
 * This controller is overridden to allow configuring sale_order_lines through a popup
 * window when a product with 'event_ok' is selected.
 *
 * This allows keeping an editable list view for sales order and remove the noise of
 * those 2 fields ('event_id' + 'event_ticket_id')
 */
var SessionConfiguratorFormController = FormController.extend({
    /**
     * We let the regular process take place to allow the validation of the required fields
     * to happen.
     *
     * Then we can manually close the window, providing event information to the caller.
     *
     * @override
     */
    saveRecord: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            var state = self.renderer.state.data;
            console.log(state);
            self.do_action({type: 'ir.actions.act_window_close', infos: {
                sessionConfiguration: {
                    session_id: {id: state.session_id.data.id},
                }
            }});
        });
    }
});

return SessionConfiguratorFormController;

});