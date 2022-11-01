function HomeButton(){
    window.location.replace("/patient_portal");
}

function PrescriptionButton(){
    window.location.replace("/patient_portal/prescription");
}

function AppointmentButton(){
    window.location.replace("/patient_portal/appointments");
}

function MessageButton(series_id){
    window.location.replace("/patient_portal/message?");
}

function AppointmentConfirm(series_id){
    $.ajax({
       url : '/patient_portal/appointment/confirm_appointment?id=' + series_id,
       type : 'POST',
       success : function(kj) {
           alert(kj)
       },
       fail : function() {
        },
    });
}

function AppointmentReschedule(series_id){
    window.location.replace("/online_appointment/location?branch=" + series_id[1] + "&id="+ series_id[0] + "&doctor="+ series_id[2]);
};

function RequestAppointment(){
            window.location.replace("/online_appointment");
}

function newMessage(id = 0){
         $.ajax({
                   url : '/patient_portal/message/new_message?id='+id,
                   type : 'POST',
                   success : function(kj) {
                            if (kj == '0'){
                                alert('User is not Employee')
                            }
                            else{
                                $(".right-side").html(kj);
                                $("#messageSent").removeClass('active-now');
                                $("#messageRcvd").removeClass('active-now');
                                $("#messageTrash").removeClass('active-now');
                            }




                                            },
                   fail : function() {

                },
                });
}

function MessageInbox(){
     $.ajax({
       url : '/patient_portal/message/inbox',
       type : 'POST',
       success : function(kj) {
            $(".right-side").html(kj);
            $("#messageRcvd").addClass('active-now');
            $("#messageSent").removeClass('active-now');
            $("#messageTrash").removeClass('active-now');
            if (window.document.body.clientWidth <= 767.98)
                $(".main-content").css('display','none');
       },
        error: function () {

       },
     });
}

function MessageSent(){
     $.ajax({
       url : '/patient_portal/message/sent',
       type : 'POST',
       success : function(kj) {
                $(".right-side").html(kj);
                $("#messageSent").addClass('active-now');
                $("#messageRcvd").removeClass('active-now');
                $("#messageTrash").removeClass('active-now');
            if (window.document.body.clientWidth <= 767.98)
                $(".main-content").css('display','none');
        },
       error: function () {

        },
    });
}
var next_form = 0;
function intakeBegin(){
    var a = JSON.parse($('input[name="forms"]').attr('value'));
    if (next_form < Object.keys(a).length){
        $('.next').attr('form',Object.keys(a)[next_form])
        next_form++
        $('.begin')[0].style.display = "None";
        $('.next')[0].style.display = "";
        for (var i=0;i<$("."+ $('.next').attr('form')).length;i++)
            $("."+ $('.next').attr('form'))[i].style.display = '';
    }
    else
        $('.Next').attr('form',"Submit")
}
//$(window).bind("pageshow", function() {
//    var form = $('form');
//    // let the browser natively reset defaults
//});

function IntakeConsentShow(){
        var a = JSON.parse($('input[name="forms"]').attr('value'));
        if (next_form < Object.keys(a).length){
            $('.next').attr('form',Object.keys(a)[next_form])
            next_form++
            $('.begin')[0].style.display = "None";
            $('.next')[0].style.display = "";
            for (var i=0;i<$("."+ $('.next').attr('form')).length;i++)
                $("."+ $('.next').attr('form'))[i].style.display = '';
        }
        else
            $('.Next').attr('form',"Submit")

        for (var j=0;j<Object.keys(a).length;j++){
            for (var i=0;i<$("."+ $('.next').attr('form')).length;i++)
                $("."+ $('.next').attr('form'))[i].style.display = 'None';
            if (next_form < Object.keys(a).length){
                $('.next').attr('form',Object.keys(a)[next_form])
                next_form++
                for (var i=0;i<$("."+ $('.next').attr('form')).length;i++)
                    $("."+ $('.next').attr('form'))[i].style.display = '';
            }
            else{
                $('.Next').attr('form',"Submit")
                $('.next')[0].style.display = "None";
                $('.submit')[0].style.display = "";
            }
            if ($('.next').attr('form') == 'acs_consent_form_template')
                break;
        }
}

function IntakeNext(){
    var verified = false;
    for (var k=0;k<$("."+ $('.next').attr('form')).length;k++){
        if (!$("."+ $('.next').attr('form')).hasClass('acs_consent_form_template') && $("."+ $('.next').attr('form'))[k].checkValidity()){
            verified = true;
        }
        else{
            if (!$("."+ $('.next').attr('form')).hasClass('acs_consent_form_template')){
                verified = false;
//                alert('some values are missing');
                $("."+ $('.next').attr('form'))[k].reportValidity();
                break;
            }
            else
                verified = true;
        }
    }

    if (verified){
        var a = JSON.parse($('input[name="forms"]').attr('value'));
        for (var i=0;i<$("."+ $('.next').attr('form')).length;i++)
            $("."+ $('.next').attr('form'))[i].style.display = 'None';
        if (next_form < Object.keys(a).length){
            $('.next').attr('form',Object.keys(a)[next_form])
            if ($('.next').attr('form') == 'acs_consent_form_template'){
                if (window.location.href.includes('?'))
                    window.history.pushState('intake_form', 'intake_form', window.location.href + '&consent_form_1');
                else
                    window.history.pushState('intake_form', 'intake_form', window.location.href + '?consent_form_1');
//                $('input[name="is_consent"]').attr('value',1);
            }
            next_form++;
            for (var i=0;i<$("."+ $('.next').attr('form')).length;i++)
                $("."+ $('.next').attr('form'))[i].style.display = '';
        }
        else{
            $('.Next').attr('form',"Submit")
            $('.next')[0].style.display = "None";
            $('.submit')[0].style.display = "";
        }
    }


//    $.ajax({
//       url : '/patient_portal/forms/body?forms=' + forms + "&id=" + id,
//       type : 'POST',
//       success : function(response) {
//            $(".intake_form").html(response);
//       },
//       error: function (jqXHR, status, err) {
//            alert(err);
//       },
//    });

}

function intake_form_submit(){
    var formData = new FormData();
    for (var i=0;i<$('form').length;i++){
        files = $($('form')[i]).find('input[type="file"]');
//         var data = new FormData();
        $($('form')[i]).serializeArray().map(function(x){formData.append($($('form')[i]).attr('name') + "___" +x.name,x.value)})
        for (var j=0; j<files.length;j++)
            formData.append($($('form')[i]).attr('name') + "___" + $(files[j]).attr('name'),$(files[j])[0].files[0]);
//         console.log(data);
//         formData.append($($('form')[i]).attr('name'),data);
//         formData.append($($('form')[i]).attr('name'),JSON.stringify(data));
//        ac[$($('form')[i]).attr('name')] = $($('form')[i]).serialize();
    }
    $.ajax({
        url: '/patient_portal/forms/body/return?appointment_id=' + $('input[name="appointment_id"]').attr('value'),
        type: "POST",
        enctype: 'multipart/form-data',
        processData: false,
        contentType: false,
        data: formData,
        success: function (result) {
            if (result == "0")
                alert('error, some fields are not filled properly')
            else
                window.location = result;
//            $("input[name='messaging_history_id']").val(result);
        }
    });
}

function openMessage(abc, channel_id=0, partner_id=0){
    $.ajax({
        url: '/patient_portal/message/inbox/seen?partner_id=' + partner_id + '&channel_id=' + channel_id + '&message_id=' + $(abc).attr('id'),
        type: "POST",
        success: function (result) {
            if (result == "0")
                alert(result)
        }
    });
    $(".email").html($(abc).attr('message'));
    $(".email-from").html($(abc).attr('author'));
    $(".subject").html($(abc).attr('subject'));
    $(".date").html($(abc).attr('date'));
    $(".fa-trash-o").attr('data-id',$(abc).attr('id'));
    $(".fa-reply").attr('data-id',$(abc).attr('id'));
    $(".inbox-content").css('display','block');
    $(".main-content").css('display','none');
    if (window.document.body.clientWidth <= 767.98){
        $(".inbox-message-list").css('display','none');
        $(".fa-chevron-left").css('display','block');
    }
}

function backMessage(abc){
    $(".inbox-message-list").css('display','');
    $(".inbox-content").css('display','none');
    $(".fa-chevron-left").css('display','');
}

function goesToTrash(gett){


    $.ajax({
       url : '/patient_portal/message/get-id?id=' + gett.getAttribute('data-id'),
       type : 'POST',
       success : function(response) {
            $("#"+ gett.getAttribute('data-id')).remove();
            $(".main-content").css('display','block');
            $(".inbox-content").css('display','none');
       },
       error: function (jqXHR, status, err) {

       },})

}

function MessageTrash(){
        $.ajax({
       url : '/patient_portal/message/trash',
       type : 'POST',
       success : function(kj) {
             $(".right-side").html(kj);
             $("#messageSent").removeClass('active-now');
             $("#messageRcvd").removeClass('active-now');
             $("#messageTrash").addClass('active-now');
            if (window.document.body.clientWidth <= 767.98)
                $(".main-content").css('display','none');
       },
       error: function (jqXHR, status, err) {
            alert(err);
       },
    });

}

function sentMessageBtn(){
    to = $(".sent-to option:selected").val();
//    id =  $(".sent-to").attr('data');
    id =  $(".sent-to option:selected").attr('data');
    var partner_id;
    if ($(".sent-to option:selected").attr('to-partner-id') == undefined)
        to_partner_id = 0;
    else
        to_partner_id = $(".sent-to option:selected").attr('to-partner-id');
    subject = $('.sent-subject').val();
    message = $('.sent-message').val();

    $.ajax({
       url : '/patient_portal/message/email_sent?id=' + id +"&to="+ to +"&subject="+ subject + "&message="+ message + "&to_partner_id=" + to_partner_id,
       type : 'POST',
       success : function() {
            window.location.replace("/patient_portal/message");
       },
       error: function () {

       },
    });

}

function replyBtn(abc){
    objectId = $("#"+ abc.getAttribute('data-id'));
    return newMessage(objectId[0].getAttribute('partner-id'))


}
