$(document).ready(function ()
	{
	
	$('form.filter_specs input').on('change', function (event) {
        if (!event.isDefaultPrevented()) {
            event.preventDefault();
            $(this).closest("form").submit();
        }
    });

});

odoo.define('website_shop.website_shop', function (require) {
var core = require('web.core');
require('website_sale.website_sale');
var publicWidget = require('web.public.widget');

publicWidget.registry.WebsiteSale.include({
    _updateProductImage: function ($productContainer, displayImage, productId, productTemplateId, newCarousel, isCombinationPossible) {
        var $carousel = $productContainer.find('#o-carousel-product');
        console.log("call")
        // When using the web editor, don't reload this or the images won't
        // be able to be edited depending on if this is done loading before
        // or after the editor is ready.
        // if (window.location.search.indexOf('enable_editor') === -1) {
        //     var $newCarousel = $(newCarousel);
        //     $carousel.after($newCarousel);
        //     $carousel.remove();
        //     $carousel = $newCarousel;
        //     $carousel.carousel(0);
        //     //this._startZoom();
        //     // fix issue with carousel height
        //     //this.trigger_up('widgets_start_request', {$target: $carousel});
        // }
        //$carousel.toggleClass('css_not_available', !isCombinationPossible);
    },
	
});

// website_sale.include({


// });
});