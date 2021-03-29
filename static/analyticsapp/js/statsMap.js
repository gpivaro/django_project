// Map showing the access location


// Generate Leaflet map
function generateMap(data) {

    // Layer Groups
    var dataPoints = []
    data.forEach(element => {
        dataPoints.push(L.marker([element.latitude, element.longitude]).bindPopup(`${element.absolute_uri}`))
    });
    var dataPointsLayer = L.layerGroup(dataPoints);

    // Map tile
    var streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    // Layers Control
    var map = L.map('statsMap', {
        center: [25, 25],
        zoom: 2,
        layers: [streets, dataPointsLayer]
    });

    var baseMaps = {
        "Streets": streets
    };

    var overlayMaps = {
        "Visitors location": dataPointsLayer
    };

    L.control.layers(baseMaps, overlayMaps).addTo(map);

    var baseMaps = {
        "<span style='color: gray'>Streets</span>": streets
    };



};

// Use AJAX to get the access data from API
$(document).ready(function () {

    // Set the request to the backend using Ajax and PUT method
    req = $.ajax({
        url: '/analytics/show-visitors/all/',
        type: 'GET',
        success: function (data) {
            // console.log(data);

            // generate the map once the page loads
            generateMap(data)

        },
        error: function (error) {
            console.log(error);
        }
    });

});




