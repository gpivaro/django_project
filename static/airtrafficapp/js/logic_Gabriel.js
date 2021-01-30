/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* Setup parameters and functions */

// Responsive chart and hide control buttons on Plotly charts
var config = {
    responsive: true,
    displayModeBar: false
};

// Creating our initial map object
/*L.map accepts 2 arguments: id of the HTML element to insert the map, 
and an object containing the initial options for the new map */
var myMap = L.map("map", {
    // For Houston uncomment:
    // center: [31.56, -96.47],
    // For IAH uncomment:
    // center: [29.984, -95.324],
    // zoom: 9,
    center: [0, 0],
    zoom: 2.1,
    scrollWheelZoom: false //Disable scroll wheel zoom on Leaflet
});

// Adding a tile layer (the background map image) to our map.
// Leaflet doesn't have out-of-the-box tile layers, but it allows us to usetile layer APIs. Here, we're using mapbox.
// We use the addTo method to add objects to our map
// Documentation for tileLayer:https://leafletjs.com/reference-1.6.0.html#tilelayer
// L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
//     attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
//     maxZoom: 18,
//     id: "dark-v10",
//     // id: "streets-v11",
//     accessToken: API_KEY
// }).addTo(myMap);



// To use OpenStreetMap instead of MapBox
var attribution =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>contributors';
var titleUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var tiles = L.tileLayer(titleUrl, { attribution });
tiles.addTo(myMap);



// Leaflet.Terminator https://github.com/joergdietrich/Leaflet.Terminator
L.terminator().addTo(myMap);


/* Date.prototype.toLocaleDateString()
     https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString */
var timeOptions = { year: 'numeric', month: 'numeric', day: 'numeric' };
// timeOptions.timeZone = 'UTC';


/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* ************************************************************************************************ */
/*  Aircrafts live data */

/* 
This is the official documentation of the OpenSky Network’s live API. 
The API lets you retrieve live airspace information for research and non-commerical purposes. 
Documentation: https://opensky-network.org/apidoc/rest.html
 */

aircrafts_api_url = "/api/v1.0/aircrafts-data"
d3.json(aircrafts_api_url).then((importedData) => {
    // Store the imported data to a variable

    var flightData = importedData;

    // console.log(flightData);

    // Retrieve the newest meas time and convert the format
    var newestData = new Date(flightData[0].time * 1000);
    var newestDataTime = newestData.toLocaleTimeString("en-US", timeOptions);

    // Display on the screen the number of aircraft currently on the maps
    document.getElementById('numAircrafts').textContent = `${flightData.length} (${newestDataTime})`;

    // Display on the screen the number of cleaned data points 
    document.getElementById('totalAircraftDatabase').textContent = `${flightData[0].id}`;


    // add marker to map for each flight
    flightData.forEach(function (element) {
        L.circle([element.latitude, element.longitude], {
            fillOpacity: 0.75,
            color: "red",
            fillColor: "blue",
            // Adjust radius
            radius: 20000
        }).bindPopup(`<h5>Aircraft Info:</h5><hr>
        ICAO address: ${element["icao24"]}<br/>
        Callsign: <a href='https://flightaware.com/resources/registration/${element["callsign"]}' target="_blank">${element["callsign"]}</a><br/>
        Origin country: ${element["origin_country"]}<br/>
        Time of position update: ${element["time_position"]} (UTC)<br/>
        Time of last update: ${element["last_contact"]} (UTC)<br/>
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
  `, { "background": "#2c3e50" }).addTo(myMap);

    })


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
        }
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
        }
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
        height: 400,
        width: 600,
        showlegend: true,
        // grid: { rows: 1, columns: 1 }
    };

    Plotly.newPlot('positionSourcePlot', data, layout, config);


    // Aircraft Speed vs. Altitude Chart
    var trace3 = {
        x: flightData.map(element => element.baro_altitude * 3.28084),
        y: flightData.map(element => element.velocity * 2.23694),
        // text: flightData.map(element => element.callsign),
        text: flightData,
        hovertemplate: 'Callsign: %{text.callsign}<extra></extra>' +
            '<br>Vertical rate: %{text.vertical_rate}',
        mode: 'markers',
        type: 'scatter'
    };

    var data = [trace3];

    var layout = {
        title: "Aircraft Speed vs. Altitude",
        xaxis: {
            title: "Altitude (ft) "
        },
        yaxis: {
            title: "Speed (mph) ",
            automargin: true,
        }
    }

    Plotly.newPlot('scatterVelAltitude', data, layout, config);


});









/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* ************************************************************************************************ */
/* ************************************************************************************************ */

// API created for this project
airports_api_url = "/api/v1.0/airports-data"
d3.json(airports_api_url).then((importedData) => {
    // console.log(importedData);

    var airportData = importedData;

    airportData.forEach(function (element) {
        if (element.Country) {
            L.circle([element.Latitude, element.Longitude], {
                fillOpacity: 0.75,
                color: "green",
                fillColor: "black",
                // Adjust radius
                radius: 2000
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
            ).addTo(myMap);
        }
    });

    document.getElementById('totalNumAirports').textContent = `${airportData.length}`;

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

    // console.log(countryAirPorts);

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
        return d.country === 'Brazil';
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
        }
    }

    // Render the plot to the div tag id "plot"
    Plotly.newPlot("barChartAirports", chartData, layout, config);
});
