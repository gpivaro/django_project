function addZero(i) {
    if (i < 10) {
        i = "0" + i;
    }
    return i;
}


// Plot closing prices using AJAX
$(document).ready(function () {


    // Set the request to the backend using Ajax and GET request
    req = $.ajax({
        url: '/homeweather/api/v1.0/weather-data/1/',
        type: 'GET',

        success: function (weatherData) {
            console.log(weatherData);

            // call function to generate plot
            generatePlotlyPlot(weatherData)
        },
        error: function (error) {
            console.log(error);
        }
    });

});


function generatePlotlyPlot(weatherData) {

    // Sort the samples in descending order of meas_time
    weatherData.sort((a, b) => b.meas_time - a.meas_time);

    var sensor4 = []; var sensor13 = []; var sensor16 = []; var sensor26 = [];
    weatherData.forEach(element => {
        if (element.sensor === 4) {
            sensor4.push(element);
        }
        else if (element.sensor === 13) {
            sensor13.push(element);
        }
        else if (element.sensor === 16) {
            sensor16.push(element);
        }
        else if (element.sensor === 26) {
            sensor26.push(element);
        }
    });
    console.log(sensor4);



    var trace1 = {
        x: sensor4.map(element => {
            var myDate = new Date(element.meas_time);
            var newDate = `${addZero(myDate.getHours() + 6)}:${addZero(myDate.getMinutes())}`;
            return newDate
        }),
        y: sensor4.map(element => element.temperature),
        type: 'scatter',
        name: sensor4[0].sensor_name
    };

    var trace2 = {
        x: sensor13.map(element => {
            var myDate = new Date(element.meas_time);
            var newDate = `${addZero(myDate.getHours() + 6)}:${addZero(myDate.getMinutes())}`;
            return newDate
        }),
        y: sensor13.map(element => element.temperature),
        type: 'scatter',
        name: sensor13[0].sensor_name
    };

    var trace3 = {
        x: sensor16.map(element => {
            var myDate = new Date(element.meas_time);
            var newDate = `${addZero(myDate.getHours() + 6)}:${addZero(myDate.getMinutes())}`;
            return newDate
        }),
        y: sensor16.map(element => element.temperature),
        type: 'scatter',
        name: sensor16[0].sensor_name
    };

    var trace4 = {
        x: sensor26.map(element => {
            var myDate = new Date(element.meas_time);
            var newDate = `${addZero(myDate.getHours() + 6)}:${addZero(myDate.getMinutes())}`;
            return newDate
        }),
        y: sensor26.map(element => element.temperature),
        type: 'scatter',
        name: sensor26[0].sensor_name
    };


    var dataPlot = [trace1, trace2, trace3, trace4];

    var layout = {
        title: 'Temperature',
        xaxis: {
            title: 'Time',
            showgrid: false,
            zeroline: false,
            autorange: 'reversed',
            tickformat: '%H:%M'
        },
        yaxis: {
            title: 'Temperature (°C)',
            showline: false
        },
        margin: {
            l: 60,
            r: 60,
            b: 160,
            t: 60,
            pad: 4
        }
    };

    // Responsive chart
    var config = { responsive: true, displayModeBar: false }

    Plotly.newPlot('linePlot', dataPlot, layout, config);
};