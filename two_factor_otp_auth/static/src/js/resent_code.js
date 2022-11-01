odoo.define('two_factor_otp_auth.resend_otp_code', function (require) {
'use strict';

var core = require('web.core');
var ajax = require('web.ajax');
var _t = core._t;
require('web.dom_ready');
var flag = false;
//var options = require('web_editor.snippets.options');

// if ($('.oe_code_form').length) {	
// 	//console.log("=++++++++#########@===========")
//     //return $.Deferred().reject("DOM doesn't contain '.oe_code_form'");
// 	function timer(remaining) {
// 	  if (!flag){
// 	  var login = $('.login').val();
// 	  var times = document.getElementById('timer_div');
// 	      $(document.getElementsByClassName('alert-dangers')).hide();
// 		  if (times.style.display === "none") {
// 		    times.style.display = "block";
// 		  } else {
// 		    times.style.display = "none";
// 		  }
// 		$(document.getElementById('timer_div')).show();
// 		let timerOn = true;
// 	  var m = Math.floor(remaining / 60);
// 	  var s = remaining % 60;
	  
// 	  m = m < 10 ? '0' + m : m;
// 	  s = s < 10 ? '0' + s : s;
// 	  document.getElementById('timer').innerHTML = m + ':' + s;
// 	  remaining -= 1;
	  
// 	  if(remaining >= 0 && timerOn) {
// 	    setTimeout(function() {
// 	        timer(remaining);
// 	    }, 1000);
// 	    return;
// 	  }

// 	  if(!timerOn) {
// 	    // Do validate stuff here
// 	    return;
// 	  }
// 	  ajax.jsonRpc("/delete/otp_code", 'call', {
// 			'login': login
// 		}).then(function (data) {

// 		});
// 	if (times.style.display === "block") {
// 		    times.style.display = "none";
// 		  } else {
// 		    times.style.display = "block";
// 		  }
// 	  // Do timeout stuff here
	  
// 	}
// 	}

// 	 timer(120);
// }
            	 

$('#resent_otp_code_button').click(function(){
	var login = $('.login').val();
     ajax.jsonRpc("/generate/otp_code", 'call', {
                'login': login
            }).then(function (data) { 
            	//timer(120);   
				function timer(remaining) {
				  flag = true;
				  var times = document.getElementById('timer_div');
				      $(document.getElementsByClassName('alert-dangers')).hide();
					  if (times.style.display === "none") {
					    times.style.display = "block";
					  } else {
					    times.style.display = "none";
					  }
					$(document.getElementById('timer_div')).show();
					let timerOn = true;
				  var m = Math.floor(remaining / 60);
				  var s = remaining % 60;
				  
				  m = m < 10 ? '0' + m : m;
				  s = s < 10 ? '0' + s : s;
				  document.getElementById('timer').innerHTML = m + ':' + s;
				  remaining -= 1;
				  
				  if(remaining >= 0 && timerOn) {
				    setTimeout(function() {
				        timer(remaining);
				    }, 1000);
				    return;
				  }

				  if(!timerOn) {
				    // Do validate stuff here
				    return;
				  }
				  ajax.jsonRpc("/delete/otp_code", 'call', {
                		'login': login
            		}).then(function (data) {

            		});
            	if (times.style.display === "block") {
					    times.style.display = "none";
					  } else {
					    times.style.display = "block";
					  }
				  // Do timeout stuff here
				  
				}
            });


});


});