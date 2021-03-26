// This functions changes the values of the td based on the dropdown values selected
// function changeCategory(val) {
//     console.log(val);
//     newValue = val.split("|")[1];
//     var trIndex = parseInt(val);
//     table = document.getElementById("tblData");
//     tr = table.getElementsByTagName("tr");
//     td = tr[trIndex].getElementsByTagName("td")[4]
//     td.innerHTML = newValue;
// };

function changeCategory(val) {
    console.log(val);
    newValue = val.split("|")[1];

    // console.log(btnNumber.split("_")[1]);
    // var trIndex = parseInt(btnNumber.split("_")[1]);
    var trIndex = parseInt(val);
    table = document.getElementById("tblData");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and find the tr id to change
    for (i = 0; i < tr.length; i++) {
        if (tr[i].id == `${trIndex}`) {
            td = tr[i].getElementsByTagName("td")[4]
            td.innerHTML = newValue;
        }

    }

    // Update modal current category
    updateModalCurrentCategory(trIndex);

    // Call the function to calculate the table totals
    calculateTable();

    // Call the function to filter and recalculate
    filterTable();
};