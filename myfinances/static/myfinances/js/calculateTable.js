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
    var categoriesArray = []
    var totalCategoriesArray = []
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[4];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (categoriesArray.includes(txtValue)) {
                // categoriesArray.push[txtValue];
                var jj = 0;
                while (totalCategoriesArray[jj].category !== txtValue) {
                    jj++;
                }
                totalCategoriesArray[jj].amount = Math.round(100 * (totalCategoriesArray[jj].amount + parseFloat(tr[i].getElementsByTagName("td")[3].innerText))) / 100
            } else {
                categoriesArray.push(txtValue);
                totalCategoriesArray.push({ "category": txtValue, "amount": parseFloat(tr[i].getElementsByTagName("td")[3].innerText) });
            }

        }
    };

    // Generate plot
    generatePlot(totalCategoriesArray);


}



function generatePlot(dataIn) {

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

    console.log(OutTotal);


    // Plot
    var dataBarPlotOut = [
        {
            y: outValues.map(element => element.category),
            x: outValues.map(element => element.amount),
            type: 'bar',
            orientation: 'h',
            number: { prefix: "$" },
            hovertemplate: 'Total: %{x:$.2f}<extra></extra>'
        }
    ];


    var layout = {
        title: 'Expenses by Category',
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
    };



    Plotly.newPlot('barChartOut', dataBarPlotOut, layout, config);

    // To retrieve the first 10 items
    var top10SelSamples = outValues;
    // Reverse the list due to the Plotly requeriments
    top10SelSamples.reverse()

    top10SelSamples = top10SelSamples.slice(0, 10)


    var data = [{
        type: "pie",
        values: top10SelSamples.map(element => -1 * element.amount),
        labels: top10SelSamples.map(element => element.category),
        textinfo: "label+percent",
        textposition: "outside",
        automargin: true,
    }]

    var layout = {
        title: "Top 10 Category Expenses",
        // height: 400,
        // width: 400,
        margin: {
            l: 10,
            r: 10,
            b: 10,
            t: 40,
            pad: 2
        },
        showlegend: false
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
                color: 'blue'
            },
            name: 'Withdrawals'
        },
        {
            y: OutTotal.map(element => element.category),
            x: OutTotal.map(element => element.amount),
            type: 'bar',
            orientation: 'h',
            number: { prefix: "$" },
            hovertemplate: 'Total: %{x:$,2f}<extra></extra>',
            marker: {
                color: 'red'
            },
            name: 'Deposits'
        }
    ];


    var layout = {
        title: 'Total Deposits and Withdrawals',
        showlegend: false,
        // autosize: true,
        // width: 500,
        height: 200,
        margin: {
            l: 110,
            r: 20,
            b: 20,
            t: 40,
            pad: 4
        },
        // hovermode: false,

    };



    Plotly.newPlot('barChartOutvsIn', dataBarPlotOut, layout, config);




}