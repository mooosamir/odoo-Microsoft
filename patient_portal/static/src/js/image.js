function readURL(input) {
  if (input.files && input.files[0]) {

    var reader = new FileReader();

    reader.onload = function(e) {
      $(input).parent().find('.image-upload-wrap').hide();
//      $('.file-upload-image').$(input).attr('src', i.target.result);
      $(input).parent().find('.file-upload-image').attr('src', e.target.result)
      $(input).parent().find('.file-upload-content').show();

      $(input).parent().find('.image-title').html(input.files[0].name);
      $(input).parent().find('.drag-text').hide();
    };

    reader.readAsDataURL(input.files[0]);

  } else {
    removeUpload();
  }
}

//function removeUpload() {
//  $('.file-upload-input').replaceWith($('.file-upload-input').clone());
//  $('.file-upload-content').hide();
//  $('.image-upload-wrap').show();
//}
//$('.image-upload-wrap').bind('dragover', function () {
//    $('.image-upload-wrap').addClass('image-dropping');
//  });
//  $('.image-upload-wrap').bind('dragleave', function () {
//    $('.image-upload-wrap').removeClass('image-dropping');
//});
