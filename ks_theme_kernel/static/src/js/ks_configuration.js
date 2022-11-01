odoo.define('ks_theme_kernel.ks_configuration', function (require){
   var ks_configuration = require('ks_theme_kernel.ks_configuration_widget');
   var ajax = require('web.ajax');
   var core = require('web.core');
   var rpc = require('web.rpc');
   var menu_name;

   $(document).ready(function(){



        //   THEME CONFIGURATION LAYOUT EVENTS
        $('.ks_sidebar_position').on('click','.ks_menu_list',function(event){
              if ($('.ks_sidebar_position').hasClass('search-filter-open')){
                    $('.o_searchview_more').click();
                    }

              _.each($('.ks_menu_list'),function(ev){
                         $(ev).removeClass('active');   
              })

              $(event.currentTarget).addClass('active')

       });

        $('.ks_sidebar_position').on('click','.ks_searchfilter_overlay',function(event){
              if ($('.ks_sidebar_position').hasClass('search-filter-open')){
                    $('.o_searchview_more').click();
              }
              if ($('.ks_theme_layout').hasClass('ks-layout-open')){
                   $('.ks_configuration').click();
              }
              // Hide Calendar Popup
              $('.bootstrap-datetimepicker-widget').addClass('d-none')
        })

        $('.ks_sidebar_position').on('click','.ks_configuration',function(event){
              if ($('.ks_sidebar_position').hasClass('search-filter-open')){
                    $('.o_searchview_more').click();
                    }
              if ($('.ks_theme_layout').length){
                  if ($('.ks-layout-open').length){
                    $('.ks_theme_layout').removeClass('ks-layout-open');
                    $('body').removeClass('ks-header-size');
                  }
                  else{
                     $('.ks_theme_layout').addClass('ks-layout-open');
                     $('body').addClass('ks-header-size');
                     ks_plane = rpc.query({
                        model : 'ks.home.view',
                        method : 'ks_get_value',
                        args : [[]],
                     }).then(function(ks_plane){
                        if (ks_plane[2] == 'light'){
                            $('#dark_mode').find('input').attr('checked',false);
                            $('#dark_mode').removeClass('active');
                            $('#light_mode').find('input').attr('checked',true);
                            $('#light_mode').addClass('active');
                            $('#ks_theme_color_id').removeClass('d-none');
                            if(ks_plane[1]){
                                $('.ks_configuration.ks-icon-outer.float-right').removeClass('d-none');
                            }
                        }
                        else if(ks_plane[2] == 'dark'){
                            $('#light_mode').find('input').attr('checked',false);
                            $('#light_mode').removeClass('active');
                            $('#dark_mode').find('input').attr('checked',true);
                            $('#dark_mode').addClass('active');
                        }
                  });
                  }
              }
              else{
                  this._ks_config = new ks_configuration();
                  this._ks_config.appendTo($('.ks_sidebar_position')).then(function () {
                     $('.ks_theme_layout').addClass('ks-layout-open');
                     $('body').addClass('ks-header-size');
//                  this is for advance color setting option hide for specific group
                     ks_plane = rpc.query({
                        model : 'ks.home.view',
                        method : 'ks_get_value',
                        args : [[]],
                     }).then(function(ks_plane){
                        if (ks_plane[2] == 'light'){
                            $('#dark_mode').find('input').attr('checked',false);
                            $('#dark_mode').removeClass('active');
                            $('#light_mode').find('input').attr('checked',true);
                            $('#light_mode').addClass('active');
                            $('#ks_theme_color_id').removeClass('d-none');
                            if(ks_plane[4]){
                                $('#ks_theme_advance_colors').removeClass('d-none');
                            }
                        }
                        else if(ks_plane[2] == 'dark'){
                            $('#light_mode').find('input').attr('checked',false);
                            $('#light_mode').removeClass('active');
                            $('#dark_mode').find('input').attr('checked',true);
                            $('#dark_mode').addClass('active');
                        }
                  });
                     var options = {
                        url:function(query) {
                            return "/get/search/suggestions/" + query;
                          },
                        listLocation: "result",
                        theme: "plate-dark",
                        getValue: function(element){
                                    return element.name;

                          },
            //            template: {
            //				type: "iconLeft",
            //				fields: {
            //
            //				}
            //            },
                        list: {
                           match: {
                                    enabled: true,
                            },
                           onChooseEvent:function(ev){
                                 $('.ks-favourite-search').val($('.ks-favourite-search').getSelectedItemData().name);
                                 var menu_item_url = $('.ks-favourite-search').getSelectedItemData().url;
                                 if (!$('.ks_menu_url').hasClass('d-none')){
                                        $('.ks_menu_url').val(menu_item_url);
                                         $('.ks-favourite-search').val('');

                                 }
                            },
                            maxNumberOfElements: 10,
                        },

                    };
                     $('.ks_sidebar_position').find('.ks-favourite-search').easyAutocomplete(options);

                     var $def_headerbgcolor = _ksGetHeaderbgColor();
                     var $def_headertextcolor = _ksGetHeadertextColor();
                     var $def_buttonbgcolor = _ksGetButtonbgColor();
                     var $def_buttontextcolor = _ksGetButtontextColor();
                     var $def_headingbgcolor = _ksGetHeadingbgColor();
                     var $def_headingtextcolor = _ksGetHeadingtextColor();


                     $def_headerbgcolor.then(function(headerbg_color){
                        $('.header-bg-color-picker').spectrum({

                            color: headerbg_color,
                            preferredFormat: "rgba",
                            showInput: true,
                            showInitial: true,
                            change: function(color) {
                                $('.ks_apply_color').attr('disabled',false);
                            }
                        });
                     })
                     $def_headertextcolor.then(function(headertext_color){
                        $('.header-text-color-picker').spectrum({
                            color: headertext_color,
                            preferredFormat: "rgba",
                            showInput: true,
                            showInitial: true,
                            change: function(color) {
                                $('.ks_apply_color').attr('disabled',false);
                            }
                         });
                      });
                     $def_buttonbgcolor.then(function(buttonbg_color){
                         $('.button-bg-color-picker').spectrum({
                            color: buttonbg_color,
                            preferredFormat: "rgba",
                            showInput: true,
                            showInitial: true,
                            change: function(color) {
                                $('.ks_apply_color').attr('disabled',false);
                            }
                         });
                     })
                     $def_buttontextcolor.then(function(buttontext_color){
                         $('.button-text-color-picker').spectrum({
                            color: buttontext_color,
                            preferredFormat: "rgba",
                            showInput: true,
                            showInitial: true,
                            change: function(color) {
                                $('.ks_apply_color').attr('disabled',false);
                            }
                         });
                     })
                     $def_headingbgcolor.then(function(headingbg_color){
                         $('.heading-bg-color-picker').spectrum({
                            color: headingbg_color,
                            preferredFormat: "rgba",
                            showInput: true,
                            showInitial: true,
                            change: function(color) {
                                $('.ks_apply_color').attr('disabled',false);
                            }
                         });
                     })
                     $def_headingtextcolor.then(function(headingtext_color){
                         $('.heading-text-color-picker').spectrum({
                            color: headingtext_color,
                            preferredFormat: "rgba",
                            showInput: true,
                            showInitial: true,
                            change: function(color) {
                                $('.ks_apply_color').attr('disabled',false);
                            }
                         });
                     })
                  });
                  ajax.jsonRpc('/favourite/menu/template','call',{}).then(function(data){

                    $('.ks-favourite-menu-body').append(data);
                    var active_font = $('.current_active_font').val();
                    if (active_font){
                            $('#'+active_font).find('input[name="selectFont"]').attr('checked',true);
                    }
                   var active_color = $('.current_active_color').val();
                   if (active_color){
                            $('#'+active_color).find('input[name="themeColor"]').attr('checked',true);
                    }
                  });

                  ajax.jsonRpc('/updatedcolor/pallete/template','call',{}).then(function(data){

                     $('.ks-color-pallete-all-list').append(data['pallete_html']);
                      var active_color = $('.current_active_color').val();
                      if (active_color){
                            $('#'+active_color).find('input[name="themeColor"]').attr('checked',true);
                    }
                    var current_active_color_pallete = data['current_active_color_pallete'];
                    if (current_active_color_pallete){
                                      $('#'+current_active_color_pallete).find('input[name="themeColor"]').attr('checked',true);
                 
                                
                    }
                     var i = 0
                     _.each($('.ks_theme_color_pallete'),function(ev){
                           
                            color_id =  $(ev).attr('id').split('_')[1];
                            if (parseInt(color_id)>10){
                            if (data['adv_access']){
                                  $('.ks-pallete-delete').removeClass('d-none').addClass('d-inline-flex');
                               }
                                    $('.color-primary-'+color_id).css({
                                                    'background-color': data["new_added_main_color"][i],
                                                });
                                     $('.color-alternate-'+color_id).css({
                                                    'background-color': data["new_added_main_color"][i],
                                                    'opacity': '0.5',
                                                });
                                i+=1;
                              }

                        
                        })
              
                     });
              }


       });

        $('.ks_sidebar_position').on('click','.ks_font',function(event){
              event.stopPropagation();
              event.preventDefault();
              $(".ks-filter-radios").css("pointer-events","none");
              _.each($('.ks_font'),function(ev){
                   $(ev).removeClass('active');
                   $(ev).find('input[name="selectFont"]').attr('checked',false);

              })
              var font_id = $(event.currentTarget).attr('id');
              $(event.currentTarget).addClass('active');
              $(event.currentTarget).find('input[name="selectFont"]').attr('checked',true);
              ajax.jsonRpc('/update/font/css','call',{'font_id': font_id}).then(function(){
                     
                     location.reload();
              });
       });

       $('.ks_sidebar_position').on('click','.ks_theme_color_pallete',function(event){
              event.stopPropagation();
              event.preventDefault();
              $(".ks-color-pallete-all-list").css("pointer-events","none");
              _.each($('.ks_theme_color_pallete'),function(ev){
                   $(ev).removeClass('active');
                   $(ev).find('input[name="themeColor"]').attr('checked',false);
                   })
              var color_id = $(event.currentTarget).attr('id');
              $(event.currentTarget).addClass('active');
              $(event.currentTarget).find('input[name="themeColor"]').attr('checked',true);
              ajax.jsonRpc('/update/colorpallete/css','call',{'color_id': color_id}).then(function(){
                     
                     location.reload();
              });
       })

       $('.ks_sidebar_position').on('change','.ks_menu_names',function(ev){
               
               menu_name = $(ev.currentTarget).val();
               if (menu_name !=''){
                    $('.ks_menu_name_validation').addClass('d-none');
                    var menu_url = $('.ks_menu_url').val();
                    if (menu_url !=''){
                        $('.ks_menu_names').addClass('d-none');
                        $('.ks_menu_url').addClass('d-none');
                        $('.ks_add_line_favourite').removeClass('d-none');
                        $('.ks_menu_url_validation').addClass('d-none');
                        ajax.jsonRpc("/update/favourite/menu", 'call', {'menu_name':menu_name,'menu_url':menu_url}
                        ).then(function(data){
                            if (data){
                            $('.favourite-menu-lines').remove();
                            $('.ks_menu_names').val('');
                            $('.ks_menu_url').val('');
                            $('.ks-favourite-menu-body').append(data);
                            }
                        });
                    }
                    else{

                        $('.ks_menu_url_validation').removeClass('d-none');
                    }
               }


       })

       $('.ks_sidebar_position').on('change','.ks_menu_url',function(ev){
               var menu_name = $('.ks_menu_names').val()
               if (menu_name ==''){
                    $('.ks_menu_name_validation').removeClass('d-none');
               }
               else{
                    $('.ks_menu_name_validation').addClass('d-none');
                    var menu_url = $(ev.currentTarget).val();
                    if (menu_url==''){
                        $('.ks_menu_url_validation').removeClass('d-none');
                    }
                    else{
                        $('.ks_menu_url_validation').addClass('d-none');
                        $('.ks_menu_names').addClass('d-none');
                        $('.ks_menu_url').addClass('d-none');
                        $('.ks_add_line_favourite').removeClass('d-none');
                        ajax.jsonRpc("/update/favourite/menu", 'call', {'menu_name':menu_name,'menu_url':menu_url}
                        ).then(function(data){
                            if (data){
                            $('.favourite-menu-lines').remove();
                            $('.ks_menu_names').val('');
                            $('.ks_menu_url').val('');
                            $('.ks-favourite-menu-body').append(data);
                            }
                        });
                    }
                }

       })

        $('.ks_sidebar_position').on('click','.ks_add_line_favourite',function(ev){
            $('.ks_menu_names').removeClass('d-none');
            $('.ks_menu_url').removeClass('d-none');
            $(ev.currentTarget).addClass('d-none')
        })
         
        $('.ks_sidebar_position').on('click','.menu-edit',function(ev){
             if ($(ev.currentTarget).hasClass('ks-edit-open')){
                $(ev.currentTarget).removeClass('ks-edit-open')
                var line_id = $(ev.currentTarget).parent().find('input').val();
                $(ev.currentTarget).parent().find('.menu-rename').addClass('d-none');
                $(ev.currentTarget).parent().find('.menu-delete').addClass('d-none');
                          
             }
             else{
                            $(ev.currentTarget).addClass('ks-edit-open')
                            var line_id = $(ev.currentTarget).parent().find('input').val();
                            $(ev.currentTarget).parent().find('.menu-rename').removeClass('d-none');
                            $(ev.currentTarget).parent().find('.menu-delete').removeClass('d-none');
             }
        })

        $('.ks_sidebar_position').on('click','.menu-rename',function(ev){
                           var target = $(ev.currentTarget)
                           target.parents('.favourite-menu-lines').find('.ks-menu-name-favourite').addClass('d-none');
                           target.parents('.favourite-menu-lines').find('.ks-menu-name-edit').attr('type','');
                            
         })

        $('.ks_sidebar_position').on('click','.menu-delete',function(ev){
                           var target = $(ev.currentTarget)
                           menu_id = parseInt(target.parent().find('.favourite-menu-id').val());
                            ajax.jsonRpc("/update/favourite/menu", 'call', {'delete':'delete','menu_id':menu_id}
                        ).then(function(data){
                            if (data){
                            $('.favourite-menu-lines').remove();
                            $('.ks-favourite-menu-body').append(data);
                            }
                        });

                             })

        $('.ks_sidebar_position').on('change','.ks-menu-name-edit',function(ev){
               menu_name = $(ev.currentTarget).val();
               menu_id = parseInt($(ev.currentTarget).parents('.favourite-menu-lines').find('.favourite-menu-id').val());
               $(ev.currentTarget).parent().find('.ks-menu-name-favourite').text(menu_name).removeClass('d-none')
               $(ev.currentTarget).attr('type','hidden')
                ajax.jsonRpc("/update/favourite/menu", 'call', {'menu_name':menu_name,'rename':'rename','menu_id':menu_id}
                        );


       })

       $('.ks_sidebar_position').on('click','.ks_cancel_color',function(ev){
              location.reload();

       })

       $('.ks_sidebar_position').on('click','.ks_apply_color',function(ev){
                var color=$(".header-bg-color-picker").spectrum('get').toHexString();
                var headertextcolor=$(".header-text-color-picker").spectrum('get').toHexString();
                var buttonbgcolor=$(".button-bg-color-picker").spectrum('get').toHexString();
                var buttontextcolor=$(".button-text-color-picker").spectrum('get').toHexString();
                var headingbgcolor=$(".heading-bg-color-picker").spectrum('get').toHexString();
                var headingtextcolor=$(".heading-text-color-picker").spectrum('get').toHexString();
                _ksonSaveClickHeaderBg(color,headertextcolor,buttonbgcolor,buttontextcolor,headingbgcolor,headingtextcolor);

       })

       $('.ks_sidebar_position').on('click','.ks-pallete-delete',function(ev){

                   var delete_color_id = $(ev.currentTarget).attr('id');

                   ajax.jsonRpc("/delete/color/pallete", 'call', {'delete_color_id':delete_color_id}
                        ).then(function(){

                                location.reload()
                        })

       })      

//        $('.ks_sidebar_position').on('click', '.ks_reset_color', function (ev) {
//              ajax.jsonRpc("/color/reset", 'call'
//              ).then(function (values) {
//                      var ks_button_scss_path= "/static/src/css/ks_theme_kernel_color.scss";
//                      $.get("/write/updated/backendtheme/color", {
//                                'scss_path': ks_button_scss_path, 'reset_headerbgcolor': values['headerbgcolor'], 'reset_headertxtcolor':values['headertxtcolor'],
//                                'reset_buttonbgcolor':values['buttonbgcolor'],'reset_buttontxtcolor':values['buttontxtcolor'],
//                                'reset_headingbgcolor':values['headingbgcolor'],'reset_headingtxtcolor':values['headingtxtcolor']
//                      }).then(function () {
//                            location.reload();
//                         });
//              });
//        });

       var _ksGetHeaderbgColor = function(e){
                        var ks_theme_kernel_color_path="/static/src/css/ks_theme_kernel_color.scss";
                        return $.get("/get/updated/backendtheme/color", { "header_bg_scss_path":ks_theme_kernel_color_path})
                        }
       var _ksGetHeadertextColor = function(e){
                        var ks_theme_kernel_color_path="/static/src/css/ks_theme_kernel_color.scss";
                        return $.get("/get/updated/backendtheme/color", { "header_text_scss_path":ks_theme_kernel_color_path})
                        }
       var _ksGetButtonbgColor = function(e){
                        var ks_theme_kernel_color_path="/static/src/css/ks_theme_kernel_color.scss";
                        return $.get("/get/updated/backendtheme/color", { "button_bg_scss_path":ks_theme_kernel_color_path})
                        }
       var _ksGetButtontextColor = function(e){
                        var ks_theme_kernel_color_path="/static/src/css/ks_theme_kernel_color.scss";
                        return $.get("/get/updated/backendtheme/color", { "button_text_scss_path":ks_theme_kernel_color_path})
                        }
       var _ksGetHeadingbgColor = function(e){
                        var ks_theme_kernel_color_path="/static/src/css/ks_theme_kernel_color.scss";
                        return $.get("/get/updated/backendtheme/color", { "heading_bg_scss_path":ks_theme_kernel_color_path})
                        }
       var _ksGetHeadingtextColor = function(e){
                        var ks_theme_kernel_color_path="/static/src/css/ks_theme_kernel_color.scss";
                        return $.get("/get/updated/backendtheme/color", { "heading_text_scss_path":ks_theme_kernel_color_path})
                        }
       var _ksonSaveClickHeaderBg = function(color,headertextcolor,buttonbgcolor,buttontextcolor,headingbgcolor,headingtextcolor){
              var $ks_theme_color  =  color;
              var ks_scss_path = "/static/src/scss/themes/default_color.scss";
              var headerbg_color = "$primary: "+$ks_theme_color+";";
              var headertextcolor = "$text-primary: "+headertextcolor+";";
              var buttonbgcolor = "$primary-light: "+buttonbgcolor+";";
              var buttontextcolor = "$sidebar-bg-color: "+buttontextcolor+";";
              var headingbgcolor = "$topmenu-bg-color: "+headingbgcolor+";";
              var headingtextcolor = "$border-color: "+headingtextcolor+";";
              $.get("/write/updated/backendtheme/color", {
                        'scss_path': ks_scss_path, 'headerbgcolor': headerbg_color,'headertextcolor':headertextcolor,
                        'buttonbgcolor':buttonbgcolor, 'buttontextcolor':buttontextcolor,'headingbgcolor':headingbgcolor,'headingtextcolor':headingtextcolor
               }).then(function(data){
//                                 $('.ks_theme_color_pallete').remove();
//                                 $('.ks-color-pallete-all-list').append(data);
//                                 $('.ks_apply_color').attr('disabled','disabled');
                                 location.reload()

               })
          }

       // To hide favt. menu options
       $('.ks_sidebar_position').on('click','.ks-floating-menu-line',function(ev){
            $('.ks-floating-menu-list').addClass('d-none');
            $('.ks-floating-menu-button').removeClass('ks-floating-open');
       })

       $('.ks_sidebar_position').on('click','.ks-floating-menu-button',function(ev){
            if ($(ev.currentTarget).hasClass('ks-floating-open')){
                $('.ks-floating-menu-list').addClass('d-none');
                $(ev.currentTarget).removeClass('ks-floating-open');
                $('.ks-floating-menu-line').tooltip()
            }
            else
            {   $(ev.currentTarget).addClass('ks-floating-open');
                    ajax.jsonRpc('/favourite/floating/template','call',{}).then(function(data){
                    $('.ks-floating-menu-list').remove();
                    $('.ks-favourite-floating-menu').append(data);
                     $('.ks-floating-menu-line').tooltip()
                });
            }
       })

       $('.ks-sidebar-sub-menu-opener').click(function(){
            $('body').toggleClass('ks-submenu-show');
       });

       $('.o_cp_controller').click(function(){
            if ($('.ks_sidebar_position').hasClass('search-filter-open')){
                $('body').removeClass('search-filter-open');
            }
       });

       $('.ks_sidebar_position').on('click','.ks_color_mode',function(event){
            event.stopPropagation();
            event.preventDefault();
            $("#ks_color_mode_option_list").css("pointer-events","none");
            _.each($('.ks_color_mode'),function(ev){
                   $(ev).removeClass('active');
                   $(ev).find('input[name="modeSelect"]').attr('checked',false);
                   })
            $(event.currentTarget).addClass('active');
            $(event.currentTarget).find('input[name="modeSelect"]').attr('checked',true);
            var current_id = $(event.currentTarget).attr('id');
            ajax.jsonRpc('/color/mode','call',{'color_mode':current_id}).then(function(data){
                 location.reload();
            });
       })

       $('.ks_sidebar_position').on('click','.modal-header',function(event){
            if ($('.ks_sidebar_position').hasClass('search-wizard-filter-open')){
                $('.modal-body .o_searchview_more').click();
            }
       })

       $('.ks_sidebar_position').on('click','.modal-footer',function(event){
            if ($('.ks_sidebar_position').hasClass('search-wizard-filter-open')){
                $('.modal-body .o_searchview_more').click();
            }
       })


        var dprocess = _.debounce(function() {
            $(window).trigger('resize');
        }, 100);
        var dprocess2 = _.debounce(function() {
            $(window).trigger('resize');
        }, 500);
        $(document).on('click', 'body .ks_resize_window', function() {
            dprocess();
            dprocess2();
        });
        $(document).on('click', 'body .o_list_record_selector input', function(ev) {
            dprocess();
            dprocess2();
            if ($(this).prop("checked")){
                $(this.closest('tr')).addClass('ks_highlight_row');
            }
            else{
                $(this.closest('tr')).removeClass('ks_highlight_row');
            }
        });
        $(document).on('click', 'body thead .o_list_record_selector input', function(ev) {
            dprocess();
            dprocess2();
            if ($(this).prop("checked")){
                $(this).closest('thead').siblings('tbody').find('tr').addClass('ks_highlight_row');
            }
            else{
                $(this).closest('thead').siblings('tbody').find('tr').removeClass('ks_highlight_row');
            }
        });

        $(window).on('hashchange', function(e){
            if($('a[role="menuitemcheckbox"]')[0] && $('.o_main_navbar .o_searchview_input_container').length == 0)
            {
                $('a[role="menuitemcheckbox"]')[0].click();
                $('a[role="menuitemcheckbox"]')[0].click();
            }
            if (document.URL.includes('menu_id'))
            {
                 var menu_id = document.URL.split('menu_id=').pop();
                 $('.oe_menu_toggler').parent().removeClass('active');
                 var search = `.oe_menu_toggler[data-menu="${menu_id}"]`;
                 $(search).parent().addClass('active');
            }

//            if($('.o_searchview_input_container')){
//                if($('.o_cp_searchview').css('display') == 'none'){
//                    $('.o_searchview_input_container').css('display','none');
//                }
//                else{
//                    $('.o_searchview_input_container').css('display','block')
//                }
//            }

        });

        // Highlight Opened App
        //window.onload=function() {
        //    if (document.URL.includes('menu_id'))
        //        {
        //             var menu_id = document.URL.split('menu_id=').pop();
        //             $('.oe_menu_toggler').parent().removeClass('active');
        //             var search = `.oe_menu_toggler[data-menu="${menu_id}"]`;
        //             $(search).parent().addClass('active');
        //        }
        //}
   })
});

