// ################################################
    //                 widget                              |         Format
    // number_only_with_single_precision             |   0.00
    // number_only_with_three_digit                  |   000
    // number_only_with_double_precision             |   00.00
    // number_only_with_two_digit_single_precision   |   00.0
    // number_only_with_single_precision_sign        |   +/- 0.00
    // number_only_with_double_precision_minus_sign  |   -00.00
    // number_only_with_single_precision_plus_sign   |   +0.00
    // number_only_with_double_precision_sign        |   +/- 00.00
    // number_only_with_two_digit_rounding           |   change 00.0 to 00
    // number_only_with_three_digit_rounding         |   change 000.0 to 000

// ################################################
odoo.define('opt_custom.field_options', function (require) {
    "use strict";

    var basic_fields = require('web.basic_fields');
    var BasicController = require('web.BasicController');
    var core = require('web.core');

    var _t = core._t;

    function zero_pad(num,size,non_zero_pad=false){
        var s = ""+num;
        if (non_zero_pad){
            return s;
        }
        while (s.length < size) {
            s = "0" + s;
        }
        return s;
    }

    basic_fields.FieldChar.include({
        events: _.extend({},  basic_fields.FieldChar.prototype.events, {
            'blur': '_onInputblur',
        }),
        init: function () {
            this._super.apply(this, arguments);
            this.number_only_with_single_precision = this.nodeOptions.number_only_with_single_precision ? this.nodeOptions.number_only_with_single_precision  : false;
            this.number_only_with_double_precision = this.nodeOptions.number_only_with_double_precision ? this.nodeOptions.number_only_with_double_precision  : false;
            this.number_only_with_two_digit_double_precision = this.nodeOptions.number_only_with_two_digit_double_precision ? this.nodeOptions.number_only_with_two_digit_double_precision  : false;
            this.number_only_with_single_precision_sign = this.nodeOptions.number_only_with_single_precision_sign ? this.nodeOptions.number_only_with_single_precision_sign  : false;
            this.number_only_with_double_precision_sign = this.nodeOptions.number_only_with_double_precision_sign ? this.nodeOptions.number_only_with_double_precision_sign  : false;
            this.number_only_with_three_digit = this.nodeOptions.number_only_with_three_digit ? this.nodeOptions.number_only_with_three_digit  : false;
            this.number_only_with_single_precision_plus_sign = this.nodeOptions.number_only_with_single_precision_plus_sign ? this.nodeOptions.number_only_with_single_precision_plus_sign  : false;
            this.number_only_with_double_precision_minus_sign = this.nodeOptions.number_only_with_double_precision_minus_sign ? this.nodeOptions.number_only_with_double_precision_minus_sign  : false;
            this.number_only_with_two_digit_single_precision = this.nodeOptions.number_only_with_two_digit_single_precision ? this.nodeOptions.number_only_with_two_digit_single_precision  : false;
            this.number_only_with_two_digit_rounding = this.nodeOptions.number_only_with_two_digit_rounding ? this.nodeOptions.number_only_with_two_digit_rounding  : false;
            this.number_only_with_three_digit_rounding = this.nodeOptions.number_only_with_three_digit_rounding ? this.nodeOptions.number_only_with_three_digit_rounding  : false;
        },
        check_number_only_with_single_precision: function(){
            var value = this.$input.val();
            var re = /^[0-9\u06F0-\u06F9\.?]*$/;
            if(value && ! re.test(value)){
                var title = "Warning !";
                var base_warnings =  'Please Enter in "0.00" format'
                this.do_warn(_t(title), base_warnings);
                return false;
            }
            if(value && value.indexOf(".") != -1){
               var temp =  value.split(".");
               if(temp && temp[0] && temp[0].length > 1 || temp.length != 2){
                     var title = "Warning !";
                     var base_warnings =  'Please Enter in "0.00" format'
                     this.do_warn(_t(title), base_warnings);
                    return false;
                   }
                }else if(value){
                    var temp =  value.length;
                    if(temp > 1){
                         var title = "Warning !";
                         var base_warnings =  'Please Enter in "0.00" format'
                         this.do_warn(_t(title), base_warnings);
                         return false;
                    }
            }
            return true;
        },
        check_number_only_with_three_digit: function(){
            var value = this.$input.val();
            var re = /^[0-9\u06F0-\u06F9?]*$/;
            if(value && ! re.test(value)){
                var title = "Warning !";
                var base_warnings =  'Please Enter in "000" format';
                this.do_warn(_t(title), base_warnings);
                return false;
            }
            if(value){
                var temp =  value.length;
                if(temp > 3){
                    var title = "Warning !";
                    var base_warnings =  'Please Enter in "000" format';
                    this.do_warn(_t(title), base_warnings);
                    return false;
                }
            }
            return true;
        },
        check_number_only_with_double_precision: function(){
              var value = this.$input.val();
              var re = /^[0-9\u06F0-\u06F9\.?]*$/;
              if(value && ! re.test(value)){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "00.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
              if(value && value.indexOf(".") != -1){
                 var temp =  value.split(".");
                 if(temp && temp[0] && temp[0].length > 2 || temp.length != 2){
                       var title = "Warning !";
                       var base_warnings =  'Please Enter in "00.00" format'
                       this.do_warn(_t(title), base_warnings);
                      return false;
                 }
              }else if(value){
                  var temp =  value.length;
                  if(temp > 2){
                       var title = "Warning !";
                       var base_warnings =  'Please Enter in "00.00" format'
                       this.do_warn(_t(title), base_warnings);
                       return false;
                  }
              }
            return true;
        },
        check_number_only_with_two_digit_single_precision: function(){
              var value = this.$input.val();
              var re = /^[0-9\u06F0-\u06F9\.?]*$/;
              if(value && ! re.test(value)){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "00.0" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
              if(value && value.indexOf(".") != -1){
                 var temp =  value.split(".");
                 if(temp && temp[0] && temp[0].length > 2 || temp.length != 2){
                       var title = "Warning !";
                       var base_warnings =  'Please Enter in "00.0" format'
                       this.do_warn(_t(title), base_warnings);
                      return false;
                 }
              }else if(value){
                  var temp =  value.length;
                  if(temp > 2){
                       var title = "Warning !";
                       var base_warnings =  'Please Enter in "00.0" format'
                       this.do_warn(_t(title), base_warnings);
                       return false;
                  }
              }
            return true
        },

        check_number_only_with_three_digit_rounding: function(){
            var value = this.$input.val();
            var re = /^[0-9\u06F0-\u06F9\.?]*$/;
            if(value && ! re.test(value)){
                var title = "Warning !";
                var base_warnings =  'Please Enter in "000.0" format'
                this.do_warn(_t(title), base_warnings);
                return false;
            }
            if(value && value.indexOf(".") != -1){
               var temp =  value.split(".");
               if(temp && temp[0] && temp[0].length > 3 || temp.length != 2){
                     var title = "Warning !";
                     var base_warnings =  'Please Enter in "000.0" format'
                     this.do_warn(_t(title), base_warnings);
                    return false;
               }
            }else if(value){
                var temp =  value.length;
                if(temp > 3){
                     var title = "Warning !";
                     var base_warnings =  'Please Enter in "000.0" format'
                     this.do_warn(_t(title), base_warnings);
                     return false;
                }
            }
          return true
      },

        check_number_only_with_single_precision_sign: function(){
              var value = this.$input.val();
              var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
              if(value && ! re.test(value)){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "+/- 0.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
              if(value && ! _.contains(['+', '-'], value.charAt(0))){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "+/- 0.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
                  
              if(value && value.indexOf(".") != -1){
                  var temp =  value.split(".");
                  if(temp && temp.length != 2){
                      var title = "Warning !";
                      var base_warnings =  'Please Enter in "+/- 0.00" format'
                      this.do_warn(_t(title), base_warnings);
                      return false;
                  }
                  else if(temp && temp[0] && temp[0].length != 0){
                      if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
                          if(temp[0].length > 2){
                              var title = "Warning !";
                              var base_warnings =  'Please Enter in "+/- 0.00" format'
                              this.do_warn(_t(title), base_warnings);
                              return false;
                          }
                      }else{
                          var title = "Warning !";
                          var base_warnings =  'Please Enter in "+/- 0.00" format'
                          this.do_warn(_t(title), base_warnings);
                          return false;
                      }
                       
                  }
               }else if(value){
                   if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
                      if(value.length > 2){
                          var title = "Warning !";
                          var base_warnings =  'Please Enter in "+/- 0.00" format'
                          this.do_warn(_t(title), base_warnings);
                          return false;
                      }
                  }else{
                      var title = "Warning !";
                      var base_warnings =  'Please Enter in "+/- 0.00" format'
                      this.do_warn(_t(title), base_warnings);
                      return false;
                  }
              }
            return true
        },
        check_number_only_with_double_precision_minus_sign:function(){
            var value = this.$input.val();
            var re = /^[0-9\u06F0-\u06F9\.\-?]*$/;
            if(value && ! re.test(value)){
                var title = "Warning !";
                var base_warnings =  'Please Enter in "-00.00" format'
                this.do_warn(_t(title), base_warnings);
                return false;
            }
            if(value && ! _.contains(['-'], value.charAt(0))){
                var title = "Warning !";
                var base_warnings =  'Please Enter in "-00.00" format'
                this.do_warn(_t(title), base_warnings);
                return false;
            }
                
            if(value && value.indexOf(".") != -1){
                var temp =  value.split(".");
                if(temp && temp.length != 2){
                    var title = "Warning !";
                    var base_warnings =  'Please Enter in "-00.00" format'
                    this.do_warn(_t(title), base_warnings);
                    return false;
                }
                if(temp && temp[0] && temp[0].length != 0){
                    if(temp[0].indexOf("-") == 0){
                        if(temp[0].length > 3){
                            var title = "Warning !";
                            var base_warnings =  'Please Enter in "-00.00" format'
                            this.do_warn(_t(title), base_warnings);
                            return false;
                        }
                    }else{
                        var title = "Warning !";
                        var base_warnings =  'Please Enter in "-00.00" format'
                        this.do_warn(_t(title), base_warnings);
                        return false;
                    }
                     
                }
             }else if(value){
                 if(value.indexOf("-") == 0){
                    if(value.length > 3){
                        var title = "Warning !";
                        var base_warnings =  'Please Enter in "-00.00" format'
                        this.do_warn(_t(title), base_warnings);
                        return false;
                    }
                }else{
                    var title = "Warning !";
                    var base_warnings =  'Please Enter in "-00.00" format'
                    this.do_warn(_t(title), base_warnings);
                    return false;
                }
            }
          return true;
      },
        check_number_only_with_single_precision_plus_sign: function(){
              var value = this.$input.val();
              var re = /^[0-9\u06F0-\u06F9\.\+?]*$/;
              if(value && ! re.test(value)){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "+0.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
              if(value && ! _.contains(['+'], value.charAt(0))){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "+0.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
                  
              if(value && value.indexOf(".") != -1){
                  var temp =  value.split(".");
                  if(temp && temp.length != 2){
                      var title = "Warning !";
                      var base_warnings =  'Please Enter in "+0.00" format'
                      this.do_warn(_t(title), base_warnings);
                      return false;
                  }
                  else if(temp && temp[0] && temp[0].length != 0){
                      if(temp[0].indexOf("+") == 0){
                          if(temp[0].length > 2){
                              var title = "Warning !";
                              var base_warnings =  'Please Enter in "+0.00" format'
                              this.do_warn(_t(title), base_warnings);
                              return false;
                          }
                      }else{
                          var title = "Warning !";
                          var base_warnings =  'Please Enter in "+0.00" format'
                          this.do_warn(_t(title), base_warnings);
                          return false;
                      }
                       
                  }
               }else if(value){
                   if(value.indexOf("+") == 0){
                      if(value.length > 2){
                          var title = "Warning !";
                          var base_warnings =  'Please Enter in "+0.00" format'
                          this.do_warn(_t(title), base_warnings);
                          return false;
                      }
                  }else{
                      var title = "Warning !";
                      var base_warnings =  'Please Enter in "+0.00" format'
                      this.do_warn(_t(title), base_warnings);
                      return false;
                  }
              }
            return true;
        },
        check_number_only_with_double_precision_sign: function(){
              var value = this.$input.val();
              var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
              if(value && ! re.test(value)){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "+/- 00.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
              if(value && ! _.contains(['+', '-'], value.charAt(0))){
                  var title = "Warning !";
                  var base_warnings =  'Please Enter in "+/- 00.00" format'
                  this.do_warn(_t(title), base_warnings);
                  return false;
              }
                  
              if(value && value.indexOf(".") != -1){
                  var temp =  value.split(".");
                  if(temp && temp.length != 2){
                      var title = "Warning !";
                      var base_warnings =  'Please Enter in "+/- 00.00" format'
                      this.do_warn(_t(title), base_warnings);
                      return false;
                  }
                  else if(temp && temp[0] && temp[0].length != 0){
                      if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
                          if(temp[0].length > 3){
                              var title = "Warning !";
                              var base_warnings =  'Please Enter in "+/- 00.00" format'
                              this.do_warn(_t(title), base_warnings);
                              return false;
                          }
                      }else{
                          var title = "Warning !";
                          var base_warnings =  'Please Enter in "+/- 00.00" format'
                          this.do_warn(_t(title), base_warnings);
                          return false;
                      }
                       
                  }
               }else if(value){
                   if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
                      if(value.length > 3){
                          var title = "Warning !";
                          var base_warnings =  'Please Enter in "+/- 00.00" format'
                          this.do_warn(_t(title), base_warnings);
                          return false;
                      }
                  }else{
                      var title = "Warning !";
                      var base_warnings =  'Please Enter in "+/- 00.00" format'
                      this.do_warn(_t(title), base_warnings);
                      return false;
                  }
              }
            return true
        },
        _onInputblur: function (event) {
            if(this.number_only_with_single_precision) {
                if(this.check_number_only_with_single_precision()){
                    var val = this.$input.val();
                    if(val){
                        if(! isNaN(val)){
                            val = zero_pad(parseFloat(val).toFixed(2).toString(),4)
                            this.$input.val(val)
                        }
                    }
                }
            }
            if(this.number_only_with_three_digit && this.check_number_only_with_three_digit()) {
                var val = this.$input.val()
                if(val){
                    if(! isNaN(val)){
                        val = zero_pad(parseInt(val),3)
                        this.$input.val(val)
                    }
                }
            }
            if(this.number_only_with_double_precision && this.check_number_only_with_double_precision()){
                var val = this.$input.val()
                if(val){
                    if(! isNaN(val)){
                        val = zero_pad(parseFloat(val).toFixed(2).toString(),5)
                        this.$input.val(val)
                    }
                }
            }
            if(this.number_only_with_two_digit_single_precision && this.check_number_only_with_two_digit_single_precision()){
                var val = this.$input.val()
                if(val){
                    if(! isNaN(val)){
                        val = zero_pad(parseFloat(val).toFixed(1).toString(),4)
                        this.$input.val(val)
                    }
                }
            }
            if(this.number_only_with_two_digit_rounding && this.check_number_only_with_two_digit_single_precision()){
                var val = this.$input.val()
                if(val){
                    if(! isNaN(val)){
                        val = (zero_pad(parseInt(val).toFixed(0).toString(),2))
                        this.$input.val(val)
                    }
                }
            }

            if(this.number_only_with_three_digit_rounding && this.check_number_only_with_three_digit_rounding()){
                var val = this.$input.val()
                if(val){
                    if(! isNaN(val)){
                        val = zero_pad(parseInt(val).toFixed(0).toString(),3)
                        this.$input.val(val)
                    }
                }
            }

            if(this.number_only_with_single_precision_sign && this.check_number_only_with_single_precision_sign()) {
                var val = this.$input.val()
                if(val){
                    if( val.indexOf('-') == -1){
                        if(val.indexOf('+') == -1){
                            if(! isNaN(val)){
                                val = "+" + zero_pad(parseFloat(val).toFixed(2).toString(),4)
                            }
                        }else{
                            var tval = val.split("+")[1];
                            if(tval && ! isNaN(tval)){
                                val = "+" + zero_pad(parseFloat(tval).toFixed(2).toString(),4)
                            }
                            
                        }
                    }else{
                        var tval = val.split("-")[1]
                        if(tval && ! isNaN(tval)){
                            val = "-" + zero_pad(parseFloat(tval).toFixed(2).toString(),4)
                        }
                        
                    }
                    this.$input.val(val)
                }
            }
            if(this.number_only_with_single_precision_plus_sign && this.check_number_only_with_single_precision_plus_sign()) {
                var val = this.$input.val()
                if(val){
                    if(val.indexOf('+') == -1){
                        if(! isNaN(val)){
                            val = "+" + zero_pad(parseFloat(val).toFixed(2).toString(),4)
                        }
                    }else{
                        var tval = val.split("+")[1];
                        if(tval && ! isNaN(tval)){
                            val = "+" + zero_pad(parseFloat(tval).toFixed(2).toString(),4)
                        }
                        
                    }
                    this.$input.val(val)
                }
                
            }
            if(this.number_only_with_double_precision_minus_sign && this.check_number_only_with_double_precision_minus_sign()) {
                var val = this.$input.val()
                if(val){
                    if(val.indexOf('-') == -1){
                        if(! isNaN(val)){
                            val = "-" + zero_pad(parseFloat(val).toFixed(2).toString(),5)
                        }
                    }else{
                        var tval = val.split("-")[1];
                        if(tval && ! isNaN(tval)){
                            val = "-" + zero_pad(parseFloat(tval).toFixed(2).toString(),5)
                        }
                        
                    }
                    this.$input.val(val)
                }
            }
            
            if(this.number_only_with_double_precision_sign && this.check_number_only_with_double_precision_sign()) {
                var val = this.$input.val()
                if(val){
                    if(val.indexOf('-') == -1){
                        if(val.indexOf('+') == -1){
                            if(! isNaN(val)){
                                if (val.length > 4){
                                    val = "+" + zero_pad(parseFloat(val).toFixed(2).toString(),5,true)
                                }else{
                                    val = "+" + zero_pad(parseFloat(val).toFixed(2).toString(),4,true)
                                }
                            }
                        }else{
                            var tval = val.split("+")[1];
                            if(tval && ! isNaN(tval)){
                                if (tval.length > 4){
                                    val = "+" + zero_pad(parseFloat(tval).toFixed(2).toString(),5,true)
                                }else{
                                    val = "+" + zero_pad(parseFloat(tval).toFixed(2).toString(),4,true)
                                }
                            }
                        }
                    }else{
                        var tval = val.split("-")[1]
                        if(tval && ! isNaN(tval)){
                            if (tval.length > 4){
                                val = "-" + zero_pad(parseFloat(tval).toFixed(2).toString(),5,true)
                            }else{
                                val = "-" + zero_pad(parseFloat(tval).toFixed(2).toString(),4,true)
                            }
                        }
                    }
                    this.$input.val(val)
                }
            }
        },
//        _onInputKeyPress: function (event) {
//            if(this.number_only_with_single_precision){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.?]*$/;
//                if(value && ! re.test(value)){
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length > 1){
//                         return false;
//                    }
//                 }else if(value){
//                    var temp =  value.length;
//                    if(temp > 1){
//                         return false;
//                    }
//                }
//            }
//            if(this.number_only_with_three_digit) {
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9?]*$/;
//                if(value && ! re.test(value)){
//                    return false;
//                }
//                if(value){
//                    var temp =  value.length;
//                    if(temp > 3){
//                         return false;
//                    }
//                }
//            }
//            if(this.number_only_with_double_precision){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.?]*$/;
//                if(value && ! re.test(value)){
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length > 2){
//                         return false;
//                    }
//                }else if(value){
//                    var temp =  value.length;
//                    if(temp > 2){
//                         return false;
//                    }
//                }
//            }
//            if(this.number_only_with_two_digit_single_precision){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.?]*$/;
//                if(value && ! re.test(value)){
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length > 2){
//                         return false;
//                    }
//                }else if(value){
//                    var temp =  value.length;
//                    if(temp > 2){
//                         return false;
//                    }
//                }
//            }
//            if(this.number_only_with_single_precision_sign){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
//                if(value && ! re.test(value)){
//                    return false;
//                }
//                if(value && ! _.contains(['+', '-'], value.charAt(0))){
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length != 0){
//                        if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
//                            if(temp[0].length > 2){
//                                return false;
//                            }
//                        }else{
//                            return false;
//                        }
//                         
//                    }
//                 }else if(value){
//                     if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
//                        if(value.length > 2){
//                            return false;
//                        }
//                    }else{
//                        return false;
//                    }
//                }
//            }if(this.number_only_with_single_precision_plus_sign){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.\+?]*$/;
//                if(value && ! re.test(value)){
//                    return false;
//                }
//                if(value && ! _.contains(['+'], value.charAt(0))){
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length != 0){
//                        if(temp[0].indexOf("+") == 0){
//                            if(temp[0].length > 2){
//                                return false;
//                            }
//                        }else{
//                            return false;
//                        }
//                         
//                    }
//                 }else if(value){
//                     if(value.indexOf("+") == 0){
//                        if(value.length > 2){
//                            return false;
//                        }
//                    }else{
//                        return false;
//                    }
//                }
//            }
//            if(this.number_only_with_double_precision_sign) {
//                    var value = this.$input.val();
//                    var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
//                    if(value && ! re.test(value)){
//                        return false;
//                    }
//                    if(value && ! _.contains(['+', '-'], value.charAt(0))){
//                        return false;
//                    }
//                    if(value && value.indexOf(".") != -1){
//                        var temp =  value.split(".");
//                        if(temp && temp[0] && temp[0].length != 0){
//                            if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
//                                if(temp[0].length > 3){
//                                    return false;
//                                }
//                            }else{
//                                return false;
//                            }
//                             
//                        }
//                     }else if(value){
//                         if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
//                            if(value.length > 3){
//                                return false;
//                            }
//                        }else{
//                            return false;
//                        }
//                    }
//                }
//            return true
//        },
//        _onInput: function (event) {
//            if(this.number_only_with_single_precision){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "0.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                   var temp =  value.split(".");
//                   if(temp && temp[0] && temp[0].length > 1){
//                         var title = "Warning !";
//                         var base_warnings =  'Please Enter in "0.00" format'
//                         this.do_warn(_t(title), base_warnings);
//                        return false;
//                   }
//                }else if(value){
//                    var temp =  value.length;
//                    if(temp > 1){
//                         var title = "Warning !";
//                         var base_warnings =  'Please Enter in "0.00" format'
//                         this.do_warn(_t(title), base_warnings);
//                         return false;
//                    }
//                }
//            }
//            if(this.number_only_with_three_digit) {
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "000" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value){
//                    var temp =  value.length;
//                    if(temp > 3){
//                        var title = "Warning !";
//                        var base_warnings =  'Please Enter in "000" format'
//                        this.do_warn(_t(title), base_warnings);
//                         return false;
//                    }
//                }
//            }
//            if(this.number_only_with_double_precision){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "00.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                   var temp =  value.split(".");
//                   if(temp && temp[0] && temp[0].length > 2){
//                         var title = "Warning !";
//                         var base_warnings =  'Please Enter in "00.00" format'
//                         this.do_warn(_t(title), base_warnings);
//                        return false;
//                   }
//                }else if(value){
//                    var temp =  value.length;
//                    if(temp > 2){
//                         var title = "Warning !";
//                         var base_warnings =  'Please Enter in "00.00" format'
//                         this.do_warn(_t(title), base_warnings);
//                         return false;
//                    }
//                }
//                
//            }
//            if(this.number_only_with_two_digit_single_precision){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "00.0" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value && value.indexOf(".") != -1){
//                   var temp =  value.split(".");
//                   if(temp && temp[0] && temp[0].length > 2){
//                         var title = "Warning !";
//                         var base_warnings =  'Please Enter in "00.0" format'
//                         this.do_warn(_t(title), base_warnings);
//                        return false;
//                   }
//                }else if(value){
//                    var temp =  value.length;
//                    if(temp > 2){
//                         var title = "Warning !";
//                         var base_warnings =  'Please Enter in "00.0" format'
//                         this.do_warn(_t(title), base_warnings);
//                         return false;
//                    }
//                }
//                
//            }
//            
//            if(this.number_only_with_single_precision_sign){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "+/- 0.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value && ! _.contains(['+', '-'], value.charAt(0))){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "+/- 0.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                    
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length != 0){
//                        if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
//                            if(temp[0].length > 2){
//                                var title = "Warning !";
//                                var base_warnings =  'Please Enter in "+/- 0.00" format'
//                                this.do_warn(_t(title), base_warnings);
//                                return false;
//                            }
//                        }else{
//                            var title = "Warning !";
//                            var base_warnings =  'Please Enter in "+/- 0.00" format'
//                            this.do_warn(_t(title), base_warnings);
//                            return false;
//                        }
//                         
//                    }
//                 }else if(value){
//                     if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
//                        if(value.length > 2){
//                            var title = "Warning !";
//                            var base_warnings =  'Please Enter in "+/- 0.00" format'
//                            this.do_warn(_t(title), base_warnings);
//                            return false;
//                        }
//                    }else{
//                        var title = "Warning !";
//                        var base_warnings =  'Please Enter in "+/- 0.00" format'
//                        this.do_warn(_t(title), base_warnings);
//                        return false;
//                    }
//                }
//            }
//            if(this.number_only_with_single_precision_plus_sign){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.\+?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "+0.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value && ! _.contains(['+'], value.charAt(0))){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "+0.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                    
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length != 0){
//                        if(temp[0].indexOf("+") == 0){
//                            if(temp[0].length > 2){
//                                var title = "Warning !";
//                                var base_warnings =  'Please Enter in "+0.00" format'
//                                this.do_warn(_t(title), base_warnings);
//                                return false;
//                            }
//                        }else{
//                            var title = "Warning !";
//                            var base_warnings =  'Please Enter in "+0.00" format'
//                            this.do_warn(_t(title), base_warnings);
//                            return false;
//                        }
//                         
//                    }
//                 }else if(value){
//                     if(value.indexOf("+") == 0){
//                        if(value.length > 2){
//                            var title = "Warning !";
//                            var base_warnings =  'Please Enter in "+0.00" format'
//                            this.do_warn(_t(title), base_warnings);
//                            return false;
//                        }
//                    }else{
//                        var title = "Warning !";
//                        var base_warnings =  'Please Enter in "+0.00" format'
//                        this.do_warn(_t(title), base_warnings);
//                        return false;
//                    }
//                }
//            }
//            if(this.number_only_with_double_precision_sign){
//                var value = this.$input.val();
//                var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
//                if(value && ! re.test(value)){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "+/- 00.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                if(value && ! _.contains(['+', '-'], value.charAt(0))){
//                    var title = "Warning !";
//                    var base_warnings =  'Please Enter in "+/- 00.00" format'
//                    this.do_warn(_t(title), base_warnings);
//                    return false;
//                }
//                    
//                if(value && value.indexOf(".") != -1){
//                    var temp =  value.split(".");
//                    if(temp && temp[0] && temp[0].length != 0){
//                        if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
//                            if(temp[0].length > 3){
//                                var title = "Warning !";
//                                var base_warnings =  'Please Enter in "+/- 00.00" format'
//                                this.do_warn(_t(title), base_warnings);
//                                return false;
//                            }
//                        }else{
//                            var title = "Warning !";
//                            var base_warnings =  'Please Enter in "+/- 00.00" format'
//                            this.do_warn(_t(title), base_warnings);
//                            return false;
//                        }
//                         
//                    }
//                 }else if(value){
//                     if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
//                        if(value.length > 3){
//                            var title = "Warning !";
//                            var base_warnings =  'Please Enter in "+/- 00.00" format'
//                            this.do_warn(_t(title), base_warnings);
//                            return false;
//                        }
//                    }else{
//                        var title = "Warning !";
//                        var base_warnings =  'Please Enter in "+/- 00.00" format'
//                        this.do_warn(_t(title), base_warnings);
//                        return false;
//                    }
//                }
//            }
//            this._super.apply(this, arguments);
//        },
        isValid: function () {
            if(this.mode == 'edit' && this._isValid){
                var value = this.value;
                if(this.number_only_with_single_precision){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_double_precision){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_two_digit_single_precision){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_single_precision_sign){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_single_precision_plus_sign){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_double_precision_minus_sign){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_double_precision_sign){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
                if(this.number_only_with_three_digit){
                    try {
                        return this.validate_char(value);
                    } catch(e) {
                        return false;
                    }
                }
            }
            return this._isValid;
        },
        validate_char: function(value){
            var re;
            var field_name = this.name;
            if(this.number_only_with_single_precision) {
                re = /^[0-9\u06F0-\u06F9\.?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }else{
                    if(value && value.indexOf(".") != -1){
                        var temp =  value.split(".");
                        if(temp && temp[0] && temp[0].length > 1 || temp.length != 2){
                             return false;
                        }
                     }else if(value){
                        var temp =  value.length;
                        if(temp > 1){
                            return false;
                        }
                    }
                    return true;
                }
                
            }
            if(this.number_only_with_three_digit) {
                var value = this.$input.val();
                var re = /^[0-9\u06F0-\u06F9?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }
                if(value){
                    var temp =  value.length;
                    if(temp > 3){
                         return false;
                    }
                }
            }
            if(this.number_only_with_double_precision) {
                re = /^[0-9\u06F0-\u06F9\.?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }else{
                    if(value && value.indexOf(".") != -1){
                        var temp =  value.split(".");
                        if(temp && temp[0] && temp[0].length > 2 || temp.length != 2){
                             return false;
                        }
                     }else if(value){
                        var temp =  value.length;
                        if(temp > 2){
                            return false;
                        }
                    }
                    return true;
                }
                
            }
            if(this.number_only_with_two_digit_single_precision) {
                re = /^[0-9\u06F0-\u06F9\.?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }else{
                    if(value && value.indexOf(".") != -1){
                        var temp =  value.split(".");
                        if(temp && temp[0] && temp[0].length > 2 || temp.length != 2){
                             return false;
                        }
                     }else if(value){
                        var temp =  value.length;
                        if(temp > 2){
                            return false;
                        }
                    }
                    return true;
                }
            }
            if(this.number_only_with_single_precision_sign){
                var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }
                if(value && ! _.contains(['+', '-'], value.charAt(0))){
                    return false;
                }
                if(value.length == 1){
                    return false
                }
                if(value && value.indexOf(".") != -1){
                    var temp =  value.split(".");
                    if(temp && temp.length != 2){
                        return false;
                    }
                    if(temp && temp[0] && temp[0].length != 0){
                        if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
                            if(temp[0].length > 2){
                                return false;
                            }
                        }else{
                            return false;
                        }
                         
                    }
                 }else if(value){
                     if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
                        if(value.length > 2){
                            return false;
                        }
                    }else{
                        return false;
                    }
                }
            }
            if(this.number_only_with_single_precision_plus_sign){
                var re = /^[0-9\u06F0-\u06F9\.\+?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }
                if(value && ! _.contains(['+'], value.charAt(0))){
                    return false;
                }
                if(value.length == 1){
                    return false
                }
                if(value && value.indexOf(".") != -1){
                    var temp =  value.split(".");
                    if(temp && temp.length != 2){
                        return false;
                    }
                    else if(temp && temp[0] && temp[0].length != 0){
                        if(temp[0].indexOf("+") == 0){
                            if(temp[0].length > 2){
                                return false;
                            }
                        }else{
                            return false;
                        }
                         
                    }
                 }else if(value){
                     if(value.indexOf("+") == 0){
                        if(value.length > 2){
                            return false;
                        }
                    }else{
                        return false;
                    }
                }
            }
            if(this.number_only_with_double_precision_minus_sign){
                var re = /^[0-9\u06F0-\u06F9\.\-?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }
                if(value && ! _.contains(['-'], value.charAt(0))){
                    return false;
                }
                if(value.length == 1){
                    return false
                }
                if(value && value.indexOf(".") != -1){
                    var temp =  value.split(".");
                    if(temp && temp.length != 2){
                        return false;
                    }
                    else if(temp && temp[0] && temp[0].length != 0){
                        if(temp[0].indexOf("-") == 0){
                            if(temp[0].length > 3){
                                return false;
                            }
                        }else{
                            return false;
                        }
                         
                    }
                 }else if(value){
                     if(value.indexOf("-") == 0){
                        if(value.length > 3){
                            return false;
                        }
                    }else{
                        return false;
                    }
                }
            }
            if(this.number_only_with_double_precision_sign){
                var re = /^[0-9\u06F0-\u06F9\.\+\-?]*$/;
                if(value && ! re.test(value)){
                    return false;
                }
                if(value && ! _.contains(['+', '-'], value.charAt(0))){
                    return false;
                }
                if(value.length == 1){
                    return false
                }
                if(value && value.indexOf(".") != -1){
                    var temp =  value.split(".");
                    if(temp && temp.length != 2){
                        return false;
                    }
                    else if(temp && temp[0] && temp[0].length != 0 || temp.length != 2){
                        if(temp[0].indexOf("+") == 0 || temp[0].indexOf("-") == 0){
                            if(temp[0].length > 3){
                                return false;
                            }
                        }else{
                            return false;
                        }
                         
                    }
                 }else if(value){
                     if(value.indexOf("+") == 0 || value.indexOf("-") == 0){
                        if(value.length > 3){
                            return false;
                        }
                    }else{
                        return false;
                    }
                }
            }
            return true;
        },
    });


});