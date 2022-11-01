odoo.define('custom_searchpanel.AbstractView', function (require) {
"use strict";

var AbstractView = require('web.AbstractView');
var SearchPanel = require('web.SearchPanel');

AbstractView.include({
    /**
     * @override
     */
    getController: function (parent) {
        var self = this;
        var cpDef = this.withControlPanel && this._createControlPanel(parent);
        var spDef;
        if (this.withSearchPanel) {
            var spProto = this.config.SearchPanel.prototype;
            var viewInfo = this.controlPanelParams.viewInfo;
            var searchPanelParams = spProto.computeSearchPanelParams(viewInfo, this.viewType);
            if (searchPanelParams.sections) {
                this.searchPanelParams.sections = searchPanelParams.sections;
                this.rendererParams.withSearchPanel = true;
                spDef = Promise.resolve(cpDef).then(this._createSearchPanel.bind(this, parent, searchPanelParams));
            }
            if (searchPanelParams.custom_sections) {
                this.searchPanelParams.custom_sections = searchPanelParams.custom_sections;
            }
        }

        var _super = this._super.bind(this);
        return Promise.all([cpDef, spDef]).then(function ([controlPanel, searchPanel]) {
            // get the parent of the model if it already exists, as _super will
            // set the new controller as parent, which we don't want
            var modelParent = self.model && self.model.getParent();
            var prom = _super(parent);
            prom.then(function (controller) {
                if (controlPanel) {
                    controlPanel.setParent(controller);
                }
                if (searchPanel) {
                    searchPanel.setParent(controller);
                }
                if (modelParent) {
                    // if we already add a model, restore its parent
                    self.model.setParent(modelParent);
                }
            });
            return prom;
        });
    },

});

});