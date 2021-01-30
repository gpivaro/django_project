/* 
This is the official documentation of the OpenSky Network’s live API. 
The API lets you retrieve live airspace information for research and non-commerical purposes. 
Documentation: https://opensky-network.org/apidoc/rest.html
 */
url = "https://opensky-network.org/api/states/all";

// Data for the airport locations
airports_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

// To use OpenStreetMap instead of MapBox
var attribution =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';
var titleUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var streets = L.tileLayer(titleUrl, { attribution });

var Stadia_AlidadeSmooth = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', {
  maxZoom: 20,
  attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
});

// Leaflet.Terminator https://github.com/joergdietrich/Leaflet.Terminator
var dayNightLayer = L.terminator();


//   Markers With Custom Icons
var aircraftIcon = L.icon({
  iconUrl: 'static/images/Airplane_wwwroot_uploads_svg_symbol_0qvhey5-airplane-vector.svg',
  iconSize: [38 / 4, 95 / 4], // size of the icon
  // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
});

//   Markers With Custom Icons
var aircraftIcon0 = L.icon({
  iconUrl: 'static/images/aircraft_0deg.svg',
  iconSize: [38 / 4, 95 / 4], // size of the icon
  // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
});

//   Markers With Custom Icons
var aircraftIcon90 = L.icon({
  iconUrl: 'static/images/aircraft_90deg.svg',
  iconSize: [38 / 4, 95 / 4], // size of the icon
  // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
});

//   Markers With Custom Icons
var aircraftIcon180 = L.icon({
  iconUrl: 'static/images/aircraft_180deg.svg',
  iconSize: [38 / 4, 95 / 4], // size of the icon
  // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
});

//   Markers With Custom Icons
var aircraftIcon270 = L.icon({
  iconUrl: 'static/images/aircraft_270deg.svg',
  iconSize: [38 / 4, 95 / 4], // size of the icon
  // popupAnchor: [-3, -76] // point from which the popup should open relative to the iconAnchor
});


/* Date.prototype.toLocaleDateString()
     https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toLocaleDateString */
var options = { year: 'numeric', month: 'numeric', day: 'numeric' };
options.timeZone = 'UTC';

// Responsive chart and hide control buttons on Plotly charts
var config = {
  responsive: true,
  displayModeBar: true
};

// Initialize all of the LayerGroups we'll be using
var layers = {
  Aircrafts: new L.LayerGroup(),
  Airports: new L.LayerGroup(),
  DayNight: dayNightLayer,
};

var baseMaps = {
  "Gray": Stadia_AlidadeSmooth,
  "Streets": streets
};

// Creating our initial map object
// L.map accepts 2 arguments: id of the HTML element to insert the map, and an object containing the initial options for the new map
var myMap = L.map("map", {
  // For Houston uncomment:
  // center: [31.56, -96.47],
  center: [40.3, -99.14],
  zoom: 4,
  scrollWheelZoom: false, //Disable scroll wheel zoom on Leaflet
  layers: [
    layers.Aircrafts,
    layers.Airports,
    layers.DayNight
  ]
});

// Add our tile layer to the map
streets.addTo(myMap);

// Create an overlays object to add to the layer control
var overlays = {
  "Aircrafts": layers.Aircrafts,
  "Airports": layers.Airports,
  "Day/Night": layers.DayNight
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

// var icons = {
//   Aircrafts: L.ExtraMarkers.icon({
//     icon: "ion-settings",
//     iconColor: "white",
//     markerColor: "yellow",
//     shape: "star"
//   }),
//   Airports: L.ExtraMarkers.icon({
//     icon: "ion-android-bicycle",
//     iconColor: "white",
//     markerColor: "red",
//     shape: "circle"
//   })
// };






d3.json(url).then(function (data) {

  d3.csv("data/airports.csv").then(function (importedData) {
    // console.log(importedData);

    var airportData = importedData;
    // Cast the data value to a number for each piece of data
    airportData.forEach(function (d) {
      d["Airport ID"] = +d["Airport ID"];
      d["Altitude"] = +d["Altitude"];
      d["Latitude"] = +d["Latitude"];
      d["Longitude"] = +d["Longitude"];
    });

    // console.log(airportData);

    airportData.forEach(function (element) {
      if (element.Country === "United States") {
        var marker = L.circle([element.Latitude, element.Longitude], {
          // icon: icons['Airports'],
          // fillOpacity: 0.75,
          color: "green",
          // fillColor: "black",
          // Adjust radius
          radius: 2000
        }).bindPopup(`<h3>Airport ID: ${element["Airport ID"]}</h3><hr>
                    Airport ID: ${element["Airport ID"]}<br/>
                    Name: ${element["Name"]}<br/>
                    City: ${element["City"]}<br/>
                    Country: ${element["Country"]}<br/>
                    DST: ${element["DST"]}<br/>
                    IATA: ${element["IATA"]}<br/>
                    ICAO: ${element["ICAO"]}<br/>
                    Altitude: ${element["Altitude"]}<br/>
                    Latitude: ${element["Latitude"]}<br/>
                    Longitude: ${element["Longitude"]}<br/>
                    Source: ${element["Source"]}<br/>
                    Timezone: ${element["Timezone"]}<br/>
                    Type: ${element["Type"]}<br/>
                    Tz database time zone: ${element["Tz database time zone"]}<br/>`
        );
        marker.addTo(layers['Airports']);
      }
    });


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

    var currentCountryAirport = totalAirportsCountry.filter(filterCountry);
    // console.log(currentCountryAirport[0].airports);
    // Display on the screen the number of cleaned data points 
    document.getElementById('numAirports').textContent = `${currentCountryAirport[0].country}${currentCountryAirport[0].airports.toLocaleString()}`;


    // Sort the samples in descending order of sample values
    totalAirportsCountry.sort((a, b) => b.airports - a.airports);

    // Select the top origin country number of aircrafts
    top10CountryAirports = totalAirportsCountry.slice(0, 10);


    // Reverse the list due to the Plotly requeriments
    top10CountryAirports.reverse()

    // console.log(top10CountryAirports);

    // Trace1 to display the data
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


    // Responsive chart
    var config = {
      responsive: true,
      displayModeBar: false
    };

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
  // End of the nested function
  ///////////////////////////////////////////////////////////////////////////////////
  // Begin of the first d3.json
  // Store the imported data to a variable
  // console.log(data);

  // Create and object with the data organized by key value pair
  var flightData = [];
  for (var i = 0; i < data.states.length; i++) {
    // conditional test to get only fligths with available location and not on the ground
    if (data.states[i][5] && !data.states[i][8]) {
      var time_position = new Date(data.states[i][3] * 1000);
      var last_contact = new Date(data.states[i][4] * 1000);
      // conditional test to label the position source method
      if (data.states[i][16] === 0) {
        position_source = "ADS-B"
      }
      else if (data.states[i][16] === 1) {
        position_source = "ASTERIX"
      }
      else {
        position_source = "MLAT"
      }
      flightData.push({
        "icao24": data.states[i][0],
        "callsign": data.states[i][1],
        "origin_country": data.states[i][2],
        "time_position": time_position.toLocaleTimeString("en-US", options),
        "last_contact": last_contact.toLocaleTimeString("en-US", options),
        "longitude": data.states[i][5],
        "latitude": data.states[i][6],
        "baro_altitude": data.states[i][7],
        "on_ground": data.states[i][8],
        "velocity": data.states[i][9],
        "true_track": data.states[i][10],
        "vertical_rate": data.states[i][11],
        "sensors": data.states[i][12],
        "geo_altitude": data.states[i][13],
        "squawk": data.states[i][14],
        "spi": data.states[i][15],
        "position_source": position_source
      });
    }
  };

  var totalFlightMap = flightData.length;

  // Display on the screen the number of cleaned data points 
  document.getElementById('numAircrafts').textContent = totalFlightMap.toLocaleString();

  updateLegend(totalFlightMap);

  // add marker to map for each flight
  flightData.forEach(function (element) {
    var marker = L.marker([element.latitude, element.longitude], {
      // icon: icons['Aircraft']
      icon: aircraftIcon,
//       var element.true_track = if(element.true_track > 90 ){icon: aircraftIcon90},
      //       fillOpacity: 0.75,
      //       color: "red",
      //       fillColor: "blue",
      // Adjust radius
      //       radius: 20000
    }).bindPopup(`
    <h5>AirCraft Information</h5><hr>
    ICAO24 / Mode S Code (hex): <a href='https://opensky-network.org/aircraft-profile?icao24=${element["icao24"]}' target="_blank">${element["icao24"]}</a><br/>
    Callsign: ${element["callsign"]} <br/>
    Country: ${element["origin_country"]}<br/>
    Time of position update: ${element["time_position"]} (UTC)<br/>
    Time of last update: ${element["last_contact"]} (UTC)<br/>
    Longitude: ${element["longitude"]}<br/>
    Latitude: ${element["latitude"]}<br/>
    Altitude ${(element["baro_altitude"])} m | ${(Math.round(element["baro_altitude"] * 3.28084))} ft<br/>
    On ground: ${element["on_ground"]}<br/>
    Velocity: ${element["velocity"]} m/s | ${Math.round(element["velocity"] * 2.23694)} mph <br/>
    True track: ${element["true_track"]}° (north=0°)<br/>
    Vertical rate: ${element["vertical_rate"]} m/s<br/>
    Sensors ID: ${element["sensors"]}<br/>
    Geometric altitude: ${(element["geo_altitude"])} m | ${(Math.round(element["geo_altitude"] * 3.28084))} ft<br/>
    Transponder code: ${element["squawk"]}<br/>
    Special purpose indicator: ${element["spi"]}<br/>
    Position_source: ${element["position_source"]}<br/>
    For more details: <a href='https://flightaware.com/live/flight/${element["callsign"]}' target="_blank">link</a>
  `, { "background": "#2c3e50" }
    );
    marker.addTo(layers['Aircrafts']);
  }
  );


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

  // Trace1 to display the data
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
  

  var posSource = [];
  var ADSB = 0; var ASTERIX = 0; var MLAT = 0;
  for (var i = 0; i < flightData.length; i++) {
    // conditional test to get position source type
    if (flightData[i].position_source === "ADS-B") {
      ADSB += 1;
    }
    else if (flightData[i].position_source === "ASTERIX") {
      ASTERIX += 1;
    }
    else if (flightData[i].position_source === "MLAT") {
      MLAT += 1;
    }
  };
  posSource.push(
    { "Type": "ADS-B", "Qtd": ADSB },
    { "Type": "ASTERIX", "Qtd": ASTERIX },
    { "Type": "MLAT", "Qtd": MLAT });
  // console.log(posSource);


  // console.log(Object.entries(posSource));
  // console.log(Object.keys(posSource));

  var data = [{
    values: posSource.map(element => element.Qtd),
    labels: posSource.map(element => element.Type),
    // text: 'CO2',
    textposition: 'inside',
    domain: { column: 1 },
    // name: 'CO2 Emissions',
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



  var trace3 = {
    y: flightData.map(element => element.baro_altitude * 3.28084),
    x: flightData.map(element => element.velocity * 2.23694),
    // text: flightData.map(element => element.callsign),
    text: flightData,
    mode: 'markers',
    type: 'scatter',
    hovertemplate: "<b>Aircraft Info:</b><br><br>" + "ICAO24: %{text.icao24}<br>" + "Flight: %{text.callsign}<br>" +
      "Vertical rate: %{text.vertical_rate:,} m/s<br>" + "Altitude %{text.baro_altitude:,} m<br>"+ "Click on the dot for more info."
  };


  var data = [trace3];

  var layout = {
    title: "Aircraft Altitude vs. Speed",
    xaxis: {
      title: "Speed (mph)"
    },
    yaxis: {
      title: "Altitude (ft)",
      automargin: true,
    }
  }

  Plotly.newPlot('scatterVelAltitude', data, layout, config);
  
  scatterVelAltitude.on('plotly_click', function(e){
    console.log(e);
    var icaoNumber = e.points[0].text.icao24;
    console.log(icaoNumber)
    window.open(`https://opensky-network.org/aircraft-profile?icao24=${icaoNumber}`);
  });
  


});

// Update the legend's innerHTML with the last updated time and station count
function updateLegend(totalFlightMap) {
  d3.select(".legend").html(
    `<p class='out-of-order'>Airplanes: ${totalFlightMap.toLocaleString()}</p>`);
}
