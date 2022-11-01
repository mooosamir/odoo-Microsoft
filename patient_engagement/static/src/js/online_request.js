window.addEventListener('DOMContentLoaded', function () {
    checkForChanges();
});

function checkForChanges () {
    if(document.getElementsByClassName("online.requests.kanban").length !=0 ){
        setTimeout(checkForChangesAgain, 500);
        setTimeout(checkForChangesAgain, 500);
    }
//    else if(document.getElementsByClassName("count_text").length !=0 ){
//        setTimeout(checkForChangesSMSText, 500);
//        setTimeout(checkForChangesSMSText, 500);
//    }
    else
        setTimeout(checkForChanges, 500);
};

function checkForChangesAgain () {
    for (var i=0;i< document.getElementsByClassName("online.requests.kanban").length; i++){
        document.getElementsByClassName("online.requests.kanban")[i].parentElement.style.width = '40%';
    }
    setTimeout(checkForChanges, 500);
}

function checkForChangesSMSText () {
    document.getElementsByClassName("count_text")[0].maxLength=130;
    $('.count_text').keyup(function() {

      var characterCount = $(this).val().length,
          current = $('#current'),
          maximum = $('#maximum'),
          theCount = $('#the-count');

      current.text(characterCount);


      /*This isn't entirely necessary, just playin around*/
      if (characterCount < 50) {
        current.css('color', '#666');
      }
      if (characterCount > 50 && characterCount < 70) {
        current.css('color', '#6d5555');
      }
      if (characterCount > 70 && characterCount < 80) {
        current.css('color', '#793535');
      }
      if (characterCount > 90 && characterCount < 100) {
        current.css('color', '#841c1c');
      }
      if (characterCount > 100 && characterCount < 120) {
        current.css('color', '#8f0001');
      }

      if (characterCount >= 120) {
        maximum.css('color', '#8f0001');
        current.css('color', '#8f0001');
        theCount.css('font-weight','bold');
      } else {
        maximum.css('color','#666');
        theCount.css('font-weight','normal');
      }

    });
    setTimeout(checkForChanges, 50000);

}