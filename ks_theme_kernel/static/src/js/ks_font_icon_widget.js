odoo.define('ks_theme_kernel.ks_font_icon_widget', function (require) {
"use strict";

var core = require('web.core');
var basic_fields = require('web.basic_fields');
var registry = require('web.field_registry');
var Widget = require('web.Widget');
var weWidgets = require('wysiwyg.widgets');

var QWeb = core.qweb;

var KsFontIconWidget = basic_fields.FieldBinaryImage.extend({

    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        this.ksSelectedIcon = false; // Not in use
    },

    template: 'KsFieldBinaryImageKernel',

    events: _.extend({}, basic_fields.FieldBinaryImage.prototype.events, {
        'click .ks_image_widget_icon_container_kernel': 'ks_image_widget_icon_container_kernel', // View container
    }),

    _render: function () {
        var ks_self = this;
        ks_self.$('> img').remove();
        ks_self.$('> span').remove();
        var img = $('<span/>').addClass('fa fa-camera'+' fa-5x');
        img.appendTo(ks_self.$el).css('color', 'black');
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function(){

        });
    },


    //This will show modal box on clicking on open icon button.
    ks_image_widget_icon_container_kernel: function (ev) {
        var self = this;
        var $span = $('<span/>');
        var mediaDialog = new weWidgets.MediaDialog(this, {
            noIcons: false,
            noVideos: true,
            noDocuments: true,
            noImages: true,
            res_model: 'ir.ui.view',
        }, $span[0]);
        mediaDialog.open();
        mediaDialog.on('save', this, function (span) {
            self.activeMetaImg = span.src;
            self.customImgUrl = span.src;
            self.$('> span').remove();
            var img = $('<span/>').addClass('fa '+ span.classList[1] + ' fa-5x');
            img.appendTo(self.$el).css('color', 'black');
            $(".font-color-picker").spectrum("set", '#000000');
            self._rpc({
                model: 'ks.menu.icon.singleton',
                method: 'create',
                args: [{'ks_font_awesome': 'fa ' + span.classList[1] + ',#000000,#000000' }]
            });
//            $(".font-bg-color-picker").spectrum("set", '#000000');
        });
        $('.color_picker_wrapper').removeClass('d-none');
        $('.font-color-picker').spectrum({
            color: '#000000',
            preferredFormat: "hex",
            showInput: true,
            showInitial: true,
            showAlpha: false,
            allowEmpty:false,
            cancelText: "Cancel",
            chooseText: "Choose",
            change: function(color) {
                $('.fa-5x').css({'color':color.toHexString()});
                self._rpc({
                    model: 'ks.menu.icon.singleton',
                    method: 'create',
                    args: [{'ks_font_awesome': 'fa ' + $('.ks_font_icon_div span.fa')[0].className.split(' ')[1] + ',' + color.toHexString() + ',#000000'}]
                });
            }
        });
//        $('.font-bg-color-picker').spectrum({
//            color: '#000000',
//            preferredFormat: "hex",
//            showInput: true,
//            showInitial: true,
//            allowEmpty:true,
//            cancelText: "Cancel",
//            chooseText: "Choose",
//            change: function(color) {
//               color = color ? color.toHexString() : '#ff000000';
//               $('.fa-5x').css({'background-color':color});
//            }
//        });
    },
});

registry.add('ks_image_widget', KsFontIconWidget);

return {
    KsFontIconWidget: KsFontIconWidget,
};
});