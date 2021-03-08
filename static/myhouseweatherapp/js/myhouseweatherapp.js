// Filter the data to load
lastHoursData = 24
// API weather data
url_api_data = `/homeweather/api/v1.0/weather-data/${lastHoursData}/`


d3.json('/analytics/show-visitors/homeweather').then((visitsData) => {
    console.log(visitsData.visits)
    document.getElementById('pageVisits').textContent = `${visitsData.visits}`;
});



function myFunction() {
    var x = parseInt(screen.availWidth);
    console.log(x)
    return x
}

if (myFunction() <= 414) {
    var heightSize = 270
} else {
    var heightSize = 450
}


// Responsive chart
var config = { responsive: true, displayModeBar: false }

d3.json(url_api_data).then((measData) => {
    // console.log(measData)

    // Separate data into two arrays one for each sensor
    var sensor13 = []
    var sensor16 = []
    measData.forEach(element => {
        if (element.sensor === 13) {
            sensor13.push(element)
        }
        else if (element.sensor === 16) {
            sensor16.push(element)
        }
    })



    // Line Chart

    // Trace1 to display the sensor 13 data
    var trace1 = {
        x: sensor13.map(element => element.meas_time),
        y: sensor13.map(element => (element.temperature * 9 / 5) + 32),
        mode: 'lines',
        name: 'Outdoor',
        line: {
            // dash: 'dashdot',
            color: 'rgb(255, 195, 0)',
            width: 3
        }
    };

    // Trace2 to display the sensor 13 data
    var trace2 = {
        x: sensor16.map(element => element.meas_time),
        y: sensor16.map(element => (element.temperature * 9 / 5) + 32),
        mode: 'lines',
        name: 'Indoor',
        line: {
            // dash: 'dot',
            color: 'rgb(144, 12, 63)',
            width: 3
        }
    };

    // create an array to be plotted
    var chartData = [trace1, trace2];



    var layout = {
        title: 'Temperature Over Time (24 h) ',
        yaxis: {
            // Degree symbol 'Option + Shift + 8'
            title: 'Temperature (°F)',
            range: [0, 120]
        },

        showlegend: true,
        legend: {
            xanchor: 'right',
            // y: 0.5,
            traceorder: 'reversed',
            font: { size: 16 },
            yref: 'paper'
        },
        margin: {
            l: 60,
            r: 60,
            b: 60,
            t: 60,
            pad: 4
        },
        font: {
            // family: 'Courier New, monospace',
            size: 16,
            color: '#000000'
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: 'rgba(0,0,0,0)',
        hovermode: false,
    };

    // Render the plot to the div tag id "plot"
    Plotly.newPlot("plotTemp", chartData, layout, config);


    //  Overlaid Histogram


    var trace1 = {
        x: sensor13.map(element => (element.temperature * 9 / 5) + 32),
        type: "histogram",
        opacity: 1,
        marker: {
            color: 'rgb(255, 195, 0)',
        },
        name: 'Outdoor',
    };
    var trace2 = {
        x: sensor16.map(element => (element.temperature * 9 / 5) + 32),
        type: "histogram",
        opacity: 1,
        marker: {
            color: 'rgb(144, 12, 63)',
        },
        name: 'Indoor',
    };

    var dataChart = [trace1, trace2];
    var layout = {
        barmode: "overlay",
        title: 'Temperature Distribution (24 h)',
        xaxis: {
            // Degree symbol 'Option + Shift + 8'
            title: 'Temperature (°F)',
            range: [0, 120]
        },
        yaxis: {
            // Degree symbol 'Option + Shift + 8'
            title: 'Data points',
        },
        legend: {
            xanchor: 'right',
            // y: 0.5,
            traceorder: 'reversed',
            font: { size: 16 },
            yref: 'paper'
        },
        margin: {
            l: 60,
            r: 60,
            b: 60,
            t: 60,
            pad: 4
        },
        font: {
            // family: 'Courier New, monospace',
            size: 16,
            color: '#000000'
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: 'rgba(0,0,0,0)',
        hovermode: false,
    };
    Plotly.newPlot('overlaidHistogram', dataChart, layout, config);


    // Angular Gauge Chart

    var colorPointer = [
        { '0 - 10': 'rgb(3, 2, 252)' },
        { '10 - 20': 'rgb(3, 2, 252)' },
        { '20 - 30': 'rgb(42, 0, 213)' },
        { '30 - 40': 'rgb(42, 0, 213)' },
        { '40 - 50': 'rgb(99, 0, 158)' },
        { '50 - 60': 'rgb(99, 0, 158)' },
        { '70 - 80': 'rgb(161, 1, 93)' },
        { '90 - 100': 'rgb(161, 1, 93)' },
        { '100 - 110': 'rgb(216, 0, 39)' },
        { '110 - 120': 'rgb(254, 0, 2)' }
    ]

    // Return one of the colors based on the temperature
    function colorPicker(data) {
        return Object.values(colorPointer[Math.floor(data / 10)])[0]
    }

    var data = [
        {
            domain: { x: [0, 1], y: [0, 1] },
            value: (sensor16[0].temperature * 9 / 5) + 32,
            number: { suffix: "°F" },
            title: { text: "Indoor Temperature<sup>2</sup>" },
            type: "indicator",
            mode: "gauge+number",
            delta: { reference: 100 },
            gauge: {
                axis: { range: [null, 120] }, bar: { color: colorPicker((sensor16[0].temperature * 9 / 5) + 32) },
            }
        }
    ];



    var layout = {
        height: heightSize,
        margin: {
            l: 50,
            r: 50,
            b: 50,
            t: 50,
            pad: 4
        },
        paper_bgcolor: "rgba(0,0,0,0)",
        font: {
            // family: 'Courier New, monospace',
            size: 18,
            color: '#000000'
        }
    };


    Plotly.newPlot('AngularGaugeChartIn', data, layout, config);

    var data = [
        {
            domain: { x: [0, 1], y: [0, 1] },
            value: (sensor13[0].temperature * 9 / 5) + 32,
            number: { suffix: "°F" },
            title: { text: "Outdoor Temperature<sup>1</sup>" },
            type: "indicator",
            mode: "gauge+number",
            delta: { reference: 80 },
            gauge: {
                axis: { range: [null, 120] }, bar: { color: colorPicker((sensor13[0].temperature * 9 / 5) + 32) }
            }
        }
    ];



    Plotly.newPlot('AngularGaugeChartOut', data, layout, config);
});






// Event listen to update page based on the dropdown selection
function updatePage() {

    var dropdown = d3.select('#selDataset');
    var dropdownValue = dropdown.property('value');
    console.log(dropdownValue);

    // Parse the dropdown values as integer
    var timeSpan = parseInt(dropdownValue);

    // Build the plot with the new stock
    buildPlot(timeSpan);
};

// Create the main function to get the data and generate the plots
function buildPlot(timeSpan) {
    // Use D3 fetch to read the JSON file
    d3.json(`/homeweather/api/v1.0/weather-data/${timeSpan}/`).then((measData) => {

        // Separate data into two arrays one for each sensor
        var sensor13 = []
        var sensor16 = []
        measData.forEach(element => {
            if (element.sensor === 13) {
                sensor13.push(element)
            }
            else {
                sensor16.push(element)
            }
        })



        // Line Chart

        // Trace1 to display the sensor 13 data
        var trace1 = {
            x: sensor13.map(element => element.meas_time),
            y: sensor13.map(element => (element.temperature * 9 / 5) + 32),
            mode: 'lines',
            name: 'Outdoor',
            line: {
                // dash: 'dashdot',
                color: 'rgb(255, 195, 0)',
                width: 3
            }
        };

        // Trace2 to display the sensor 13 data
        var trace2 = {
            x: sensor16.map(element => element.meas_time),
            y: sensor16.map(element => (element.temperature * 9 / 5) + 32),
            mode: 'lines',
            name: 'Indoor',
            line: {
                // dash: 'dot',
                color: 'rgb(144, 12, 63)',
                width: 3
            }
        };

        // create an array to be plotted
        var chartData = [trace1, trace2];



        var layout = {
            title: `Temperature Over Time (${timeSpan} h) `,
            yaxis: {
                // Degree symbol 'Option + Shift + 8'
                title: 'Temperature (°F)',
                range: [0, 120]
            },

            showlegend: true,
            legend: {
                xanchor: 'right',
                // y: 0.5,
                traceorder: 'reversed',
                font: { size: 16 },
                yref: 'paper'
            },
            margin: {
                l: 60,
                r: 60,
                b: 60,
                t: 60,
                pad: 4
            },
            font: {
                // family: 'Courier New, monospace',
                size: 16,
                color: '#000000'
            },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: 'rgba(0,0,0,0)',
            hovermode: false,
        };

        // Render the plot to the div tag id "plot"
        Plotly.newPlot("plotTemp", chartData, layout, config);


        //  Overlaid Histogram


        var trace1 = {
            x: sensor13.map(element => (element.temperature * 9 / 5) + 32),
            type: "histogram",
            opacity: 1,
            marker: {
                color: 'rgb(255, 195, 0)',
            },
            name: 'Outdoor',
        };
        var trace2 = {
            x: sensor16.map(element => (element.temperature * 9 / 5) + 32),
            type: "histogram",
            opacity: 1,
            marker: {
                color: 'rgb(144, 12, 63)',
            },
            name: 'Indoor',
        };

        var dataChart = [trace1, trace2];
        var layout = {
            barmode: "overlay",
            title: `Temperature Distribution (${timeSpan} h)`,
            xaxis: {
                // Degree symbol 'Option + Shift + 8'
                title: 'Temperature (°F)',
                range: [0, 120]
            },
            yaxis: {
                // Degree symbol 'Option + Shift + 8'
                title: 'Data points',
            },
            legend: {
                xanchor: 'right',
                // y: 0.5,
                traceorder: 'reversed',
                font: { size: 16 },
                yref: 'paper'
            },
            margin: {
                l: 60,
                r: 60,
                b: 60,
                t: 60,
                pad: 4
            },
            font: {
                // family: 'Courier New, monospace',
                size: 16,
                color: '#000000'
            },
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: 'rgba(0,0,0,0)',
            hovermode: false,
        };
        Plotly.newPlot('overlaidHistogram', dataChart, layout, config);

    })
}


// Handler for the dropdown change
d3.select('#selDataset').on('change', updatePage);