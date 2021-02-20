import csv, io
from django.shortcuts import render, reverse
from django.contrib import messages
from .models import Statement, Categories
from django.http import JsonResponse
from .utils import label_transactions
import requests
import pandas as pd

# Create your views here.
# one parameter named request
def home(request):
    return render(request, "myfinances/home.html")


# one parameter named request
def statement_upload(request):
    # declaring template
    template = "myfinances/index.html"
    data = Statement.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        "order": "Upload your statement file.",
        "statements": data,
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES["file"]

    # let's check if it is a csv file
    if csv_file.name.endswith(".CSV") or csv_file.name.endswith(".csv"):
        pass
    else:
        messages.error(request, "THIS IS NOT A CSV FILE")
    data_set = csv_file.read().decode("UTF-8")
    # setup a stream which is when we loop through each line we are able to handle a data in a stream

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    io_string = io.StringIO(data_set)
    next(io_string)
    transactions_list = []
    for column in csv.reader(io_string, delimiter=",", quotechar="|"):

        transactions_list.append(
            {
                "Details": column[0],
                "Posting Date": column[1],
                "Description": column[2],
                "Amount": column[3],
                "Type": column[4],
                "Balance": column[5],
                "Check": column[6],
            }
        )

    # Query database for list of categories and convert to dataframe
    categories = Categories.objects.all().values()
    categories_df = pd.DataFrame(categories)

    # Call function to label the transactions
    labeled_transactions = label_transactions(
        transactions_list, categories_df, start_date, end_date
    )

    # Create a table row ID for table classification purpouses
    table_row_id = list(range(len(labeled_transactions["statement_dict"])))

    context = {
        "transactions_list": labeled_transactions["statement_dict"],
        "categories_list": labeled_transactions["categories_list"],
        "table_row_id": table_row_id,
    }

    selected_end_date = labeled_transactions["statement_dict"][0]["Date"].strftime(
        "%m/%d/%Y"
    )
    selected_start_date = labeled_transactions["statement_dict"][
        len(labeled_transactions["statement_dict"]) - 1
    ]["Date"].strftime("%m/%d/%Y")

    messages.success(
        request,
        f"You have uploaded {csv_file} and selected {selected_start_date} to {selected_end_date}.",
    )
    return render(request, template, context)


def categories(request):
    data = list(Categories.objects.all().values())
    return JsonResponse(data, safe=False)
