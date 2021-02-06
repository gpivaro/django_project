// Filter the data to load
lastHoursData = 24
// API weather data
url_api_data = `/myhouseweather/api/v1.0/weather-data/${lastHoursData}/`


d3.json(url_api_data).then((measData) => {
    // console.log(measData)

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
        y: sensor13.map(element => element.temperature),
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

    // Responsive chart
    var config = { responsive: true }

    var layout = {
        title: 'Temperature over Time',
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
        }
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
        title: 'Temperature Distribution',
        xaxis: {
            // Degree symbol 'Option + Shift + 8'
            title: 'Temperature (°F)',
            range: [0, 120]
        },
        legend: {
            xanchor: 'right',
            // y: 0.5,
            traceorder: 'reversed',
            font: { size: 16 },
            yref: 'paper'
        }
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
            title: { text: "Indoor Temperature" },
            type: "indicator",
            mode: "gauge+number",
            delta: { reference: 100 },
            gauge: {
                axis: { range: [null, 120] }, bar: { color: colorPicker((sensor16[0].temperature * 9 / 5) + 32) },
            }
        }
    ];


    var layout = { width: 600, height: 400 };
    Plotly.newPlot('AngularGaugeChartIn', data, layout);

    var data = [
        {
            domain: { x: [0, 1], y: [0, 1] },
            value: (sensor13[0].temperature * 9 / 5) + 32,
            number: { suffix: "°F" },
            title: { text: "Outdoor Temperature" },
            type: "indicator",
            mode: "gauge+number",
            delta: { reference: 100 },
            gauge: {
                axis: { range: [null, 120] }, bar: { color: colorPicker((sensor13[0].temperature * 9 / 5) + 32) }
            }
        }
    ];


    var layout = { width: 600, height: 400 };
    Plotly.newPlot('AngularGaugeChartOut', data, layout);
});

