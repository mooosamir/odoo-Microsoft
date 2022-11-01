odoo.define('ks_theme_kernel.ks_clock_widget', function(require){
"use strict";

var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');

var _t = core._t;
var global_self = null;

var KsClock = Widget.extend({
    template: 'ks_clock',
    events: {
        'click': '_onClick',
    },

    init: function () {
        var res = this._super.apply(this, arguments);
        return res;
    },

    willStart: function () {
        global_self = this;
        return this._super();
    },

    start: function () {
        var self = this;
        var options = {};
        var user_lang = session.user_context.lang.replace("_", "-");
        return this._super().then(function () {
            options = {
                timeZone : session.user_context.tz, // "Asia/Kolkata"
    //                    hour12 : res.ks_time_format == 'hour24' ? false : true,    // true or false
                hour12 : true,    // true or false
                hour : "2-digit",  // numeric or 2-digit
                minute : "2-digit", // numeric or 2-digit
//                second : "2-digit"  // numeric or 2-digit
            }
            var bHeight = $('.app-sidebar-menu-bottom').outerHeight();
            var uHeight = $('.o_user_menu').outerHeight();
//                    if (res.ks_time_format == 'hour24' ? false : true){
            $('.app-sidebar-menu').attr('style','max-height:calc(100% - '+ (bHeight + uHeight + 23) + 'px)');
            self.$el.removeClass('d-none');
            setInterval(self.renderTime, 1000, options, user_lang);
        });
    },
    
    // No functionality on click for now(alarm or world-clock)
    _onClick: function (ev) {
        ev.preventDefault();
//        var msg = new SpeechSynthesisUtterance();
//        var voices = window.speechSynthesis.getVoices();
//        msg.voice = voices[10]; // Note: some voices don't support altering params
//        msg.voiceURI = 'Google हिन्दी';
//        msg.text = 'Hi ' + session.name + ' the time is ' + ev.currentTarget.innerText;
//        msg.lang = 'hi-IN';
        if ('speechSynthesis' in window) {
            //If browser has Synthesis support
            var msg = new SpeechSynthesisUtterance(ev.currentTarget.innerText);
            msg.volume = 1; // 0 to 1
            msg.rate = 1; // 0.1 to 10
            msg.pitch = 1; //0 to 2
            msg.lang = session.user_context.lang.replace("_", "-");
            var user_lang = session.user_context.lang.slice(0,2);
            var u_lang = speechSynthesis.getVoices().filter(function(voice) {return voice.lang.includes(user_lang)})[0];
            if (u_lang){ msg.voice = u_lang; }
            else{
                msg.voice = speechSynthesis.getVoices().filter(function(voice) {return voice.lang.includes("en-US")})[0];
            }
            window.speechSynthesis.speak(msg);
        }
    },

    renderTime: function(options, user_lang){
        this.$(".ks_clock_text").text(global_self.getTime(options, user_lang));
    },

    getTime: function(options, user_lang) {
        try{
            var time = new Date().toLocaleTimeString([user_lang, "en-US"], options);
        }
        catch(err){
            if (err instanceof RangeError){
                options.timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                var time = new Date().toLocaleTimeString([user_lang, "en-US"], options);
                this.do_warn(_t("Warning"), _t("The selected timezone is depreciated.Please change the timezone"));
            }
        }
        finally{
           return time;
        }
    },

});

SystrayMenu.Items.push(KsClock);
return KsClock;

});
