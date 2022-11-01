jQuery(document).ready(function() {
if (jQuery('.zoom-product')) {
    jQuery('.zoom-product').elevateZoom(
     {
         zoomType: "lens",
         lensShape: "square",
         lensSize: 200
     }
     );

}

var zoomConfig = {cursor: 'crosshair', zoomType: "inner" }; 
var image = $('#gallery_id');
var zoomImage = $('.zoom-product');
console.log("Image-",zoomImage);

zoomImage.elevateZoom(zoomConfig);//initialise zoom
image.hover(function(){
    // Remove old instance od EZ
    $('.zoomContainer').remove();
    zoomImage.removeData('elevateZoom');
    // Update source for images
    zoomImage.attr('src', $(this).data('image'));
    zoomImage.data('zoom-image', $(this).data('zoom-image'));
    // Reinitialize EZ
    zoomImage.elevateZoom(zoomConfig);
});

});

