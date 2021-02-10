// document.getElementById('aircraftICAOFlight').textContent = "Loading";
// document.getElementById('aircraftCallsignICAO').textContent = "Loading";
document.getElementById('totalDistance').textContent = "Loading";
document.getElementById('aircraftICAO').textContent = "Loading";
document.getElementById('aircraftCallsign').textContent = "Loading";


// Responsive chart and hide control buttons on Plotly charts
var config = {
    responsive: true,
    displayModeBar: false
};

// To use OpenStreetMap default tile layer
var streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// To use OpenStreetMap Stadia tile layer
var Stadia_AlidadeSmooth = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
});

var Stadia_AlidadeSmoothDark = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
});

// Leaflet.Terminator https://github.com/joergdietrich/Leaflet.Terminator
var dayNightLayer = L.terminator();

// Initialize all of the LayerGroups we'll be using
var layersRightMap = {
    RoutePoints: new L.FeatureGroup(),
    RouteLines: new L.FeatureGroup(),
    DayNight: dayNightLayer,
};

var baseMaps = {
    "Streets": streets,
    "Gray": Stadia_AlidadeSmooth,
    "Dark": Stadia_AlidadeSmoothDark
};

// Creating our initial map object
// L.map accepts 2 arguments: id of the HTML element to insert 
// the map, and an object containing the initial options for the new map
var mapAirplanes = L.map("mapAircraft", {
    // For Houston uncomment:
    // center: [31.56, -96.47],
    center: [0, 0],
    zoom: 2,
    scrollWheelZoom: false, //Disable scroll wheel zoom on Leaflet
    layers: [
        layersRightMap.RoutePoints,
        layersRightMap.RouteLines
    ],
    fullscreenControl: true,
});

// Add our tile layer to the map
streets.addTo(mapAirplanes);

// Create an overlays object to add to the layer control
var overlays = {
    "Check Points": layersRightMap.RoutePoints,
    "Route": layersRightMap.RouteLines,
    "Day/Night": layersRightMap.DayNight
};


// Create a control for our layers, add our overlay layers to it
L.control.layers(baseMaps, overlays).addTo(mapAirplanes);

// Return date formated to local string
function formatDate(myDate) {
    /* Date.prototype.toLocaleDateString()
     https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString */
    var timeOptions = { year: 'numeric', month: 'numeric', day: 'numeric' };
    // timeOptions.timeZone = 'UTC';
    // Retrieve the newest meas time and convert the format
    var newestData = new Date(myDate * 1000);
    var newestDataTime = newestData.toLocaleTimeString("en-US", timeOptions);
    return newestDataTime
}

// function to calculate the distance
function distCalc(origin, destination) {
    var from = turf.point(origin);
    var to = turf.point(destination);
    var options = { units: 'miles' };
    return distance = turf.distance(from, to, options);
}

// function to access the api and get the json data based on icao24
function getDataICAO(icao24) {
    url_icao24 = `/airtraffic/api/v1.0/aircrafts-data/icao24/${icao24}`

    // Clear the layers before redraw the map
    layersRightMap.RoutePoints.clearLayers();
    layersRightMap.RouteLines.clearLayers();

    d3.json(url_icao24).then((importData) => { createMarker(importData) });

};

// function to access the api and get the json data based on callsign
function getDataCallsign(callsign) {
    url_icao24 = `/airtraffic/api/v1.0/aircrafts-data/callsign/${callsign}`

    // Clear the layers before redraw the map
    layersRightMap.RoutePoints.clearLayers();
    layersRightMap.RouteLines.clearLayers();

    d3.json(url_icao24).then((importData) => { createMarker(importData) });
};

/* Data binding with the enter function to populate 
    the dropdown menu with subject ids available */
function selectOptionAddText(domElement, enterData) {
    d3.select(domElement)
        .selectAll('option')
        .data(enterData)
        .enter()
        .append('option')
        .attr("value", function (data, index) {
            return data;
        })
        .text(function (data, index) {
            return data;
        });
}

/* function to access the api and get the json 
data to populate the dropdown menus */
function loadDropdown() {
    url_icao24 = `/airtraffic/api/v1.0/aircrafts-data`
    d3.json(url_icao24).then((importData) => {
        createDropdownMenu(importData)
    });
};

// Create dropdown menu
function createDropdownMenu(importData) {
    var icao24Array = []
    var callsignArray = []
    importData.forEach(element => {
        if (element.icao24 != '') {
            icao24Array.push(element.icao24)
        };
        if (element.callsignArray != '') {
            callsignArray.push(element.callsign)
        };
    })

    // Sort arrays
    icao24Array.sort();
    callsignArray.sort();
    // Remove empty strings on the array
    var newIcao24Array = icao24Array.filter(function (e) {
        return e === 0 ? '0' : e
    })
    var newcallsignArray = callsignArray.filter(function (e) {
        return e === 0 ? '0' : e
    })
    // Add the options for the dropdown menu
    selectOptionAddText('#selectICAO24', newIcao24Array)
    selectOptionAddText('#selectCallsign', newcallsignArray)
}

// Event listener to update page based on the dropdown selection
function updatePageICAO() {
    // Select the dropdown and set the variable with the value of the dropdown
    var dropdown = d3.select('#selectICAO24');
    var dropdownValue = dropdown.property('value');

    // Pass the selected value to the function that will 
    // get the data based on the selected value
    getDataICAO(dropdownValue);
};

// Event listener to update page based on the dropdown selection
function updatePageCallsign() {
    // Select the dropdown and set the variable with the value of the dropdown
    var dropdown = d3.select('#selectCallsign');
    var dropdownValue = dropdown.property('value');

    // Clear the layers before redraw the map
    layersRightMap.RoutePoints.clearLayers();
    layersRightMap.RouteLines.clearLayers();


    // Pass the selected value to the function that will 
    // get the data based on the selected value
    getDataCallsign(dropdownValue);
};


// function to create the markers and the marker layer
function createMarker(data) {
    // create array of markers
    // create array of markers
    var markersArray = [];
    var latlngsPolyline = [];
    var allAircrafts = [];
    var allFligths = [];
    var totalDist = 0;
    var nn = 0;
    data.forEach(element => {
        // console.log([element.latitude, element.longitude]);
        var marker = L.circle([element.latitude, element.longitude], {
            radius: 5000,
            color: "red"
        }).bindPopup(`<h5>Aircraft Info:</h5><hr>
        ICAO24 / Mode S Code (hex): <a href='https://opensky-network.org/aircraft-profile?icao24=${element["icao24"]}' target="_blank">${element["icao24"]}</a><br/>
                    Callsign: <a href='https://flightaware.com/resources/registration/${element["callsign"]}' target="_blank">${element["callsign"]}</a><br/>
                    Origin country: ${element["origin_country"]}<br/>
                    Time of position update: ${formatDate(element["time_position"])}<br/>
                    Time of last update: ${formatDate(element["last_contact"])}<br/>
                    Longitude: ${element["longitude"]}<br/>
                    Latitude: ${element["latitude"]}<br/>
                    Altitude ${element["baro_altitude"]} m | ${Math.round(element["baro_altitude"] * 3.28084)} ft<br/>
                    On ground: ${element["on_ground"]}<br/>
                    Velocity: ${element["velocity"]} m/s | ${Math.round(element["velocity"] * 2.23694)} mph <br/>
                    True track: ${element["true_track"]}° (north=0°)<br/>
                    Vertical rate: ${element["vertical_rate"]} m/s<br/>
                    Sensors ID: ${element["sensors"]}<br/>
                    Geometric altitude: ${element["geo_altitude"]} m | ${Math.round(element["geo_altitude"] * 3.28084)} ft<br/>
                    Transponder code: ${element["squawk"]}<br/>
                    Special purpose indicator: ${element["spi"]}<br/>
                    Position_source: ${element["position_source"]}<br/>
                    For more details: <a href='https://flightaware.com/live/flight/${element["callsign"]}' target="_blank">link</a>
                    `, { "background": "#2c3e50" })
        marker.addTo(layersRightMap['RoutePoints']);


        markersArray.push(marker);
        latlngsPolyline.push([element.latitude, element.longitude]);
        if (allAircrafts.includes(element["icao24"])) {
            5
        } else {
            allAircrafts.push(element["icao24"])
        }
        if (allFligths.includes(element["callsign"])) {
            5
        } else {
            allFligths.push(element["callsign"])
        };


    });

    // Verify how many differents flight for the same aircraft
    // or how many different aircrafts for the same flight
    document.getElementById('aircraftICAOFlight').textContent = `${allAircrafts.length} `;
    document.getElementById('aircraftCallsignICAO').textContent = `${allFligths.length} `;


    // Add lines based on the coordinates
    var polyline = L.polyline(latlngsPolyline, { color: 'blue' });
    polyline.addTo(layersRightMap['RouteLines'])

    // zoom the map to the polyline
    mapAirplanes.fitBounds(polyline.getBounds());


    // calculate the total distance
    var totalDist = 0
    for (var i = 0; i < latlngsPolyline.length - 1; i++) {
        totalDist = totalDist + distCalc(latlngsPolyline[i + 1], latlngsPolyline[i])
    }
    totalDist = Math.round(totalDist);
    document.getElementById('totalDistance').textContent = `${totalDist.toLocaleString()} (mi)`;

    // Aircraft name or flight name
    document.getElementById('aircraftICAO').textContent = `${data[1].icao24} `;
    document.getElementById('aircraftCallsign').textContent = `${data[1].callsign} `;


};



// Initialize the map
// getDataICAO('ace6e2');
getDataCallsign('AAL2028')

// loadDropdown();

// Handler for the dropdown change for ICAO24
d3.select('#selectICAO24').on('change', updatePageICAO);

// Handler for the dropdown change for Callsign
d3.select('#selectCallsign').on('change', updatePageCallsign);



