function initMap() {
    // labels show (for odoo only)
    checkForChanges();
    function checkForChanges () {
        if($('div[aria-hidden="true"]').length !=0 ){
            setTimeout(checkForChangesAgain, 500);
        }
        else
            setTimeout(checkForChanges, 500);
    };
    function checkForChangesAgain(){
        var labels = $('div[aria-hidden="true"]');
        for (var i=0; i<labels.length; i++)
            labels[i].ariaHidden = false;
        setTimeout(checkForChanges, 500);
    }

    var places = [];
    var markers = [];
    var search_dict = {};
    var distance_rows = [];
    var distance_length = 0;
    var distance_counter = 0;
    var service = new google.maps.DistanceMatrixService();
    var lat = 40.75795344978029;
    var lng = -73.98551942323733;
    const infoWindow = new google.maps.InfoWindow();
   // Create the search box and link it to the UI element.
    const input = document.getElementById("google_maps_search");
    const searchBox = new google.maps.places.SearchBox(input);

    function handleLocationError(browserHasGeolocation, infoWindow, pos) {
        infoWindow.setPosition(pos);
        infoWindow.setContent(
            browserHasGeolocation
                ? "Error: The Geolocation service failed."
                : "Error: Your browser doesn't support geolocation."
        );
        infoWindow.open(map);
    }
    function show_new_markers(locations_list){
        var destinations = [];
        markers = [];
        var bounds = new google.maps.LatLngBounds();
//     center at current location
        bounds.extend({ lat: lat, lng: lng });
        if (!locations_list.length){
//            $(".branch_map_online_appointment .branches").fadeOut("slow");
            $(".branch_map_online_appointment .branches").html(`            <div class="row"
                 style="margin: 0px;padding: 2%;margin-bottom: 3%; width:450px; margin-left:15px;animation-delay: 2s;">
                <div class="col-lg-12">
                    <div class="row" style="margin-bottom: 10px;">
                        <div class="col-lg-2"/>
                        <div class="col-lg-10">
                            <br/>
                        </div>
                    </div>
                    <div class="row" style="margin-bottom: 10px;">
                        <div class="col-lg-1"></div>
                        <div class="col-lg-10">
                            <center><b>No Branches found in this region</b></center>
                        </div>
                        <div class="col-lg-1"></div>
                    </div>
                    <div class="row" style="margin-bottom: 10px;">
                        <div class="col-lg-2"/>
                        <div class="col-lg-10">
                            <br/>
                        </div>
                    </div>
                </div>
            </div>
            `);
            $(".branch_map_online_appointment .branches").fadeOut("slow");
            $(".branch_map_online_appointment .branches").fadeIn("slow");
        }
        locations_list.forEach(([position, title], i) => {
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: `${title}`,
                label: `${i + 1}`,
                optimized: false,
                animation: google.maps.Animation.DROP,
            });
            destinations.push(new google.maps.LatLng(position['lat'], position['lng']));

            markers.push(marker);
            marker.addListener("click", () => {
                console.log(marker.getTitle());
                for (let item of $(".branch_map_online_appointment .branches")[0].children) {
                    item.style.backgroundColor = '';
                }
                $(".branch_map_online_appointment .branches").find('.branch_' + marker.getTitle())[0].style.backgroundColor = '#ffffe9'
            });

            bounds.extend(position);
        });

        map.setCenter(bounds.getCenter());
        map.fitBounds(bounds);
        map.setZoom(map.getZoom()-1);

        if(map.getZoom()> 15){
            map.setZoom(14);
        }

        get_distance(destinations);
    }
    function get_distance(destinations){
        distance_length = Math.ceil(destinations.length/10);
        distance_rows = [];
        distance_counter = 0;
        for (var i=0; i<distance_length; i++){
            service.getDistanceMatrix(
            {
                origins: [new google.maps.LatLng(lat, lng)],
                destinations: destinations.slice(i*10,10*(i+1)),
                travelMode: 'DRIVING',
                drivingOptions: {
                    departureTime: new Date(Date.now()),
                    trafficModel: 'bestguess'
                },
                unitSystem: google.maps.UnitSystem.IMPERIAL,
            }, distance_result);
        }
    }
    function distance_result(response, status) {
        distance_counter ++;
        if (status == "MAX_ELEMENTS_EXCEEDED" | status == "MAX_DIMENSIONS_EXCEEDED" | status == "REQUEST_DENIED")
            alert("system error");
        else if (status == "OVER_QUERY_LIMIT" | status == "UNKNOWN_ERROR")
            alert("try again in a few minutes");
        else if (status == "OK"){
            for (var i=0;i<response.rows[0].elements.length;i++)
                distance_rows.push(response.rows[0].elements[i])
        }

        if (distance_counter == distance_length){
            search_dict.rows = JSON.stringify(distance_rows);

            return $.ajax({
                url: '/online_appointment/branches_show',
                method: "POST",
                data: search_dict,
                }).done(function(modal) {
                    $(".branch_map_online_appointment .branches").html(modal);
                    $('.branch_map_online_appointment .branches .btn_branch').click(function (ev) {
                        window.location.href = '/online_appointment/location?branch=' + $(ev.currentTarget).attr('value');
                    });
                });
        }
    }
    function search_input(){
    // Bias the SearchBox results towards current map's viewport.
        map.addListener("bounds_changed", () => {
            searchBox.setBounds(map.getBounds());
        });

        searchBox.addListener("places_changed", () => {
            places = searchBox.getPlaces();

            if (places.length == 0)
              return;

//            if (places[0].geometry || places[0].geometry.location) {
//                lat = places[0].geometry.location.lat();
//                lng = places[0].geometry.location.lng();
//                map.setCenter({ lat: lat, lng: lng });
//            }

            var region_found = 0;
            search_dict = {};
            for (var i=$(places[0].adr_address).length;i>=0;i--){
            	if ($($(places[0].adr_address)[i]).attr('class') == 'postal-code')
		            search_dict.postal_code = $($(places[0].adr_address)[i])[0].innerText;
        	    else if ($($(places[0].adr_address)[i]).attr('class') == 'locality')
		            search_dict.locality = $($(places[0].adr_address)[i])[0].innerText;
        	    else if ($($(places[0].adr_address)[i]).attr('class') == 'country-name')
		            search_dict.country_name = $($(places[0].adr_address)[i])[0].innerText;
        	    else if ($($(places[0].adr_address)[i]).attr('class') == 'region' && !region_found){
		            search_dict.region = $($(places[0].adr_address)[i])[0].innerText;
            		region_found = 1;
            	}
            }
            return $.ajax({
                url: '/online_appointment/markers_search_based',
                method: "POST",
                data: search_dict,
                }).done(function(json_response) {
                    for (let i = 0; i < markers.length; i++)
                        markers[i].setMap(null);
                    $(".branch_map_online_appointment .branches").html('');
                    show_new_markers(JSON.parse(json_response));
                });
      });
    }
    function users_location(){
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    $('.branch_map_online_appointment #origin_location').html('your location');
                    lat = position.coords.latitude;
                    lng = position.coords.longitude;
                    infoWindow.setPosition({ lat: lat, lng: lng });
                    infoWindow.setContent("Your Location.");
                    infoWindow.open(map);
                    map.setCenter({ lat: lat, lng: lng });

                    const placeId = lat + ',' + lng;
                    const latlng = {
                        lat: parseFloat(lat),
                        lng: parseFloat(lng),
                    };
                    geocoder = new google.maps.Geocoder();
                    geocoder
                        .geocode({ location: latlng })
                        .then(({ results }) => {
                            if (results.length) {
                                console.log(results[0].formatted_address);
                                console.log(results);
                                var counter = 0;
                                var dict = {};
                                for (var i=results[0].address_components.length-1;i>=0;i--){
                                    counter ++;
                                    dict[i] = results[0].address_components[i].long_name;
                                    if (counter == 5)
                                        break;
                                }
                                return $.ajax({
                                    url: '/online_appointment/markers_location_based',
                                    method: "POST",
                                    data: dict,
                                    }).done(function(json_response) {
                                        for (let i = 0; i < markers.length; i++)
                                            markers[i].setMap(null);
                                        $(".branch_map_online_appointment .branches").html('');
                                        if (!$.isEmptyObject(search_dict)){
                                            if (search_dict.hasOwnProperty('rows'))
                                                delete search_dict.rows;
                                            return $.ajax({
                                                url: '/online_appointment/markers_search_based',
                                                method: "POST",
                                                data: search_dict,
                                                }).done(function(json_response) {
                                                    for (let i = 0; i < markers.length; i++)
                                                        markers[i].setMap(null);
                                                    $(".branch_map_online_appointment .branches").html('');
                                                    show_new_markers(JSON.parse(json_response));
                                                });
                                        }
                                    });
                            }
                        })
                },
                () => {
                    alert("Can't get permission to access location.")
                },
            );
        }
        else {
            // Browser doesn't support Geolocation
            handleLocationError(false, infoWindow, map.getCenter());
        }
    }

    var map = new google.maps.Map(document.getElementById("GoogleMapForBranches"), {
        zoom: 14,
        center: { lat: lat, lng: lng },
        disableDefaultUI: true,
        gestureHandling: "greedy",

//        minZoom: 8,
//        maxZoom: 16,
//        restriction: {
//            strictBounds: true,
//        //   latLngBounds: {
//        //     north: -10,
//        //     south: -40,
//        //     east: 160,
//        //     west: 100,
//        //   },
//        },

        zoomControl: true,
        scaleControl: true,
        rotateControl: true,
        rotateControlOptions: {
            position: google.maps.ControlPosition.BOTTOM_CENTER,
        },
        fullscreenControl: true,
        zoomControlOptions: {
            position: google.maps.ControlPosition.LEFT_CENTER,
        },
        streetViewControl: true,
        streetViewControlOptions: {
            position: google.maps.ControlPosition.RIGHT_BOTTOM,
        },
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_CENTER,
        },
    });
    search_input();

//    $('.branch_map_online_appointment #dark_mode').click(function (ev) {
//        map = new google.maps.Map(document.getElementById("GoogleMapForBranches"), {
//            zoom: 14,
//            center: { lat: lat, lng: lng },
//            disableDefaultUI: true,
//            gestureHandling: "greedy",
//            zoomControl: true,
//            scaleControl: true,
//            rotateControl: true,
//            rotateControlOptions: {
//                position: google.maps.ControlPosition.BOTTOM_CENTER,
//            },
//            fullscreenControl: true,
//            zoomControlOptions: {
//                position: google.maps.ControlPosition.LEFT_CENTER,
//            },
//            streetViewControl: true,
//            streetViewControlOptions: {
//                position: google.maps.ControlPosition.RIGHT_BOTTOM,
//            },
//            mapTypeControl: true,
//            mapTypeControlOptions: {
//                style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
//                position: google.maps.ControlPosition.TOP_CENTER,
//            },
//             styles: [
//                 { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
//                 { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
//                 { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
//                 {
//                   featureType: "administrative.locality",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#d59563" }],
//                 },
//                 {
//                   featureType: "poi",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#d59563" }],
//                 },
//                 {
//                   featureType: "poi.park",
//                   elementType: "geometry",
//                   stylers: [{ color: "#263c3f" }],
//                 },
//                 {
//                   featureType: "poi.park",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#6b9a76" }],
//                 },
//                 {
//                   featureType: "road",
//                   elementType: "geometry",
//                   stylers: [{ color: "#38414e" }],
//                 },
//                 {
//                   featureType: "road",
//                   elementType: "geometry.stroke",
//                   stylers: [{ color: "#212a37" }],
//                 },
//                 {
//                   featureType: "road",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#9ca5b3" }],
//                 },
//                 {
//                   featureType: "road.highway",
//                   elementType: "geometry",
//                   stylers: [{ color: "#746855" }],
//                 },
//                 {
//                   featureType: "road.highway",
//                   elementType: "geometry.stroke",
//                   stylers: [{ color: "#1f2835" }],
//                 },
//                 {
//                   featureType: "road.highway",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#f3d19c" }],
//                 },
//                 {
//                   featureType: "transit",
//                   elementType: "geometry",
//                   stylers: [{ color: "#2f3948" }],
//                 },
//                 {
//                   featureType: "transit.station",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#d59563" }],
//                 },
//                 {
//                   featureType: "water",
//                   elementType: "geometry",
//                   stylers: [{ color: "#17263c" }],
//                 },
//                 {
//                   featureType: "water",
//                   elementType: "labels.text.fill",
//                   stylers: [{ color: "#515c6d" }],
//                 },
//                 {
//                   featureType: "water",
//                   elementType: "labels.text.stroke",
//                   stylers: [{ color: "#17263c" }],
//                 },
//               ],
//        });
//    });
    $('.branch_map_online_appointment #current_location').click(function(){
        users_location();
    });
    users_location();
    $(".branch_map_online_appointment .btn_panel")[0].style.display = '';
}