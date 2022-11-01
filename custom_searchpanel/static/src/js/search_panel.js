odoo.define('custom_searchpanel.SearchPanel', function (require) {
"use strict";

var SearchPanel = require('web.SearchPanel');
var viewUtils = require('web.viewUtils');
var defaultViewTypes = ['kanban', 'tree'];

function _processSearchPanelNode(node, fields) {
    var sections = {};
    node.children.forEach((childNode, index) => {
        if (childNode.tag !== 'field') {
            return;
        }
        if (childNode.attrs.invisible === "1") {
            return;
        }
        var fieldName = childNode.attrs.name;
        var type = childNode.attrs.select === 'multi' ? 'filter' : 'category';

        var sectionId = _.uniqueId('section_');
        var section = {
            color: childNode.attrs.color,
            description: childNode.attrs.string || fields[fieldName].string,
            fieldName: fieldName,
            icon: childNode.attrs.icon,
            id: sectionId,
            index: index,
            type: type,
        };
        if (section.type === 'category') {
            section.icon = section.icon || 'fa-folder';
        } else if (section.type === 'filter') {
            section.disableCounters = !!pyUtils.py_eval(childNode.attrs.disable_counters || '0');
            section.domain = childNode.attrs.domain || '[]';
            section.groupBy = childNode.attrs.groupby;
            section.icon = section.icon || 'fa-filter';
        }
        sections[sectionId] = section;
    });
    return sections;
}

SearchPanel.include({
    /**
     * @override
     */
    init: function (parent, params) {
        this._super.apply(this, arguments);
        this.custom_searchpanel = params.custom_sections;
    },

    willStart: function () {
        var self = this;
        var loadCategoriesProm;
        if (this.initialState) {
            this.filters = this.initialState.filters;
            this.categories = this.initialState.categories;
        } else {
            loadCategoriesProm = this._fetchCategories().then(function () {
                return self._fetchFilters().then(self._applyDefaultFilterValues.bind(self));
            });
        }
        this.custom_searchpanel = this._fetch_custom_searchpanel()
        return Promise.all([loadCategoriesProm, this._super.apply(this, arguments)]);
    },

    /**
     * @override
     */
    computeSearchPanelParams: function (viewInfo, viewType) {
        var searchPanelSections;
        var searchPanelCustomSections = [];
        var classes;
        if (viewInfo) {
            var arch = viewUtils.parseArch(viewInfo.arch);
            viewType = viewType === 'list' ? 'tree' : viewType;
            arch.children.forEach(function (node) {
                if (node.tag === 'searchpanel') {
                    var attrs = node.attrs;
                    var viewTypes = defaultViewTypes;
                    if (attrs.view_types) {
                        viewTypes = attrs.view_types.split(',');
                    }
                    if (attrs.class) {
                        classes = attrs.class.split(' ');
                    }
                    if (viewTypes.indexOf(viewType) !== -1) {
                        var filtered_node = []
                        filtered_node = JSON.parse(JSON.stringify(node));
                        for (var i=0;i<node.children.length;i++){
                            if(node.children[i].attrs.widget !== undefined)
                                filtered_node.children.pop(node.children[i].attrs);
                        }
                        searchPanelSections = _processSearchPanelNode(filtered_node, viewInfo.fields);
                    }
                }
                if (node.tag === 'searchpanel') {
                    for (var i=0;i<node.children.length;i++){
                        if(node.children[i].attrs.widget !== undefined)
                            searchPanelCustomSections.push(node.children[i].attrs);
                    }
                }
            });
        }
        return {
            sections: searchPanelSections,
            custom_sections: searchPanelCustomSections,
            classes: classes,
        };
    },
    /**
     * @override
     */
    _render: function () {
        var self = this;
        this.$el.empty();

        // sort categories and filters according to their index
        var categories = Object.keys(this.categories).map(function (categoryId) {
            return self.categories[categoryId];
        });
        var filters = Object.keys(this.filters).map(function (filterId) {
            return self.filters[filterId];
        });
        var sections = categories.concat(filters).sort(function (s1, s2) {
            return s1.index - s2.index;
        });
        var custom_searchpanel = Object.keys(this.custom_searchpanel).map(function (filterId) {
            return self.custom_searchpanel[filterId];
        });

        sections.forEach(function (section) {
            if (Object.keys(section.values).length) {
                if (section.type === 'category') {
                    self.$el.append(self._renderCategory(section));
                } else {
                    self.$el.append(self._renderFilter(section));
                }
            }
        });

        if (custom_searchpanel.length) {
            self._renderCustomPanel(custom_searchpanel);
        }

    },

    _fetch_custom_searchpanel: function () {
        var self = this;
        var proms = Object.keys(this.custom_searchpanel).map(function (categoryId) {
            var categoriesProm;
                categoriesProm = self._rpc({
                    model: 'custom.searchpanel',
                    method: 'search',
                    fields: JSON.parse(self.custom_searchpanel[categoryId].widget).fields,
                    args: [[], self.custom_searchpanel[categoryId].widget, self.model],
                }).then(function (result) {
                    return result.values;
                });
            return categoriesProm
        });
        return Promise.all(proms);
    },

    _renderCustomPanel: function (custom_values) {
        this.$el.append(qweb.render('CustomPanel', {custom_values: custom_values}));
    },


});

});