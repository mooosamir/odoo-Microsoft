odoo.define('frames_data.frames_data_import', function (require) {
"use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var frames_data_import = AbstractAction.extend({
        template: 'frames_data_wizard',
        hasControlPanel: false,
        loadControlPanel: false,
        withSearchBar: false,
        events: {
            'change .main_style': 'main_style_changed',
            'change .add_manufacturer_collections .checkbox': 'manufacturer_collections_changed',
            'click #select_all': 'select_all_clicked',
            'click #fd_import': 'import_clicked',
            'click #fd_synchronize': 'synchronize_clicked',
            'click #fd_synchronize_existing': 'synchronize_existing_clicked',
        },

        willStart: function() {
            var self = this;
            return Promise.all([
                this._super.apply(this, arguments),
                self._rpc({model: 'frames.data', method: 'get_manufacturers_and_collections', args : [[]]})
                    .then(function (manufacturer_collections) {self.manufacturer_collections = manufacturer_collections;}),
                self._rpc({model: 'frames.data', method: 'get_vendors', args : [[]]})
                    .then(function (vendors) {self.vendors = vendors;}),
                ]);
        },
        init: function(parent, args) {
            var self = this;
            this.data_table;
            this.vendors = [];
//            this.collections = [];
//            this.manufacturers = [];
            this.manufacturer_collections = [];
            this.select_all = true;
            this.cfmid = [];
            this._super(parent, args);
        },
        start: function () {
            var res = this._super();
            this.data_table = this.$el.find('.add_manufacturer_collections table').DataTable({
                paging: false,
                searching: false,
                columnDefs: [
                  { "orderDataType": "dom-checkbox", "targets": 0 }
                ],
            });
            return res;
        },
        manufacturer_collections_changed: function(ev){
            if (ev.currentTarget == undefined)
                var cfmid = $(ev);
            else
                var cfmid = $(ev.currentTarget);

            var row = cfmid.closest('tr');
            var hmc = row.find(':checkbox:checked').length;
            var kluj = parseInt(hmc);
            row.find('td.counter').text(kluj);
            this.data_table.row(row).invalidate('dom');

//            if (cfmid.prop('checked')){
//                if (!this.cfmid.includes(cfmid.attr('data-cfmid')))
//                    this.cfmid.push(cfmid.attr('data-cfmid'));
//            }
//            else {
//                var index = this.cfmid.indexOf(cfmid);
//                if (index > -1)
//                  this.cfmid.splice(index, 1);
//            }
        },
        main_style_changed: function(ev){
            var self = this;
            var arrow = $(ev.currentTarget).parent().parent().parent().find('.arrow');
            if ($(ev.currentTarget).prop('checked') && $(ev.currentTarget).attr('data-sfmid')){
                arrow[0].style.display = '';
                this._rpc({model: 'frames.data', method: 'get_configurations_by_sfmid', args : [[], $(ev.currentTarget).attr('data-sfmid')]})
                    .then(function (configurations) {
                        var currentTarget = $(ev.currentTarget);
                        currentTarget.parent().parent().parent().after($($(QWeb.render("frames_data.add_configurations_by_sfmid", {configurations:configurations[0],vendors:self.vendors}))));
                        if (configurations[0].length){
                            var min = configurations[0].reduce(function(prev, curr) {
                                return prev['SalePrice'] < curr['SalePrice'] ? prev : curr;
                            });
                            $(ev.currentTarget).parent().parent().parent().find('.wholesale').val(min['SalePrice']);
                            $(ev.currentTarget).parent().parent().parent().find('.retail').val(min['Retail']);
                            self.wholesale_changed($(ev.currentTarget).parent().parent().parent().find('.wholesale'));
                        }
                    });
            }
            else {
                var currentTarget = $(ev.currentTarget);
                $(ev.currentTarget).parent().parent().parent().find('.wholesale').val('');
                $(ev.currentTarget).parent().parent().parent().find('.retail').val('');
                arrow[0].style.display = 'none';
                var style_configurations = $('.style_configurations');
                if (style_configurations.length)
                    for (var i=0; i<style_configurations.length; i++)
                        if (style_configurations.attr('data-sfmid') == $(ev.currentTarget).attr('data-sfmid'))
                            $(style_configurations[i]).parent().parent().parent().remove();
            }
        },
        select_all_clicked: function(ev){
            var self = this;
            if (this.select_all){
                this.select_all = false;
                var checkbox = $('.checkbox:not(:checked)');
                for (var i=0; i<checkbox.length;i++){
                    $(checkbox[i]).prop('checked',true)
                    self.manufacturer_collections_changed($(checkbox[i]))
                }
            }
            else{
                this.select_all = true;
                var checkbox = $('.checkbox:checked');
                for (var i=0; i<checkbox.length;i++){
                    $(checkbox[i]).prop('checked',false)
                    self.manufacturer_collections_changed($(checkbox[i]))
                }
            }
        },
        import_clicked: function(ev, is_new = 0){
            var self = this;
            var checkbox = $('.checkbox:checked');
            var cfmids = [];
            for (var i=0; i<checkbox.length;i++)
              cfmids.push(parseInt($(checkbox[i]).attr('data-cfmid')))
            self._rpc({model: 'frames.data', method: 'import_frames_by_cfmid', args : [[], cfmids, $('#vendor option:selected').attr('data-id')]})
                .then(function (response) {
                    if (response[0]){
                        var checkbox = $('.checkbox:checked');
                        for (var i=0; i<checkbox.length;i++)
                            $(checkbox[i]).prop('checked',false)
                        alert("Data imported.")

                        if (response[1].length)
                            alert("Frame listing already exists \n" + response[1]);
//                                    alert("These frame/s is/are already associated with a listing. Please synchronize for up to date variations \n" + response[1]);
                        else
                            self.trigger_up('breadcrumb_clicked', {controllerID: self.__parentedParent.controllerStack[0]});
                    }
                    else
                        alert('Server error, try again in a few seconds')
                });
//            var upc_list = '';
//            var data = []
//            var styles = $('.main_style:checked');
//            for (var i=0; i< styles.length; i++){
//                var sfmid = $(styles[i]).parent().parent().parent().find('.checkbox').attr('data-sfmid');
//                var style_configurations = $('.style_configurations.' + sfmid + ':not(.upc)');
//                for (var j=0;j<style_configurations.length;j++)
//                    data.push($(style_configurations[j]).parent().parent().parent().find('.upc')[0].innerText)
//            }
//            var upc_style_configurations = $('.style_configurations.upc');
//            for (var i=0;i<upc_style_configurations.length;i++)
//                data.push($(upc_style_configurations[i]).parent().parent().parent().find('.UPC')[0].innerText)
////                data.push($($(upc_style_configurations[i]).parent().parent().parent()[0].children[4])[0].innerText)
//
//            this._rpc({model: 'frames.data', method: 'check_upc_exist', args : [[], data]})
//                .then(function (response) {
//                    if (response[0])
//                        upc_list = response[2];
//                    var data = []
//                    var upc_data = []
//                    var styles = $('.main_style:checked');
//                    for (var i=0; i< styles.length; i++){
//                        data.push(JSON.parse($(styles[i]).parent().parent().parent().find('.json').val()))
//                        if ($('#vendor option:selected').length)
//                            data[data.length-1].Vendor = $('#vendor option:selected').attr('data-id');
////                        data[data.length-1].Vendor = $($($(styles[i]).parent().parent().parent())[0].children[7].children[0]).find(":selected").attr('data-id');
//                        data[data.length-1].Wholesale = $(styles[i]).parent().parent().parent().find('.wholesale').val();
//                        data[data.length-1].Retail = $(styles[i]).parent().parent().parent().find('.retail').val();
//
//                        var sfmid = $(styles[i]).parent().parent().parent().find('.checkbox').attr('data-sfmid');
//                        var style_configurations = $('.style_configurations.' + sfmid + ':not(.upc)');
//                        data[data.length-1].configurations = []
//                        for (var j=0;j<style_configurations.length;j++){
//                            data[data.length-1].configurations.push(JSON.parse($(style_configurations[j]).parent().parent().parent().find('.json').val()));
//                            data[data.length-1].configurations[j].SKU = $(style_configurations[j]).parent().parent().parent().find('.sku').val();
//                            data[data.length-1].configurations[j].Wholesale = $(style_configurations[j]).parent().parent().parent().find('.wholesale').val();
//                            data[data.length-1].configurations[j].Retail = $(style_configurations[j]).parent().parent().parent().find('.retail').val();
//                            data[data.length-1].configurations[j].Min_Qty = $(style_configurations[j]).parent().parent().parent().find('.min_qty').val();
//                            data[data.length-1].configurations[j].Max_Qty = $(style_configurations[j]).parent().parent().parent().find('.max_qty').val();
//                        }
//                    }
//                    var upc_style_configurations = $('.style_configurations.upc');
//                    for (var i=0; i< upc_style_configurations.length; i++){
//                        upc_data.push(JSON.parse($(upc_style_configurations[i]).parent().parent().parent().find('.json').val()));
//                        if ($('#vendor option:selected').length)
//                            upc_data[upc_data.length-1].Vendor = $('#vendor option:selected').attr('data-id');
////                        upc_data[upc_data.length-1].Vendor = $($($($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling)[0].previousElementSibling)[0].children[7].children[0]).find(":selected").attr('data-id');
//                        upc_data[upc_data.length-1].Wholesale = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.wholesale').val();
//                        upc_data[upc_data.length-1].Retail = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.retail').val();
//                        upc_data[upc_data.length-1].SKU = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.sku').val();
//                        upc_data[upc_data.length-1].Min_Qty = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.min_qty').val();
//                        upc_data[upc_data.length-1].Max_Qty = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.max_qty').val();
//                    }
//                    self._rpc({model: 'frames.data', method: 'import_frames', args : [[], data, upc_data, response[1]]})
//                        .then(function (response) {
//                            if (response[0]){
//                                alert("Data imported.")
//                                if (response[1].length)
//                                    alert("Frame listing already exists \n" + response[1]);
////                                    alert("These frame/s is/are already associated with a listing. Please synchronize for up to date variations \n" + response[1]);
//                                if (is_new){
//                                    $('#style_configurations .details').html('');
//                                    $('#upc_style_configurations .details').html('')
//                                    $('#manufacturer_collection option:selected').prop('selected',false);
//                                    $('#style').val('');
//                                    $('#upc').val('');
//                                }
//                                else
//                                    self.trigger_up('breadcrumb_clicked', {controllerID: self.__parentedParent.controllerStack[0]});
//                            }
//                            else
//                                alert('Server error, try again in a few seconds')
//                        });
//                });
        },
        synchronize_clicked: function(ev){
            var self = this;
//            var data = []
//            var upc_data = []
//            var styles = $('.main_style:checked');
//            for (var i=0; i< styles.length; i++){
//                data.push(JSON.parse($(styles[i]).parent().parent().parent().find('.json').val()))
//                if ($('#vendor option:selected').length)
//                    data[data.length-1].Vendor = $('#vendor option:selected').attr('data-id');
////                        data[data.length-1].Vendor = $($($(styles[i]).parent().parent().parent())[0].children[7].children[0]).find(":selected").attr('data-id');
//                data[data.length-1].Wholesale = $(styles[i]).parent().parent().parent().find('.wholesale').val();
//                data[data.length-1].Retail = $(styles[i]).parent().parent().parent().find('.retail').val();
//
//                var sfmid = $(styles[i]).parent().parent().parent().find('.checkbox').attr('data-sfmid');
//                var style_configurations = $('.style_configurations.' + sfmid + ':not(.upc)');
//                data[data.length-1].configurations = []
//                for (var j=0;j<style_configurations.length;j++){
//                    data[data.length-1].configurations.push(JSON.parse($(style_configurations[j]).parent().parent().parent().find('.json').val()));
//                    data[data.length-1].configurations[j].SKU = $(style_configurations[j]).parent().parent().parent().find('.sku').val();
//                    data[data.length-1].configurations[j].Wholesale = $(style_configurations[j]).parent().parent().parent().find('.wholesale').val();
//                    data[data.length-1].configurations[j].Retail = $(style_configurations[j]).parent().parent().parent().find('.retail').val();
//                    data[data.length-1].configurations[j].Min_Qty = $(style_configurations[j]).parent().parent().parent().find('.min_qty').val();
//                    data[data.length-1].configurations[j].Max_Qty = $(style_configurations[j]).parent().parent().parent().find('.max_qty').val();
//                }
//            }
//            var upc_style_configurations = $('.style_configurations.upc');
//            for (var i=0; i< upc_style_configurations.length; i++){
//                upc_data.push(JSON.parse($(upc_style_configurations[i]).parent().parent().parent().find('.json').val()));
//                if ($('#vendor option:selected').length)
//                    upc_data[upc_data.length-1].Vendor = $('#vendor option:selected').attr('data-id');
////                        upc_data[upc_data.length-1].Vendor = $($($($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling)[0].previousElementSibling)[0].children[7].children[0]).find(":selected").attr('data-id');
//                upc_data[upc_data.length-1].Wholesale = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.wholesale').val();
//                upc_data[upc_data.length-1].Retail = $($($(upc_style_configurations[i]).parent().parent().parent())[0].previousElementSibling.previousElementSibling).find('.retail').val();
//                upc_data[upc_data.length-1].SKU = $($($(upc_style_configurations[i]).parent().parent().parent())[0]).find('.sku').val();
//                upc_data[upc_data.length-1].Min_Qty = $($($(upc_style_configurations[i]).parent().parent().parent())[0]).find('.min_qty').val();
//                upc_data[upc_data.length-1].Max_Qty = $($($(upc_style_configurations[i]).parent().parent().parent())[0]).find('.max_qty').val();
//
//                upc_data.push(JSON.parse($($(upc_style_configurations[i]).parent().parent().parent()[0].children[0].children[0]).val()))
//            }
            var checkbox = $('.checkbox:checked');
            var cfmids = [];
            for (var i=0; i<checkbox.length;i++)
              cfmids.push(parseInt($(checkbox[i]).attr('data-cfmid')))

            self._rpc({model: 'frames.data', method: 'sync_frames_by_cfmid', args : [[], cfmids, $('#vendor option:selected').attr('data-id')]})
                .then(function (response) {
                    if (response){
                        alert("Data Synchronized.");
                        self.trigger_up('breadcrumb_clicked', {controllerID: self.__parentedParent.controllerStack[0]});
                    }
                    else
                        alert('Server error, try again in a few seconds')
                });
        },
        synchronize_existing_clicked: function(ev){
            var self = this;
            var checkbox = $('.checkbox:checked');
            var cfmids = [];
            for (var i=0; i<checkbox.length;i++)
              cfmids.push(parseInt($(checkbox[i]).attr('data-cfmid')))

            self._rpc({model: 'frames.data', method: 'sync_existing_frames_by_cfmid', args : [[]]})
                .then(function (response) {
                    if (response){
                        alert("Data Synchronized.");
                        self.trigger_up('breadcrumb_clicked', {controllerID: self.__parentedParent.controllerStack[0]});
                    }
                    else
                        alert('Server error, try again in a few seconds')
                });
        },
    });

    core.action_registry.add("frames_data_import", frames_data_import);
    return frames_data_import;
});