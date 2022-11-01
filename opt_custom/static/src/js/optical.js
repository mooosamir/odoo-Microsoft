odoo.define('opt_custom.singup', function (require) {
    "use strict";
	$("#collection_id").val(null).trigger("change"); 
   	$('#business_type_id').on('change',function(){
   			$("#collection_id").val(null).trigger("change"); 
            if($("#business_type_id option:selected").val() == 2){
            	$("#collection-container").removeClass("d-none")
            }
            else{
            	$("#collection-container").addClass("d-none")
            }
      });
    if($("#business_type_id option:selected").val() == 2){
		$("#collection-container").removeClass("d-none")
        }
    else{
    	$("#collection-container").addClass("d-none")
    }
    $('#collection_id').select2()
    $('#collection_id').on('change',function(){
    	$('#collection_input').val($('#collection_id').val())
    	$('#collection_input').text($('#collection_id').val())
    });
});




