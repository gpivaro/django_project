import os
import csv
import io
import pandas as pd
import numpy as np
import re
from .models import Statements
from django.db.models import Q
from django.contrib import messages


""" Received the transactions data, the list of categorized transactions, the start and end date.
    Adjust the list of transactions of the data, clean the data and categorize it. 
    Return the transactions categorized and the categories list.
"""


# Helper function to upload transactions to the Statement model
def upload_transactions_to_db(transactions, owner):
    for tx in transactions:
        try:
            Posting_Date = tx["Date"].date()
            Amount = float(tx["Amount"])
            Balance = float(tx["Balance"])
        except (ValueError, KeyError):
            continue  # Skip malformed entries

        exists = Statements.objects.filter(
            Q(Details=tx["Details"]) &
            Q(Posting_Date=Posting_Date) &
            Q(Description=tx["Description"]) &
            Q(Amount=Amount) &
            Q(Balance=Balance) &
            Q(Owner=owner)   # ✅ check duplicates per user
        ).exists()

        if not exists:
            Statements.objects.create(
                Details=tx["Details"],
                Posting_Date=Posting_Date,
                Description=tx["Description"],
                Amount=Amount,
                Type=tx["Type"],
                Balance=tx["Balance"],
                Check_Slip=tx.get("Check", ""),
                Owner=owner   # ✅ assign authenticated user
            )


def label_transactions(data, categories_words_cleaned_df, owner, start_date="", end_date=""):
    chase_df = pd.DataFrame(data)
    chase_df["Date"] = chase_df["Posting Date"].astype("datetime64[ns]")
    chase_df.drop(columns=["Posting Date"], inplace=True)
    chase_df["Amount"] = chase_df["Amount"].astype("float")

    chase_new_df = chase_df
    chase_new_df.loc[chase_new_df["Balance"] == " ", "Balance"] = 0
    chase_new_df["Balance"] = chase_new_df["Balance"].astype("float")
    chase_new_df.loc[chase_new_df["Check"].isnull(), "Check"] = 0

    oldest_date = chase_new_df["Date"].min()
    newest_date = chase_new_df["Date"].max()
    if start_date == "":
        start_date = oldest_date
    if end_date == "":
        end_date = newest_date

    month_transactions = chase_new_df.loc[
        (chase_new_df["Date"] >= start_date) & (
            chase_new_df["Date"] < end_date)
    ].sort_values("Date", ascending=False)

    month_transactions.reset_index(inplace=True)
    month_transactions.drop(columns=["index"], inplace=True)

    # ✅ pass owner to upload
    upload_transactions_to_db(month_transactions.to_dict("records"), owner)

    categories_words_cleaned_df.sort_values("Expression", inplace=True)
    categories_list = sorted(
        list(categories_words_cleaned_df["Group"].unique()))

    patterns = list(categories_words_cleaned_df["Expression"])
    month_transactions["Category"] = ""
    month_transactions = month_transactions.copy()

    for index, row in month_transactions.iterrows():
        text = row["Description"]
        for n in range(len(patterns)):
            if re.search(patterns[n], text):
                month_transactions.loc[index,
                                       "Category"] = categories_words_cleaned_df.loc[n, "Group"]
                break

    statement_dict = month_transactions.to_dict("records")
    return {"statement_dict": statement_dict, "categories_list": categories_list}


def banktransactions_upload(request):
    """
    Handle CSV upload of bank transactions:
    - Validate file type
    - Parse CSV into a pandas DataFrame
    - Clean and normalize data (dates, numeric fields)
    - Upload new transactions to the database
    - Return counts of uploaded vs declined records
    """

    csv_file = request.FILES.get("file")
    acct_last4 = request.POST.get("acct_last4")

    # ✅ Validate file extension
    if not csv_file or not csv_file.name.lower().endswith(".csv"):
        messages.error(request, "THIS IS NOT A CSV FILE")
        return

    # ✅ Read CSV directly into DataFrame
    try:
        transactions_df = pd.read_csv(
            csv_file,
            encoding="utf-8",
            skiprows=1,  # skip header row if bank adds metadata line
            names=[
                "Details",
                "Posting Date",
                "Description",
                "Amount",
                "Type",
                "Balance",
                "Check",
                "N/A"
            ],
            quotechar='"',   # handle quoted text properly
        )
    except Exception as e:
        messages.error(request, f"Error reading CSV: {e}")
        return

    # ✅ Drop unused column
    transactions_df.drop(columns=["N/A"], inplace=True)

    # ✅ Convert Posting Date to datetime
    transactions_df["Date"] = pd.to_datetime(
        transactions_df["Posting Date"], errors="coerce"
    )
    transactions_df.drop(columns=["Posting Date"], inplace=True)

    # ✅ Ensure Balance is numeric and drop invalid rows
    transactions_df["Balance"] = pd.to_numeric(
        transactions_df["Balance"], errors="coerce")
    transactions_df = transactions_df.dropna(subset=["Balance"])

    # ✅ Ensure Amount is numeric
    transactions_df["Amount"] = pd.to_numeric(
        transactions_df["Amount"], errors="coerce")

    # add bank account
    transactions_df["Acct_Info"] = acct_last4

    # (Optional) Save cleaned CSV for debugging
    # transactions_df.to_csv("ignore_folder/test_transactions.csv", index=False)

    # --- Upload to DB ---
    uploaded_count = 0
    declined_count = 0

    for tx in transactions_df.to_dict("records"):
        try:
            Posting_Date = tx["Date"].date()
            Amount = float(tx["Amount"])
            Balance = float(tx["Balance"])
        except (ValueError, KeyError, AttributeError):
            declined_count += 1
            continue  # Skip malformed entries

        # ✅ Check for duplicates per user
        exists = Statements.objects.filter(
            Q(Details=tx["Details"]) &
            Q(Posting_Date=Posting_Date) &
            Q(Description=tx["Description"]) &
            Q(Amount=Amount) &
            Q(Balance=Balance) &
            Q(Owner=request.user) &
            Q(Acct_Info=tx["Acct_Info"])
        ).exists()

        if not exists:
            Statements.objects.create(
                Details=tx["Details"],
                Posting_Date=Posting_Date,
                Description=tx["Description"],
                Amount=Amount,
                Type=tx["Type"],
                Balance=Balance,
                Check_Slip=tx.get("Check", ""),
                Owner=request.user,
                Acct_Info=tx["Acct_Info"]
            )
            uploaded_count += 1
        else:
            declined_count += 1

    # ✅ Report results back to user
    messages.success(
        request,
        f"Upload complete: {uploaded_count} records added, {declined_count} records declined."
    )
