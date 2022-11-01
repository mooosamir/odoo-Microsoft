odoo.define('opt_custom.SwitchCompanyMenu', function (require) {
"use strict";

    var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
    var Session = require('web.Session');
    var session = require('web.session');
    var rpc = require('web.rpc');
    var utils = require('web.utils');

    Session.include({
       setCompanies: function (main_company_id, company_ids, reload=1) {
            var hash = $.bbq.getState()
            hash.cids = company_ids.sort(function(a, b) {
                if (a === main_company_id) {
                    return -1;
                } else if (b === main_company_id) {
                    return 1;
                } else {
                    return a - b;
                }
            }).join(',');
            utils.set_cookie('cids', hash.cids || String(main_company_id));
            $.bbq.pushState({'cids': hash.cids}, 0);
            if (reload)
                location.reload();
        },
    });

    SwitchCompanyMenu.include({
        _onSwitchCompanyClick: function (ev) {
            if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
                return;
            }
            ev.preventDefault();
            ev.stopPropagation();
            var dropdownItem = $(ev.currentTarget).parent();
            var dropdownMenu = dropdownItem.parent();
            var companyID = dropdownItem.data('company-id');
            var allowed_company_ids = this.allowed_company_ids;
            if (dropdownItem.find('.fa-square-o').length) {
                // 1 enabled company: Stay in single company mode
                if (this.allowed_company_ids.length === 1) {
                    if (this.isMobile) {
                        dropdownMenu = dropdownMenu.parent();
                    }
                    dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                    dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                    allowed_company_ids = [companyID];
                } else { // Multi company mode
                    allowed_company_ids.push(companyID);
                    dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                }
            }
            $(ev.currentTarget).attr('aria-pressed', 'true');
            session.setCompanies(companyID, allowed_company_ids, 0);
            rpc.query({
                model: 'res.company',
                method: 'update_company',
                args : [[], companyID]
            }).then(function () {
                location.reload();
            })
//            if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
//                return;
//            }
//            ev.preventDefault();
//            ev.stopPropagation();
//            var dropdownItem = $(ev.currentTarget).parent();
//            var dropdownMenu = dropdownItem.parent();
//            var companyID = dropdownItem.data('company-id');
//            // Multi company mode
//            var allowed_company_ids = [companyID];
//            $(ev.currentTarget).attr('aria-pressed', 'true');
//
//            if (allowed_company_ids.includes(companyID))
//                session.setCompanies(companyID, allowed_company_ids);
        },
    });

});