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




// tr {
//     overflow: hidden;
//     height: 14px;
//     white-space: nowrap;
//   }