

// Use AJAX to get the access data from API
$(document).ready(function () {

    // Set the request to the backend using Ajax and PUT method
    req = $.ajax({
        url: '/analytics/show-visitors/all/',
        type: 'GET',
        success: function (data) {
            // console.log(data);

            // generate stats about the access
            accessStats(data);

        },
        error: function (error) {
            console.log(error);
        }
    });

});


function accessStats(data) {

    // generate the map once the page loads
    generateMap(data);

    // bar chart
    barChart(data, "barChart");

    // bubble chart
    bubleChart(data, "scatterChart");

    accessByURI(data)

}




// Generate Leaflet map showing the access location
function generateMap(data) {

    // Layer Groups for access
    var dataPoints = []
    var dataHeatPoints = []
    data.forEach(element => {
        dataPoints.push(
            L.circle([element.latitude, element.longitude]
                , {
                    color: 'red',
                    fillColor: '#f03',
                    fillOpacity: 0.5,
                    radius: 500
                }
            )
                .bindPopup(`<p>Click for <a href="/analytics/access-detail/${element.id}/" target=_blank>details</a></p>`));

        dataHeatPoints.push([element.latitude, element.longitude]);
    });
    var dataPointsLayer = L.layerGroup(dataPoints);


    // https://github.com/Leaflet/Leaflet.heat
    var heat = L.heatLayer(dataHeatPoints,
        {
            radius: 15,
            blur: 5
        });


    // Map tile
    var streets = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    // Layers Control
    var map = L.map('statsMap', {
        center: [25, 25],
        zoom: 2,
        layers: [streets, dataPointsLayer, heat]
    });


    var baseMaps = {
        "Streets": streets
    };

    var overlayMaps = {
        "Visitors location": dataPointsLayer,
        "Visits heatmap": heat
    };


    L.control.layers(baseMaps, overlayMaps).addTo(map);

    var baseMaps = {
        "<span style='color: gray'>Streets</span>": streets
    };


};








// Generate a plotly bubble chart
function barChart(data, divName) {

    // console.log(data);
    var countryArray = []
    var countryCountArray = []
    data.forEach(element => {
        if (countryArray.includes(element.country)) {
            var index = countryArray.indexOf(element.country);
            countryCountArray[index] = countryCountArray[index] + 1
        } else {
            countryArray.push(element.country);
            countryCountArray.push(1);

        };
    });

    var countryObject = []
    var i;
    for (i = 0; i < countryArray.length; i++) {
        countryObject.push({ "country": countryArray[i], "visits": countryCountArray[i] });
    }
    // console.log(countryObject);

    // Sort the samples in descending order of sample values
    countryObject.sort((a, b) => b.visits - a.visits);

    // Select the top origin country number of aircrafts
    top10countryObject = countryObject.slice(0, 10);
    // top10countryObject = countryObject;


    // console.log(top10countryObject);
    // var uniqueCountryArray = [...new Set(countryArray)];
    // console.log(uniqueCountryArray);

    // Reverse the list due to the Plotly requeriments
    top10countryObject.reverse()


    // Trace1 to display the Aircraft by Country of Origin chart
    var trace1 = {
        x: top10countryObject.map(element => element.visits),
        y: top10countryObject.map(element => element.country),
        orientation: "h",
        type: "bar"
    };

    // create an array to be plotted
    var chartData = [trace1];

    var layout = {
        title: "Accesses by Country of Origin",
        xaxis: {
            title: "Number of accesses"
        },
        yaxis: {
            automargin: true,
        },
        // plot_bgcolor: "black",
        // paper_bgcolor: "slategrey"
    }

    // Responsive chart and no display mode bar
    var config = { responsive: true, displayModeBar: false }

    // Render the plot to the div tag id "plot"
    Plotly.newPlot(divName, chartData, layout, config);

}


// Generate a plotly bubble chart
function bubleChart(data, divName) {

    // get number of access by date
    var accessDate = accessByDate(data);

    var trace1 = {
        x: accessDate.map(element => element.Date),
        y: accessDate.map(element => element.Visits),
        type: 'bar',
        // marker: {
        //     size: [40, 60, 80, 100]
        // }
    };

    var dataPlot = [trace1];

    var layout = {
        title: 'Accesses by Date',
        showlegend: false,
        // height: 600,
        // width: 600
        xaxis: {
            title: "Date"
        },
        yaxis: {
            automargin: true,
            title: "Number of accesses"
        },
    };

    // Responsive chart and no display mode bar
    var config = { responsive: true, displayModeBar: false }


    Plotly.newPlot(divName, dataPlot, layout, config);
}


// function to group and count an array of elements
function accessByDate(data) {

    // loop over the array and get a single occurrency and count it
    var dataArray = []
    var dataCountArray = []
    data.forEach(element => {
        var currentElement = element.timestamp.split('T')[0]
        if (dataArray.includes(currentElement)) {
            var index = dataArray.indexOf(currentElement);
            dataCountArray[index] = dataCountArray[index] + 1
        } else {
            dataArray.push(currentElement);
            dataCountArray.push(1);

        };
    });

    // Create an object with the key and number of occurrencies
    var dataObject = []
    var i;
    for (i = 0; i < dataArray.length; i++) {
        dataObject.push({ "Date": dataArray[i], "Visits": dataCountArray[i] });
    }


    return dataObject;

}

// function to group and count an array of elements
function accessByURI(data) {

    // loop over the array and get a single occurrency and count it
    var dataArray = []
    var dataCountArray = []
    data.forEach(element => {
        var currentElement = element.absolute_uri
        if (dataArray.includes(currentElement)) {
            var index = dataArray.indexOf(currentElement);
            dataCountArray[index] = dataCountArray[index] + 1
        } else {
            dataArray.push(currentElement);
            dataCountArray.push(1);

        };
    });

    // Create an object with the key and number of occurrencies
    var dataObject = []
    var i;
    for (i = 0; i < dataArray.length; i++) {
        dataObject.push({ "URI": dataArray[i], "Visits": dataCountArray[i] });
    }

    // Sort the samples in descending order of sample values
    dataObject.sort((a, b) => b.Visits - a.Visits);


    console.log(dataObject);

    return dataObject;

}