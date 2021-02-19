function totalRowCalc(total) {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("tblTotal");
    tr = table.getElementsByTagName("tr");


    document.getElementById("tblTotal").deleteRow(tr.length - 1);

    // Create an empty <tr> element and add it to the 1st position of the table:
    var row = table.insertRow(tr.length);

    // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    // var cell3 = row.insertCell(2);
    // var cell4 = row.insertCell(3);
    // var cell5 = row.insertCell(4);
    // var cell6 = row.insertCell(5);

    // Add some text to the new cells:
    // cell1.innerHTML = "---";
    // cell2.innerHTML = "---";
    cell1.innerHTML = "<strong>TOTALS</strong>";
    cell2.innerHTML = `<strong>$${(Math.round(100 * total) / 100).toLocaleString()}</strong>`;
    // cell5.innerHTML = "---";
    // cell6.innerHTML = "---";


}

function myDeleteFunction() {
    document.getElementById("myTable").deleteRow(0);
}
