// Update categories using Jquery/Ajax


$(document).ready(function () {

    // CSRF Failed: CSRF token missing or incorrect
    // https://stackoverflow.com/questions/26639169/csrf-failed-csrf-token-missing-or-incorrect
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    //console.log(`csrftoken=${csrftoken}`);

    // Event listener for the update button
    $(document).on('click', '.updateButton', function () {

        // Get the category ID based on the even
        var category_ID = $(this).attr('category_id');
        // Get the category value (text)
        var category = $('#categoryInput' + category_ID).val();
        // Get the expression value (text)
        var expression = $('#expressionInput' + category_ID).val();


        // Set the request to the backend using Ajax and PUT method
        req = $.ajax({
            url: `/myfinances/api/categories/${category_ID}/`,
            type: 'PUT',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                "id": category_ID,
                "Group": category,
                "Expression": expression,
                "Class": "",
                "Owner": "gfp.1@hotmail.com",
            },
            success: function (data) {
                console.log(data);
                // Fade out and fade in the section to visualization
                $('#category_id' + category_ID).fadeOut(1111).fadeIn(1111);
            },
            error: function (error) {
                console.log(error);
            }
        });

    });



    // Event listener for the delete button
    $(document).on('click', '.deleteButton', function () {

        console.log('Clicked');
        // Get the category ID based on the even
        var category_ID = $(this).attr('category_id');



        // Set the request to the backend using Ajax and PUT method
        req = $.ajax({
            url: `/myfinances/api/categories/${category_ID}/`,
            type: 'DELETE',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                "id": category_ID,
            },
            success: function () {
                console.log("Category deleted successfuly.");
                // Fade out and fade in the section to visualization
                // $('#category_id' + category_ID).fadeOut(1111);
                $('#row_id' + category_ID).fadeOut(1111);
            },
            error: function (error) {
                console.log(error);
            }
        });



    });


    // Event listener for the create button
    $('.createButton').on('click', function () {

        // Get the category value (text)
        var category = $('#newCategoryInput').val();
        // Get the expression value (text)
        var expression = $('#newExpressionInput').val();


        // Set the request to the backend using Ajax and PUT method
        req = $.ajax({
            url: `/myfinances/api/categories/`,
            type: 'POST',
            headers: { "X-CSRFToken": csrftoken },
            data: {
                "Group": category,
                "Expression": expression,
                "Class": "",
                "Owner": "gfp.1@hotmail.com",
            },
            success: function (data) {
                console.log(data);
                // Update table with new data
                $('#tableCategories tr:last').after(`<tr id="row_id${data.id}">
                                                                <td>
                                                                    <div id="category_id${data.id}" class="panel panel-default">
                                                                        <!-- <div class="panel-heading">
                                                                            <span class="panel-title">Number: <span id="expression${data.id}">${data.id}</span>
                                                                            </span>
                                                                        </div> -->

                                                                        <div class="panel-body">
                                                                            <div class="form-inline">
                                                                                <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                                                                                <div class="form-group">
                                                                                    <label for="categoryInput${data.id}"></label>
                                                                                    <input type="text" class="form-control ml-2"
                                                                                        id="categoryInput${data.id}" value="${data.Group}">
                                                                                </div>

                                                                                <div class="form-group ml-4">
                                                                                    <label for="expressionInput${data.id}"></label>
                                                                                    <input type="text" class="form-control ml-2"
                                                                                        id="expressionInput${data.id}" value="${data.Expression}">
                                                                                </div>
                                                                                
                                                                                <button class="btn btn-warning updateButton ml-4"
                                                                                category_id="${data.id}">Update</button>
                                
                                                                                <button class="btn btn-danger deleteButton ml-4"
                                                                                    category_id="${data.id}">Delete</button>

                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </td>
                                                            </tr>`);
                // Fade out and fade in the section to visualization

                $('#alertSucces').removeClass("d-none");
                $('#alertSucces').hide().delay(111).fadeIn(1111).fadeOut(5111);


                $('#newCategory').fadeOut(1);
                $('#newCategoryInput').val("Category");
                $('#newExpressionInput').val("Expression");
                $('#newCategory').fadeIn(111);

            },
            error: function (error) {
                console.log(error);
                if (error.responseJSON.Group) {
                    alert(`Category: ${error.responseJSON.Group}`);
                }

                if (error.responseJSON.Expression) {
                    alert(`Expression: ${error.responseJSON.Expression}`);
                }
            }
        });

    });


})
