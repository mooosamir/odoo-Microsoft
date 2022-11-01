odoo.define('online_appointment.google_maps', function (require) {

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var publicWidget = require('web.public.widget');

    var _t = core._t;

    publicWidget.registry.OnlineAppointmentGoogleMaps = publicWidget.Widget.extend({
        selector: '#GoogleMapForBranches',
        start: function () {
            var self = this;
            var res = this._super.apply(this.arguments).then(function () {
                $('#GoogleMapForBranches').after("<script src='https://maps.googleapis.com/maps/api/js?key=AIzaSyArYgVUuHv7YDmcTxYRBLDlv6M_OG_BE0U&callback=initMap&libraries=places&v=weekly' async/>");
            });
            return res;
        },
    });
});