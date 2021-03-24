
// Handler for the dropdown change for Callsign
d3.select('#BtnModal').on('click', loadDropdown);

/* function to access the api and get the json 
data to populate the dropdown menus */
function loadDropdown() {
    url_categories = '/myfinances/categories/'
    d3.json(url_categories).then((importData) => {
        createDropdownMenu(importData);
    });
};

// Create dropdown menu
function createDropdownMenu(importData) {
    var categoryArray = []
    importData.forEach(element => {
        categoryArray.push(element.Group)
    });
    // Remove duplicates by creating a set
    var uniqueCategories = [...new Set(categoryArray)];
    console.log(uniqueCategories);

    // jQuery to clear the dropdown menu before reload it
    $('#dropDownCategories').children('option').remove();


    // Pass the category strings to load the dropdown
    selectOptionAddText('#dropDownCategories', uniqueCategories);


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


