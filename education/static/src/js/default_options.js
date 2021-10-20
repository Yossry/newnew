odoo.define('education.wysiwyg.root', function (require) {
'use strict';

var Widget = require('web.Widget');

var assetsLoaded = false;

var WysiwygRoot = Widget.extend({
    assetLibs: ['web_editor.compiled_assets_wysiwyg'],

    publicMethods: ['isDirty', 'save', 'getValue', 'setValue', 'getEditable', 'on', 'trigger', 'focus'],

    /**
     *   @see 'web_editor.wysiwyg' module
     **/
    init: function (parent, params) {
        this._super.apply(this, arguments);
        this._params = params;
        this.$editor = null;
    },
    /**
     * Load assets
     *
     * @override
     **/
    willStart: function () {
        var self = this;

        var $target = this.$el;
        this.$el = null;

        return this._super().then(function () {
            if (!assetsLoaded) {
                var Wysiwyg = odoo.__DEBUG__.services['web_editor.wysiwyg'];
                _.each(['getRange', 'setRange', 'setRangeFromNode'], function (methodName) {
                    WysiwygRoot[methodName] = Wysiwyg[methodName].bind(Wysiwyg);
                });
                assetsLoaded = true;
            }

            var Wysiwyg = self._getWysiwygContructor();
            var instance = new Wysiwyg(self, self._params);
            self._params = null;

            _.each(self.publicMethods, function (methodName) {
                self[methodName] = instance[methodName].bind(instance);
            });

            return instance.attachTo($target).then(function () {
                self.$editor = instance.$editor || instance.$el;
            });
        });
    },

    _getWysiwygContructor: function () {
        return odoo.__DEBUG__.services['web_editor.wysiwyg'];
    }
});

return WysiwygRoot;

});


odoo.define('education.wysiwyg.default_options', function (require) {
'use strict';

var core = require('web.core');

var _lt = core._lt;

return {
    styleTags: ['p', 'pre', 'small', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'],
    fontSizes: [_lt('Default'), 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32 ,33 ,34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 62],
};
});
