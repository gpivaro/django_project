//Source: https://www.w3schools.com/howto/howto_js_filter_table.asp
// Changed the code to look for the table id that contains the string to be found
function filterTable() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("tblData");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    var totalRowValues = 0;
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[4];
        if (td) {
            txtValue = td.textContent || td.innerText;
            // txtValue = td.id;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
                // Get the values of the column 3 to calculate the total row
                totalRowValues = totalRowValues + parseFloat(tr[i].getElementsByTagName("td")[3].innerText)

            } else {
                tr[i].style.display = "none";
            }
        }
    }

    // Call the funtion to calculate the total row value
    totalRowCalc(totalRowValues);

}

function filterDescription() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("descriptionInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("tblData");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    var totalRowValues = 0;
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[2]; //Select the td index
        if (td) {
            txtValue = td.textContent || td.innerText;
            // txtValue = td.id;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
                // Get the values of the column 3 to calculate the total row
                totalRowValues = totalRowValues + parseFloat(tr[i].getElementsByTagName("td")[3].innerText)

            } else {
                tr[i].style.display = "none";
            }
        }
    }

    // Call the funtion to calculate the total row value
    totalRowCalc(totalRowValues);

}