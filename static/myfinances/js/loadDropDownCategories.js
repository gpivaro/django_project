
// Capture the event for the modal button
$(document).ready(function () {
    $('button[data-toggle="modal"]').on('click', function () {
        var buttonModalId = $(this).attr('id');
        //alert(buttonModalId);
        $('#' + buttonModalId).css({ "color": "red" });

        // Get the ID of the select
        var $dropdownID = '#Select_' + buttonModalId.split('_')[1];
        // alert($dropdownID);

        $('#currentCategory_' + buttonModalId.split('_')[1]).html('T');


        // Handler for the dropdown change for Callsign
        loadDropdown($dropdownID);

    });
});

// Capture the event for the select / dropdown menu
$(document).ready(function () {
    // select the selects with the target class and listen for the change
    $('select[class="noExport selDataset"]').on('change', function () {
        // Get the select that was changed
        var selectId = $(this).attr('id');
        $valueSelect = $('#' + selectId).val();
        // alert($valueSelect);
        $newCategory = selectId.split('_')[1] + '|' + $valueSelect;
        // alert($newCategory);

        // call the function that will change the category for the transaction
        changeCategory($newCategory);

    });
});


// Handler for the dropdown change for Callsign
d3.select('#BtnModal').on('click', function () {
    var dropdownID = '#dropDownCategories';
    loadDropdown(dropdownID);
});

/* function to access the api and get the json 
data to populate the dropdown menus */
function loadDropdown(dropdownID) {
    url_categories = '/myfinances/categories/'
    d3.json(url_categories).then((importData) => {
        createDropdownMenu(importData, dropdownID);
    });
};

// Create dropdown menu
function createDropdownMenu(importData, dropdownID) {
    var categoryArray = []
    importData.forEach(element => {
        categoryArray.push(element.Group)
    });
    // Remove duplicates by creating a set
    var uniqueCategories = [...new Set(categoryArray)];
    console.log(uniqueCategories);


    // jQuery to clear the dropdown menu before reload it
    $(dropdownID).children('option').remove();


    // Pass the category strings to load the dropdown
    selectOptionAddText(dropdownID, uniqueCategories);


}


/* Data binding with the enter function to populate 
    the dropdown menu with subject ids available */
function selectOptionAddText(domElement, enterData) {
    d3.select(domElement)
        .selectAll('option')
        .data(enterData)
        .enter()
        .append('option')
        .attr("value", function (data, index) {
            return data;
        })
        .text(function (data, index) {
            return data;
        });
}


