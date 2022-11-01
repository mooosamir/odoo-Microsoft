odoo.define('ks_theme_kernel.ks_unsplash_widget', function (require) {
"use strict";

var core = require('web.core');
var basic_fields = require('web.basic_fields');
var registry = require('web.field_registry');
var Widget = require('web.Widget');
var weWidgets = require('wysiwyg.widgets');

var QWeb = core.qweb;

var KsUnsplashWidget = basic_fields.FieldBinaryImage.extend({

    init: function (parent, state, params) {
        this._super.apply(this, arguments);
    },

    template: 'KsFieldBinaryImageKernel',

    events: _.extend({}, basic_fields.FieldBinaryImage.prototype.events, {
        'click .ks_image_widget_icon_container_kernel': 'ks_image_widget_icon_container_kernel', // View container
    }),

//     _render: function () {
//         var ks_self = this;
//         var url = this.placeholder;
//         if (ks_self.value) {
//             ks_self.$('> img').remove();
//             ks_self.$('> span').remove();
//             $('<span>').addClass('fa fa-' + ks_self.recordData.ks_default_icon + ' fa-5x').appendTo(ks_self.$el).css('color', 'black');
//         }
//         else {
//             var $img = $(QWeb.render("FieldBinaryImage-img", {
//                 widget: this,
//                 url: url
//             }));
//             ks_self.$('> img').remove();
//             ks_self.$('> span').remove();
//             ks_self.$el.prepend($img);
//         }
//     },

    //This will show modal box on clicking on open icon button.
    ks_image_widget_icon_container_kernel: function (ev) {
        var self = this;
        var $img = $('<img/>');
        var mediaDialog = new weWidgets.MediaDialog(this, {
            onlyImages: true,
            firstFilters: ['logo'],
            res_model: 'ir.ui.view',
        }, $img[0]);
        mediaDialog.open();
        mediaDialog.on('save', this, function (imgg) {
            var convertImgToDataURLviaCanvas = function(url, callback) {
                var img = new Image();

                img.crossOrigin = 'Anonymous';

                img.onload = function() {
                    var canvas = document.createElement('CANVAS');
                    var ctx = canvas.getContext('2d');
                    var dataURL;
                    canvas.height = this.height;
                    canvas.width = this.width;
                    ctx.drawImage(this, 0, 0);
                    dataURL = canvas.toDataURL();
                    callback(dataURL);
                    canvas = null;
                };
                img.src = url;
            }
            convertImgToDataURLviaCanvas(imgg.src, function( base64_data ) {
                self.$el.children()[0].src = base64_data;
                self._rpc({
                    model: 'ks.menu.icon.singleton',
                    method: 'create',
                    args: [{'ks_attachment': base64_data}]
                });
            });
        });
    },

});

registry.add('ks_unsplash_widget', KsUnsplashWidget);

return {
    KsUnsplashWidget: KsUnsplashWidget,
};
});