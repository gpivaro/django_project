// Responsive chart and hide control buttons on Plotly charts
var config = {
    responsive: true,
    displayModeBar: false
};


// Define variables for our tile layers
var attribution =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
var titleUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var OpenStreetTiles = L.tileLayer(titleUrl, { attribution });

// // Define streetmap layer
// var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
//     attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
//     maxZoom: 18,
//     id: "streets-v11",
//     accessToken: os.environ['API_KEY']
// });

// // Define darkmap layer
// var darkmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
//     attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
//     maxZoom: 18,
//     id: "dark-v10",
//     accessToken: os.environ['API_KEY']
// });

// // Define lightmap layer
// var lightmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
//     attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
//     maxZoom: 18,
//     id: "light-v10",
//     accessToken: os.environ['API_KEY']
// });

// // Define satellite layer
// var satellite = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
//     attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
//     maxZoom: 18,
//     id: "satellite-v9",
//     accessToken: os.environ['API_KEY']
// });

// Define a baseMaps object to hold our base layers
var baseMaps = {
    // "Streets": streetmap,
    // "Dark": darkmap,
    // "Grayscale": lightmap,
    // "Satellite": satellite,
    "OpenStreet": OpenStreetTiles
};



/* Date.prototype.toLocaleDateString()
     https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString */
var timeOptions = { year: 'numeric', month: 'numeric', day: 'numeric' };
// timeOptions.timeZone = 'UTC';

//   Markers With Custom Icons
var aircraftIcon = L.icon({
    iconUrl: '/static/images/Airplane_wwwroot_uploads_svg_symbol_0qvhey5-airplane-vector.svg',
    iconSize: [38 / 5, 95 / 5], // size of the icon
    // iconAnchor: [22, 94], // point of the icon which will correspond to marker's location
    // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
});


/* 
This is the official documentation of the OpenSky Network’s live API. 
The API lets you retrieve live airspace information for research and non-commerical purposes. 
Documentation: https://opensky-network.org/apidoc/rest.html
 */

//  API endpoints created for this project
aircrafts_api_url = "/api/v1.0/aircrafts-data"
airports_api_url = "/api/v1.0/airports-data"

// Chain the promises
d3.json(aircrafts_api_url).then((aircraftsData) => {
    return aircraftsData
}).then(
    function (aircraftsData) {
        d3.json(airports_api_url).then((importedData) => {

            // data from the first d3.json about the aircrafts
            var flightData = aircraftsData;

            // data from the second d3.json about the airports
            var airportData = importedData;

            // Retrieve the newest meas time and convert the format
            var newestData = new Date(flightData[0].time * 1000);
            var newestDataTime = newestData.toLocaleTimeString("en-US", timeOptions);

            // Display on the screen the number of cleaned data points 
            var totalFlightMap = flightData.length;
            document.getElementById('numAircrafts').textContent = `${totalFlightMap.toLocaleString()} (${newestDataTime})`;

            // Display on the screen the number of cleaned data points 
            document.getElementById('totalAircraftDatabase').textContent = `${flightData[0].id.toLocaleString()}`;

            // Display on the screen the number of airports
            document.getElementById('totalNumAirports').textContent = `${airportData.length.toLocaleString()}`;

            // add marker to map for each flight
            aircrafts = []
            flightData.forEach(function (element) {
                circles = L.marker([element.latitude, element.longitude], {
                    icon: aircraftIcon,
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
                    `, { "background": "#2c3e50" })

                aircrafts.push(circles);

            });

            // add marker for the airports
            airportArray = [];
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
                    airportArray.push(circles);
                }
            });


            // create a layerGroup for each aircraft markers.
            // Now we can handle them as one group instead of referencing each individually.
            var airportLayer = L.layerGroup(airportArray);
            // create a layerGroup for each airport markers.
            var aircraftsLayer = L.layerGroup(aircrafts);

            // Leaflet.Terminator https://github.com/joergdietrich/Leaflet.Terminator
            var dayNigthRegions = L.terminator();

            // Create overlay object to hold our overlay layer	
            var overlayMaps = {
                "Day/Nigth": dayNigthRegions,
                "Airports": airportLayer,
                "Aircrafts": aircraftsLayer
            };

            // Create our map, giving it the streetmap and earthquakes layers to display on load
            var myMap = L.map("map", {
                // center: [39, -99],
                // zoom: 4,
                center: [16, 0],
                zoom: 2,
                layers: [OpenStreetTiles, airportLayer, aircraftsLayer],
                scrollWheelZoom: false //Disable scroll wheel zoom on Leaflet
            });

            // Create a layer control
            // Pass in our baseMaps and overlayMaps
            // Add the layer control to the map
            L.control.layers(baseMaps, overlayMaps, {
                collapsed: false
            }).addTo(myMap);


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
    }
);


// Add ChartJS to handle the query data
url_aircrafts_hour = "/api/v1.0/aircrafts-data/byhour"
d3.json(url_aircrafts_hour).then((queryData) => {
    // console.log(queryData);

    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: queryData.map(element => element.timeData),
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
})
