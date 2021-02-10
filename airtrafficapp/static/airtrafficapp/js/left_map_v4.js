document.getElementById('numAircrafts').textContent = "Wait... Loading";
document.getElementById('totalNumAirports').textContent = "Wait... Loading";
document.getElementById('totalAircraftDatabase').textContent = "Wait... Loading";




d3.json('/airtraffic/analytics/show-visitors/count/').then((visitsData) => {
    console.log(visitsData.visits)
    document.getElementById('pageVisits').textContent = `${visitsData.visits}`;
});
// $(function () { $('#exampleModal').modal('show'); });


//  API endpoints created for this project
var aircrafts_api_url = "/airtraffic/api/v1.0/aircrafts-data/"

// To use OpenStreetMap default tile layer
var streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

// Responsive chart and hide control buttons on Plotly charts
var config = {
    responsive: true,
    displayModeBar: true
};

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
var layersLeftMap = {
    Aircrafts: new L.FeatureGroup(),
    Airports: new L.FeatureGroup(),
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
var myMap = L.map("map", {
    // For Houston uncomment:
    // center: [31.56, -96.47],
    center: [0, 0],
    zoom: 2,
    scrollWheelZoom: false, //Disable scroll wheel zoom on Leaflet
    layers: [
        layersLeftMap.Aircrafts,
        layersLeftMap.Airports
    ],
    fullscreenControl: true,
});

// Add our tile layer to the map
streets.addTo(myMap);

// Create an overlays object to add to the layer control
var overlays = {
    "Aircrafts": layersLeftMap.Aircrafts,
    "Airports": layersLeftMap.Airports,
    "Day/Night": layersLeftMap.DayNight
};


// Create a control for our layers, add our overlay layers to it
L.control.layers(baseMaps, overlays).addTo(myMap);

// Create a legend to display information about our map
var info = L.control({
    position: "bottomright"
});

// When the layer control is added, insert a div with the class of "legend"
info.onAdd = function () {
    var div = L.DomUtil.create("div", "legend");
    return div;
};

// Add the info legend to the map
info.addTo(myMap);
//   Markers With Custom Icons
var aircraftIcon = L.icon({
    iconUrl: '/static/airtrafficapp/images/Airplane_wwwroot_uploads_svg_symbol_0qvhey5-airplane-vector.svg',
    iconSize: [38 / 2, 95 / 2], // size of the icon
});


/* Date.prototype.toLocaleDateString()
     https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString */
var timeOptions = { year: 'numeric', month: 'numeric', day: 'numeric' };
// Return date formated to local string
function formatDate(myDate) {
    // timeOptions.timeZone = 'UTC';
    // Retrieve the newest meas time and convert the format
    var newestData = new Date(myDate * 1000);
    var newestDataTime = newestData.toLocaleTimeString("en-US", timeOptions);
    return newestDataTime
}

function aircraftLayer(flightData) {
    // Display on the screen the number of cleaned data points 
    var totalFlightMap = flightData.length;
    document.getElementById('numAircrafts').textContent = `${totalFlightMap.toLocaleString()} (${formatDate(flightData[0].time)})`;


    // add markers to the aircraft layer
    flightData.forEach(function (element) {
        marker = L.marker([element.latitude, element.longitude], {
            icon: aircraftIcon,
        }).bindPopup(`<h5>AirCraft Information</h5><hr>
                ICAO24 / Mode S Code (hex): <a href='https://opensky-network.org/aircraft-profile?icao24=${element["icao24"]}' target="_blank">${element["icao24"]}</a><br/>
                Callsign: <a href='https://flightaware.com/live/flight/${element["callsign"]}' target="_blank">${element["callsign"]}</a><br/>
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
        marker.addTo(layersLeftMap['Aircrafts']);
    });

    generateAirCraftPlots(flightData);
}

function airportsLayer(airportData) {
    // Display on the screen the number of airports
    document.getElementById('totalNumAirports').textContent = `${airportData[0].Country} ${airportData.length.toLocaleString()}`;

    d3.json(`/airtraffic/api/v1.0/country-coordinates/${airportData[0].Country}`).then((CountryData) => {
        console.log(CountryData[0]);
        myMap.setView([CountryData[0].latitude, CountryData[0].longitude], 4);
    })


    // add marker for the airports
    airportData.forEach(function (element) {
        if (element.Country) {
            circles = L.circle([element.Latitude, element.Longitude], {
                fillOpacity: 0.75,
                color: "green",
                fillColor: "black",
                // Adjust radius
                radius: 100
            }).bindPopup(`<h5>${element["Name"]}</h5><hr>
              Airport ID: ${element["AirportID"]}<br/>
              City: ${element["City"]}<br/>
              Country: ${element["Country"]}<br/>
              DST: ${element["DST"]}<br/>
              IATA: ${element["IATA"]}<br/>
              ICAO: ${element["ICAO"]}<br/>
              Altitude: ${element["Altitude"]} m<br/>
              Latitude: ${element["Latitude"]}<br/>
              Longitude: ${element["Longitude"]}<br/>
              Source: ${element["Source"]}<br/>
              Timezone: ${element["Timezone"]}<br/>
              Type: ${element["Type"]}<br/>
              Tz database time zone: ${element["Tzdatabasetimezone"]}<br/>
              For more details: <a href='https://ourairports.com/airports/${element["ICAO"]}' target="_blank">link</a>`
            )
            circles.addTo(layersLeftMap['Airports']);
        }

        // get the bounds of a layerGroup in Leaflet
        // myMap.fitBounds(layersLeftMap.Airports.getBounds());

    });

    // document.getElementById('exampleModal').remove();



}

// call the API and create the Aircrafts layer
async function createLayerAircrafts(aircrafts_api_url) {
    d3.json(aircrafts_api_url).then((flightData) => {
        aircraftLayer(flightData);
        createDropdownMenu(flightData);

    });
}

// call the API and create the Airports layer
function createAirportsLayer(url) {
    d3.json(url).then((airportData) => {
        airportsLayer(airportData)
    });
}

/* function to access the api and get the json 
data to populate the dropdown menus */
function loadDropdownAirport() {
    d3.json('/airtraffic/api/v1.0/airports-data/ALL').then((importData) => {
        createDropdownMenuAirPort(importData);
        generateAirportPlots(importData);
    });
};

// Create dropdown menu
function createDropdownMenuAirPort(importData) {
    var airportArray = []
    // console.log(importData);
    importData.forEach(element => {
        if (airportArray.includes(element.Country)) {
            5
        } else {
            airportArray.push(element.Country)
        }

    })
    airportArray.sort();
    selectOptionAddText('#selectAirportCountry', airportArray)

}

// function closeModal() { $('#exampleModal').modal('toggle'); };

// Initialize the map once the page loads for the first time
function initMap() {
    // Initialize the page
    // Load only Brazil fligths to speed the page loading

    createAirportsLayer("/airtraffic/api/v1.0/airports-data/United%20States");

    // $(async function () {
    //     await createLayerAircrafts("/airtraffic/api/v1.0/aircrafts-data/ALL");
    //     $(function () { $('#exampleModal').modal('toggle'); });
    // });

    createLayerAircrafts("/airtraffic/api/v1.0/aircrafts-data/ALL");

    loadDropdownAirport();
    // $('#exampleModal').modal('toggle');

    // closeModal()
    // Load all fligths
    // createLayerAircrafts("/airtraffic/api/v1.0/aircrafts-data/ALL");




}


// Event listener to update page based on the dropdown selection
function updateAirportCountry() {
    // Select the dropdown and set the variable with the value of the dropdown
    var dropdown = d3.select('#selectAirportCountry');
    var dropdownValue = dropdown.property('value');

    // Clear layers --> https://jsfiddle.net/chk1/g2zcrhr1/
    layersLeftMap.Airports.clearLayers();
    // layersLeftMap.Aircrafts.clearLayers();


    // Call the function that generate the airport layer
    createAirportsLayer(`/airtraffic/api/v1.0/airports-data/${dropdownValue}`);
    // createLayerAircrafts(`/api/v1.0/aircrafts-data/${dropdownValue}`);


};


function generateAirCraftPlots(flightData) {
    // ******************************************************************
    // Add plots

    // Create an array with the origin countries
    countrytData = [];
    for (var i = 0; i < flightData.length; i++) {
        // conditional test to get only fligths with
        if (countrytData.includes(flightData[i].origin_country)) {
            var n = 1;
        } else {
            countrytData.push(flightData[i].origin_country)
        }
    };


    // Create an object with the aircrafts by origin country
    originCountryAircraft = [];
    for (var i = 0; i < countrytData.length; i++) {
        // conditional test to get only fligths with
        n = 0;
        for (var j = 0; j < flightData.length; j++) {
            if (countrytData[i] === flightData[j].origin_country) {
                n += 1
            }
        }
        originCountryAircraft.push({ "country": countrytData[i], "aircrafts": n });
    };


    // Sort the samples in descending order of sample values
    originCountryAircraft.sort((a, b) => b.aircrafts - a.aircrafts);
    // Select the top origin country number of aircrafts
    top10originCountryAircraft = originCountryAircraft.slice(0, 10);
    // console.log(top10originCountryAircraft);

    // Reverse the list due to the Plotly requeriments
    top10originCountryAircraft.reverse()


    // Trace1 to display the Aircraft by Country of Origin chart
    var trace1 = {
        x: top10originCountryAircraft.map(element => element.aircrafts),
        y: top10originCountryAircraft.map(element => element.country),
        orientation: "h",
        type: "bar"
    };

    // create an array to be plotted
    var chartData = [trace1];

    var layout = {
        title: "Aircraft by Country of Origin",
        xaxis: {
            title: "Number of aircrafts"
        },
        yaxis: {
            automargin: true,
        },
        // plot_bgcolor: "black",
        // paper_bgcolor: "slategrey"
    }

    // Render the plot to the div tag id "plot"
    Plotly.newPlot("barChart", chartData, layout, config, { displayModeBar: false });


    // Aircraft Altitude Distribution plot
    var trace2 = {
        x: flightData.map(element => element.baro_altitude * 3.28084),
        type: 'histogram',
    };
    var histData = [trace2];


    var layout = {
        title: "Aircraft Altitude Distribution",
        xaxis: {
            title: "Altitude (ft) "
        },
        yaxis: {
            title: "Frequency",
            automargin: true,
        },
        // paper_bgcolor: "slategrey"
    };

    Plotly.newPlot('baroAltitudeHist', histData, layout, config, { displayModeBar: false });

    // Data for position source chart
    var posSource = [];
    var ADSB = 0; var ASTERIX = 0; var MLAT = 0;
    for (var i = 0; i < flightData.length; i++) {
        // conditional test to get position source type
        if (flightData[i].position_source === 0) {
            ADSB += 1;
        }
        else if (flightData[i].position_source === 1) {
            ASTERIX += 1;
        }
        else if (flightData[i].position_source === 2) {
            MLAT += 1;
        }
    };
    posSource.push(
        { "Type": "ADS-B", "Qtd": ADSB },
        { "Type": "ASTERIX", "Qtd": ASTERIX },
        { "Type": "MLAT", "Qtd": MLAT }
    );

    // Position Source Chart
    var data = [{
        values: posSource.map(element => element.Qtd),
        labels: posSource.map(element => element.Type),
        textposition: 'inside',
        domain: { column: 1 },
        hoverinfo: 'label+percent+name',
        hole: .4,
        type: 'pie'
    }];

    var layout = {
        title: 'Aircraft Position Source',
        height: 300,
        width: 500,
        margin: { "t": 35, "b": 0, "l": 0, "r": 10 },
        showlegend: true,
        legend: { "orientation": "h" },
        // paper_bgcolor: "slategrey"
        // grid: { rows: 1, columns: 1 }
    };

    Plotly.newPlot('positionSourcePlot', data, layout, config);


    // Aircraft Speed vs. Altitude Chart
    var trace3 = {
        y: flightData.map(element => element.baro_altitude * 3.28084),
        x: flightData.map(element => element.velocity * 2.23694),
        // text: flightData.map(element => element.callsign),
        text: flightData,
        mode: 'markers',
        type: 'scatter',
        hovertemplate: "<b>Aircraft Info:</b><br><br>" + "ICAO24: %{text.icao24}<br>" + "Flight: %{text.callsign}<br>" +
            "Vertical rate: %{text.vertical_rate:,} m/s<br>" + "Altitude %{text.baro_altitude:,} m<br>" + "Click on the dot for more info."
    };

    var data = [trace3];

    var layout = {
        title: "Aircraft Speed vs. Altitude",
        xaxis: {
            title: "Speed (mph) "
        },
        yaxis: {
            title: "Altitude (ft) ",
            automargin: true,
        },
        // paper_bgcolor: "slategrey"
    }

    Plotly.newPlot('scatterVelAltitude', data, layout, config);

    scatterVelAltitude.on('plotly_click', function (e) {
        // console.log(e);
        var icaoNumber = e.points[0].text.icao24;
        // console.log(icaoNumber)
        // execute the function to redraw the map after the user click on the dot
        getDataICAO(`${icaoNumber}`);
        // display an alert message about the map
        alert(`The route for ${icaoNumber} will be displayed on the right map.`)
        // To open a new window to redirect for more info
        // window.open(`https://opensky-network.org/aircraft-profile?icao24=${icaoNumber}`);
    });

}

function generateAirportPlots(airportData) {
    // Create an array with the airports by countries
    countryAirPorts = [];
    for (var i = 0; i < airportData.length; i++) {
        // conditional test to get only fligths with
        if (countryAirPorts.includes(airportData[i].Country)) {
            var n = 1;
        } else {
            countryAirPorts.push(airportData[i].Country)
        }
    };

    // Create an object with the aircrafts by origin country
    totalAirportsCountry = [];
    for (var i = 0; i < countryAirPorts.length; i++) {
        // conditional test to get only fligths with
        n = 0;
        for (var j = 0; j < airportData.length; j++) {
            if (countryAirPorts[i] === airportData[j].Country) {
                n += 1
            }
        }
        totalAirportsCountry.push({ "country": countryAirPorts[i], "airports": n });
    };

    function filterCountry(d) {
        return d.country === 'United States';
    };

    // var currentCountryAirport = totalAirportsCountry.filter(filterCountry);
    // console.log(currentCountryAirport[0].airports);
    // // Display on the screen the number of cleaned data points 
    // document.getElementById('numAirports').textContent = `${currentCountryAirport[0].country}
    // ${currentCountryAirport[0].airports} `;


    // Sort the samples in descending order of sample values
    totalAirportsCountry.sort((a, b) => b.airports - a.airports);

    // Select the top origin country number of aircrafts
    top10CountryAirports = totalAirportsCountry.slice(0, 10);


    // Reverse the list due to the Plotly requeriments
    top10CountryAirports.reverse()


    // Trace1 to display the Airport by Country Data
    var trace1 = {
        x: top10CountryAirports.map(element => element.airports),
        y: top10CountryAirports.map(element => element.country),
        orientation: "h",
        type: "bar",
        marker: {
            color: 'rgb(142,124,195)'
        }
    };

    // create an array to be plotted
    var chartData = [trace1];

    var layout = {
        title: "Airports by Country",
        xaxis: {
            title: "Number of airports"
        },
        yaxis: {
            automargin: true,
        },
        // paper_bgcolor: "slategrey"
    }

    // Render the plot to the div tag id "plot"
    Plotly.newPlot("barChartAirports", chartData, layout, config);
}


function generateDataBaseSizePlots(queryData) {

    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: queryData.map(element => formatDate(element.time)),
            datasets: [{
                label: '# of aircrafts position info',
                data: queryData.map(element => element.totalDataPoints),
                backgroundColor: ['rgba(255, 99, 132, 0.2)'],
                borderColor: ['rgba(255, 99, 132, 1)'],
                borderWidth: 1
            }]
        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: 'Total Aircrafts Position Recorded By Hour',
                fontSize: 20,
            },
            scales: {
                yAxes: [{
                    scaleLabel: {
                        display: true,
                        labelString: 'Position Information',
                        fontSize: 16,
                    },
                    ticks: {
                        beginAtZero: true
                    }
                }]
            },

        }
    });
}




// Add ChartJS to handle the query data
url_aircrafts_hour = "/airtraffic/api/v1.0/aircrafts-data/byhour"
d3.json(url_aircrafts_hour).then((queryData) => {
    // console.log(queryData);
    generateDataBaseSizePlots(queryData)
    totalValues = 0;
    queryData.forEach(element => {
        totalValues = totalValues + element.totalDataPoints
    });

    // Display on the screen the number of cleaned data points 
    document.getElementById('totalAircraftDatabase').textContent = `${totalValues.toLocaleString()}`;

})



// Handler for the dropdown change of airports
d3.select('#selectAirportCountry').on('change', updateAirportCountry);

// initialize the page
initMap()
