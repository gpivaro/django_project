
// Define variables for our tile layers
var attribution =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
var titleUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var OpenStreetTiles = L.tileLayer(titleUrl, { attribution });

function loadRoute(icao24) {
    url_icao24 = `http://127.0.0.1:5000/api/v1.0/aircraft-icao24/${icao24}`
    d3.json(url_icao24).then((importData) => {
        console.log(importData);

        var icaoData = []
        importData.forEach(function (element) {
            if (element.latitude) {
                circles = L.circle([element.latitude, element.longitude], {
                    fillOpacity: 0.75,
                    color: "blue",
                    fillColor: "black",
                    // Adjust radius
                    radius: 100
                });
                icaoData.push(circles);
            }
        })

        var map = L.map("map", {
            // center: [39, -99],
            // zoom: 4,
            center: [0, 0],
            zoom: 2,
            layers: [OpenStreetTiles, icaoLayer],
            scrollWheelZoom: false //Disable scroll wheel zoom on Leaflet
        });
    }
    )
}

// console.log(myData);

icao24 = 'a5cd55'
icao24 = 'a6ec56'
loadRoute(icao24)

// Event listen to update page based on the dropdown selection
function updatePage() {

    var dropdown = d3.select('#selectICAO24');
    var dropdownValue = dropdown.property('value');
    console.log(dropdownValue);

    // Parse the dropdown values as integer
    var SubjectID = parseInt(dropdownValue);

    // Build the plot with the new stock
    loadRoute(SubjectID);
};

// Handler for the dropdown change
d3.select('#selectICAO24').on('change', updatePage);


// var container = L.DomUtil.get('map');
//         if (container != null) {
//             console.log('A')
//             container._leaflet_id = null;
//             // map.remove();
//             // map.invalidateSize();

//             var icaoLayer = L.layerGroup(icaoData);
//             var map = L.map("map", {
//                 // center: [39, -99],
//                 // zoom: 4,
//                 center: [0, 0],
//                 zoom: 2,
//                 layers: [OpenStreetTiles, icaoLayer],
//                 scrollWheelZoom: false //Disable scroll wheel zoom on Leaflet
//             });
//         } else {

//             console.log('B')
//             // map.off();
//             // map.remove();
//             // map.invalidateSize();
//             var icaoLayer = L.layerGroup(icaoData);
//             var map = L.map("map", {
//                 // center: [39, -99],
//                 // zoom: 4,
//                 center: [0, 0],
//                 zoom: 2,
//                 layers: [OpenStreetTiles, icaoLayer],
//                 scrollWheelZoom: false //Disable scroll wheel zoom on Leaflet
//             });

// return map