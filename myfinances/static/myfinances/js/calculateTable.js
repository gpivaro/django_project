var config = { responsive: true, displayModeBar: false }

//Source: https://www.w3schools.com/howto/howto_js_filter_table.asp
// Changed the code to look for the table id that contains the string to be found
function calculateTable() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("tblData");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    var categoriesArray = []; var totalCategoriesArray = []; var expensesArray = [];
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[4];
        if (td) {
            txtValue = td.textContent || td.innerText;
            expensesArray.push({ "date": (tr[i].getElementsByTagName("td")[0].innerText), "amount": parseFloat(tr[i].getElementsByTagName("td")[3].innerText) });
            if (categoriesArray.includes(txtValue)) {
                // categoriesArray.push[txtValue];
                var jj = 0;
                while (totalCategoriesArray[jj].category !== txtValue) {
                    jj++;
                }
                totalCategoriesArray[jj].amount = Math.round(1000 * (totalCategoriesArray[jj].amount + parseFloat(tr[i].getElementsByTagName("td")[3].innerText))) / 1000
            } else {
                categoriesArray.push(txtValue);
                totalCategoriesArray.push({ "category": txtValue, "amount": parseFloat(tr[i].getElementsByTagName("td")[3].innerText) });
            }

        }
    };

    // Generate plot
    generatePlot(totalCategoriesArray, expensesArray);


}



function generatePlot(dataIn, expensesArray) {

    // Sort the samples in descending order of amount
    dataIn.sort((a, b) => b.amount - a.amount);
    console.log(Object.values(dataIn));


    var inValues = []
    var totalIn = 0;
    dataIn.forEach(element => {
        if (element.amount >= 0) {
            inValues.push(element);
            totalIn = totalIn + element.amount;
        }
    });

    var outValues = []
    var totalOut = 0;
    dataIn.forEach(element => {
        if (element.amount < 0) {
            outValues.push(element);
            totalOut = totalOut + -1 * element.amount;
        }
    });

    // Total in and Out
    var InTotal = [{ "category": "Deposits", "amount": Math.round(totalIn) }];
    var OutTotal = [{ "category": "Withdrawals", "amount": Math.round(totalOut) }];



    // Plot
    var dataBarPlotOut = [
        {
            y: outValues.map(element => element.category),
            x: outValues.map(element => -1 * element.amount),
            type: 'bar',
            orientation: 'h',
            number: { prefix: "$" },
            hovertemplate: 'Total: %{x:$,2f}<extra></extra>',
            marker: {
                color: 'red', opacity: .6
            }
        },
    ];


    var layout = {
        title: 'Expenses by Category',
        xaxis: {
            title: "Amount ($)",
            automargin: true,
        },
        // autosize: true,
        // width: 500,
        // height: 500,
        margin: {
            l: 220,
            r: 20,
            b: 20,
            t: 40,
            pad: 4
        },
        hoverlabel: { bgcolor: "#FFF" },
    };



    Plotly.newPlot('barChartOut', dataBarPlotOut, layout, config);

    // To retrieve the first 10 items
    var top10SelSamples = outValues;
    // Reverse the list due to the Plotly requeriments
    top10SelSamples.reverse()

    top10SelSamples = top10SelSamples.slice(0, 10)

    var ultimateColors = [
        ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600'],
    ];

    var data = [{
        type: "pie",
        hole: .4,
        values: top10SelSamples.map(element => -1 * element.amount),
        labels: top10SelSamples.map(element => element.category),
        textinfo: "label+percent",
        textposition: "outside",
        automargin: true,
        marker: {
            colors: ultimateColors[0]
        },
        // text: $top10SelSamples.map(element => -1 * element.amount)
    }];

    // data.hoverinfo = 'text';

    var layout = {
        title: "Proportion of Expenses by Category",
        // height: 400,
        // width: 400,
        margin: {
            l: 10,
            r: 10,
            b: 10,
            t: 40,
            pad: 2
        },
        showlegend: false,
        annotations: [
            {
                font: {
                    size: 20
                },
                showarrow: false,
                text: 'Top 10',
                x: 0.5,
                y: 0.5
            }
        ],
    }

    Plotly.newPlot('pieChartOut', data, layout, config)


    // Plot
    var dataBarPlotOut = [
        {
            y: InTotal.map(element => element.category),
            x: InTotal.map(element => element.amount),
            type: 'bar',
            orientation: 'h',
            number: { prefix: "$" },
            hovertemplate: 'Total: %{x:$,2f}<extra></extra>',
            marker: {
                color: 'blue', opacity: .6
            },
            name: 'Deposits'
        },
        {
            y: OutTotal.map(element => element.category),
            x: OutTotal.map(element => element.amount),
            type: 'bar',
            orientation: 'h',
            number: { prefix: "$" },
            hovertemplate: 'Total: %{x:$,2f}<extra></extra>',
            marker: {
                color: 'red', opacity: .6
            },
            name: 'Withdrawals'
        }
    ];


    var layout = {
        title: 'Total Deposits and Withdrawals',
        xaxis: {
            title: "Amount ($)",
            automargin: true,
        },
        showlegend: false,
        // autosize: true,
        // width: 500,
        height: 200,
        margin: {
            l: 100,
            r: 20,
            b: 30,
            t: 40,
            pad: 4
        },
        hoverlabel: { bgcolor: "#FFF" }
        // hovermode: false,

    };



    Plotly.newPlot('barChartOutvsIn', dataBarPlotOut, layout, config);


    var expensesDateOut = [];
    expensesArray.forEach(element => {
        if (element.amount < 0) {
            expensesDateOut.push(element);
        }
    });

    // console.log((new Date(Date.parse(expensesDateOut[1].date))).getDay());

    var trace1 = {
        x: expensesDateOut.map(element => (new Date(Date.parse(element.date)))),
        y: expensesDateOut.map(element => -1 * element.amount),
        mode: 'markers',
        type: 'scatter',
        marker: {
            color: 'red', opacity: .6
        },
    };

    var layout = {
        title: 'Expenses Distribution by Date',
        yaxis: {
            title: "Amount ($)",
            // automargin: true,
        },
        showlegend: false,
        // autosize: true,
        // width: 500,
        height: 200,
        margin: {
            l: 100,
            r: 60,
            b: 60,
            t: 40,
            pad: 4
        },
        hoverlabel: { bgcolor: "#FFF" }
        // hovermode: false,

    };

    var data = [trace1];

    Plotly.newPlot('scatterExpenseDay', data, layout, config);





    // Create a object list with the target data columns
    var cleanData = [];
    for (var i = 0; i < outValues.length; i++) {
        cleanData.push({
            "category": outValues[i].category,
            "amount": -1 * outValues[i].amount
        });
    };

    console.log(cleanData);

    // Insert a table
    d3.select("#categoryTable")
        .select("table")
        // .append("thead")
        // .selectAll("tr")
        // .append("tr")
        .html(`<th class="alert-dark text-uppercase" style="padding:0px; margin:0px;" onclick="sortTable(0, \'tableCategoryExpenses\')">Category &nbsp;<i class="fa fa-fw fa-sort"></i></th> 
                <th class="alert-dark text-uppercase" style="padding:0px; margin:0px;" onclick="sortTableNumeric(1,\'tableCategoryExpenses\')">Amount ($) &nbsp;<i class="fa fa-fw fa-sort"></i></th>`)
        .append("tbody")
        .selectAll("tr")
        .data(cleanData)
        .enter()
        .append("tr")
        .style('height', '2px')
        // .append("hr")
        // .html('<hr style="padding:0px; margin:0px;">')
        .html(function (d) {
            return `<td style="padding:0px; margin:0px;">${d["category"]}</td>
            <td style="padding:0px; margin:0px; padding-right:6px">${d["amount"]}</td>`;
        })
        .style('height', '2px')
        .style('font-size', '10pt')
        .style('padding', '0px')
        .style('margin', '0px');

    document.getElementById('tableTitle').textContent = "Total Expenses by Category";

    console.log('calculate table task done.');

    $(document).ready(function () {
        $(".modal fade").hide();
        console.log('Modal closed');
    })


}

// tr {
//     overflow: hidden;
//     height: 14px;
//     white-space: nowrap;
//   }