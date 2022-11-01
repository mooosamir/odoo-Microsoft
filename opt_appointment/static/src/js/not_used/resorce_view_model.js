odoo.define('opt_appointment.DashboardModel', function (require) {
    "use strict";

    var AbstractModel = require('web.AbstractModel');
    var Context = require('web.Context');
    var core = require('web.core');
    var fieldUtils = require('web.field_utils');
    var session = require('web.session');

    var DashboardModel = AbstractModel.extend({
        init: function() {
            this._super.apply(this, arguments);
        },
        load: function(params) {
            this.modelName = params.modelName;
            this.fieldNames = params.fieldNames;
            this.fieldsInfo = params.fieldsInfo;
            this.mapping = params.mapping;

            if (!this.preload_def) {
                this.preload_def = $.Deferred();
                $.when(
                    this._rpc({
                        model: this.modelName,
                        method: "check_access_rights",
                        args: ["write", false],
                    }),
                    this._rpc({
                        model: this.modelName,
                        method: "check_access_rights",
                        args: ["unlink", false],
                    }),
                    this._rpc({
                        model: this.modelName,
                        method: "check_access_rights",
                        args: ["create", false],
                    })
                ).then((write, unlink, create) => {
                    this.write_right = write;
                    this.unlink_right = unlink;
                    this.create_right = create;
                    this.preload_def.resolve();
                });
            }

            this.data = {
                domain: params.domain,
                context: params.context,
            };

            return this.preload_def.then(this._loadTimeline.bind(this));
        },
        reload: function (handle, params) {
            if (params.domain) {
                this.data.domain = params.domain;
            }
            if (params.context) {
                this.data.context = params.context;
            }
            return this._loadTimeline();
        },
        _loadTimeline: function() {
            return this._rpc({
                model: this.modelName,
                method: "search_read",
                context: this.data.context,
                fields: this.fieldNames,
                domain: this.data.domain,
            }).then(events => {
                this.data.data = events;
                this.data.rights = {
                    unlink: this.unlink_right,
                    create: this.create_right,
                    write: this.write_right,
                };
            });
        },
    });
    return DashboardModel;

});
