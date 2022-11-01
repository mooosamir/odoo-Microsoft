odoo.define('vision_web.vision_web_import', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var vision_web_import = AbstractAction.extend({
        template: 'vision_web_wizard',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'change .category': 'category_changed',
            'change .lens_sub_category': 'sub_category_changed',
            'change .treatment_sub_category': 'sub_category_changed',
            'change .treatment_selection': 'selection_changed',
            'change .lens_selection': 'selection_changed',
            'keyup .sub_category_search': 'sub_category_search',
            'keyup .selection_search': 'selection_search',

            'click #vw_import': 'import_clicked',
            'click #vw_cancel': 'cancel_clicked',
        },
        start: function () {
            return this._super();
        },
        willStart: function() {
            var self = this;
            return Promise.all([
                    this._super.apply(this, arguments),
                    self._rpc({model: 'vision.web', method: 'get_api_data', args : [[]]})
                        .then(function (sub_categories) {
                            self.lens_sub_categories = sub_categories[0];
                            self.lens_treatment_sub_categories = sub_categories[1];
                            self.lens_add_ids = sub_categories[2];
                        }),
                    self._rpc({model: 'vision.web', method: 'get_vendors', args : [[]]})
                        .then(function (vendors) {self.vendors = vendors;}),
                    ]);
        },
        init: function(parent, args) {
            var self = this;
            this.categories = [{'id': 0,'name': 'Lenses'},{'id': 1,'name': 'Lenses Treatments'}];
            this.lens_treatment_sub_categories = [];
            this.lens_sub_categories = [];
            this.lens_add_ids = [];
            this.vendors = [];
            this.lens_imported_selections = {};
            this.treatment_imported_selections = {};
            this._super(parent, args);
            this.controlPanelParams.context.dialog_size = 'extra-large';
            this.controlPanelParams.context.renderFooter = false;
        },
        sub_category_search: function(ev){
            var sub_categories = [];
            var found_sub_categories = [];
            if ($('.category:checked').attr('value') == 'Lenses')
                sub_categories = this.lens_sub_categories;
            else if ($('.category:checked').attr('value') == 'Lenses Treatments')
                sub_categories = this.lens_treatment_sub_categories;
            if (sub_categories.length){
                $('.selection_search').val('');
//                $('.sub_category_search').val('');
                $('#sub_category .radio_into_button').html('');
                for (var i=0;i<sub_categories.length;i++){
                    if (sub_categories[i]['name'].toUpperCase().includes($(ev.currentTarget).val().toUpperCase()))
                        found_sub_categories.push(sub_categories[i])
                }
                if ($('.category:checked').attr('value') == 'Lenses')
                    $('#sub_category .radio_into_button').html($($(QWeb.render("vision_web.add_lens_sub_categories", {sub_categories:found_sub_categories}))));
                else if ($('.category:checked').attr('value') == 'Lenses Treatments')
                    $('#sub_category .radio_into_button').html($($(QWeb.render("vision_web.add_treatment_sub_categories", {sub_categories:found_sub_categories}))));
            }

        },
        selection_search: function(ev){
            var selections = [];
            var found_selections = [];
            if ($('.category:checked').attr('value') == 'Lenses')
                selections = JSON.parse($('.lens_sub_category:checked').attr('selection'));
            else if ($('.category:checked').attr('value') == 'Lenses Treatments')
                selections = JSON.parse($('.treatment_sub_category:checked').attr('selection'));
            if (selections.length){
//                $('.selection_search').val('');
                $('#selection .radio_into_button').html('');
                if ($('.category:checked').attr('value') == 'Lenses')
                    for (var i=0;i<selections.length;i++){
                        if (selections[i]['name'].toUpperCase().includes($(ev.currentTarget).val().toUpperCase()))
                            found_selections.push(selections[i])
                    }
                else if ($('.category:checked').attr('value') == 'Lenses Treatments')
                    for (var i=0;i<selections.length;i++){
                        if (selections[i]['Description'].toUpperCase().includes($(ev.currentTarget).val().toUpperCase()))
                            found_selections.push(selections[i])
                    }
                if ($('.category:checked').attr('value') == 'Lenses')
                    $('#selection .radio_into_button').html($($(QWeb.render("vision_web.add_lens_selections", {selections:found_selections}))));
                else if ($('.category:checked').attr('value') == 'Lenses Treatments')
                    $('#selection .radio_into_button').html($($(QWeb.render("vision_web.add_treatment_selections", {selections:found_selections}))));
            }

        },
        category_changed: function(ev){
            var self = this;
            $('#selection .radio_into_button').html('');
            if ($(ev.currentTarget).attr('value') == 'Lenses')
                $('#sub_category .radio_into_button').html($($(QWeb.render("vision_web.add_lens_sub_categories", {sub_categories:this.lens_sub_categories}))));
            else
                $('#sub_category .radio_into_button').html($($(QWeb.render("vision_web.add_treatment_sub_categories", {sub_categories:this.lens_treatment_sub_categories}))));
        },
        sub_category_changed: function(ev){
            var self = this;
            if ($('.category:checked').attr('value') == 'Lenses')
                $('#selection .radio_into_button').html($($(QWeb.render("vision_web.add_lens_selections", {selections:JSON.parse($(ev.currentTarget).attr('selection'))}))));
            else
                $('#selection .radio_into_button').html($($(QWeb.render("vision_web.add_treatment_selections", {selections:JSON.parse($(ev.currentTarget).attr('selection'))}))));
        },
        selection_changed: function(ev){
            var self = this;
            if ($('.category:checked').attr('value') == 'Lenses'){
                if ($(ev.currentTarget).prop('checked')){
                    var key = $('.lens_sub_category:checked').attr('id') + "_" + $(ev.currentTarget).attr('id');
                    this.lens_imported_selections[key] =  JSON.parse($(ev.currentTarget).attr('data-json'));
                    this.lens_imported_selections[key].category = $('.category:checked').attr('value');
                    this.lens_imported_selections[key].sub_category =  $('.lens_sub_category:checked').attr('id');
                }
                else
                    if (this.lens_imported_selections.hasOwnProperty($('.lens_sub_category:checked').attr('id') + "_" + $(ev.currentTarget).attr('id')))
                        delete this.lens_imported_selections[$('.lens_sub_category:checked').attr('id') + "_" + $(ev.currentTarget).attr('id')]
            }
            else{
                if ($(ev.currentTarget).prop('checked')){
                    var key = $('.treatment_sub_category:checked').attr('id') + "_" + $(ev.currentTarget).attr('id');
                    this.treatment_imported_selections[key] =  JSON.parse($(ev.currentTarget).attr('data-json'));
                    this.treatment_imported_selections[key].category = $('.category:checked').attr('value');
                    this.treatment_imported_selections[key].sub_category =  $('.treatment_sub_category:checked').attr('id');
                }
                else
                    if (this.treatment_imported_selections.hasOwnProperty($('.treatment_sub_category:checked').attr('id')  + "_" + $(ev.currentTarget).attr('id')))
                        delete this.treatment_imported_selections[$('.treatment_sub_category:checked').attr('id')  + "_" + $(ev.currentTarget).attr('id')];
            }
        },
        cancel_clicked: function(ev){
            var self = this;
            self.do_action({
                type: 'ir.actions.act_window_close'
            })
        },
        import_clicked: function(ev){
            var self = this;
            self._rpc({model: 'vision.web', method: 'import_lens', args : [[], this.lens_imported_selections, this.treatment_imported_selections, this.lens_add_ids]})
                .then(function (response) {
                    if (response){
                        alert("Data imported.")
                        self.do_action({
                            type: 'ir.actions.act_window_close'
                        })
                    }
                    else
                        alert('Server error, try again in a few seconds')
                });
        },
    });

    core.action_registry.add("vision_web_import", vision_web_import);
    return vision_web_import;
});