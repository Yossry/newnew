odoo.define('education.SessionConfiguratorFormView', function (require) {
"use strict";

var SessionConfiguratorFormController = require('education.SessionConfiguratorFormController');
var FormView = require('web.FormView');
var viewRegistry = require('web.view_registry');

/**
 * @see EventConfiguratorFormController for more information
 */
var SessionConfiguratorFormView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
        Controller: SessionConfiguratorFormController
    }),
});

viewRegistry.add('session_configurator_form', SessionConfiguratorFormView);

return SessionConfiguratorFormView;

});
