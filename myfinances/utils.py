import os
import pandas as pd
import numpy as np
import re
from .models import Statements
from django.db.models import Q


""" Received the transactions data, the list of categorized transactions, the start and end date.
    Adjust the list of transactions of the data, clean the data and categorize it. 
    Return the transactions categorized and the categories list.
"""


# Helper function to upload transactions to the Statement model
def upload_transactions_to_db(transactions):
    for tx in transactions:
        # Parse date and amount safely
        try:
            Posting_Date = tx["Date"].date()
            Amount = float(tx["Amount"])
            Balance = float(tx["Balance"])
        except (ValueError, KeyError):
            continue  # Skip malformed entries

        # Check for duplicates using a combination of key fields
        exists = Statements.objects.filter(
            Q(Details=tx["Details"]) &
            Q(Posting_Date=Posting_Date) &
            Q(Description=tx["Description"]) &
            Q(Amount=Amount) &
            Q(Balance=Balance)
        ).exists()

        if not exists:
            Statements.objects.create(
                Details=tx["Details"],
                Posting_Date=Posting_Date,
                Description=tx["Description"],
                Amount=Amount,
                Type=tx["Type"],
                Balance=tx["Balance"],
                Check_Slip=tx.get("Check", "")
            )

def label_transactions(data, categories_words_cleaned_df, start_date="", end_date=""):

    # Convert the input data in a dataframe
    chase_df = pd.DataFrame(data)

    chase_df["Date"] = chase_df["Posting Date"].astype("datetime64[ns]")
    chase_df.drop(columns=["Posting Date"], inplace=True)
    chase_df["Amount"] = chase_df["Amount"].astype("float")

    # Create new dataframe
    chase_new_df = chase_df

    # Fill the empty values for the pending transactions balance
    chase_new_df["Balance"].iloc[0] == " "
    chase_new_df.loc[chase_new_df["Balance"] == " ", "Balance"] = 0
    chase_new_df["Balance"] = chase_new_df["Balance"].astype("float")

    # Set NAN values to 0
    chase_new_df.loc[chase_new_df["Check"].isnull(), "Check"] = 0

    # Get the oldest and the newest date
    oldest_date = chase_new_df["Date"].min()
    newest_date = chase_new_df["Date"].max()

    # Verify if a start date was provided. If not use the oldest date
    if start_date == "":
        start_date = oldest_date

    # Verify if a end date was provided. If not use the newest date
    if end_date == "":
        end_date = newest_date

    # Filtering dataset entries
    month_transactions = chase_new_df.loc[
        (chase_new_df["Date"] >= start_date) & (chase_new_df["Date"] < end_date)
    ].sort_values("Date", ascending=False)

    # Reset the ndex to index the transactions on the new order
    month_transactions.reset_index(inplace=True)

    # Drop columns for visualization purposes
    month_transactions.drop(columns=["index"], inplace=True)
    
        
    # Upload to database while avoiding duplicates
    upload_transactions_to_db(month_transactions.to_dict("records"))

    # Import cleaned expressions and groups
    # categories_words_cleaned_df = pd.read_csv(categories_words_cleaned_file)
    categories_words_cleaned_df.sort_values("Expression", inplace=True)

    # Get list of categories
    categories_list = sorted(list(categories_words_cleaned_df["Group"].unique()))

    # Search the patterns
    patterns = list(categories_words_cleaned_df["Expression"])
    month_transactions["Category"] = ""
    month_transactions = month_transactions.copy()

    # Iterate over all the transactions
    for index, row in month_transactions.iterrows():
        # Search and match the first occurency of the table
        text = row["Description"]
        for n in range(len(patterns)):
            if re.search(patterns[n], text):
                month_transactions.loc[index, "Category"] = categories_words_cleaned_df.loc[n, "Group"]
                break

    statement_dict = month_transactions.to_dict("records")
    



    return {"statement_dict": statement_dict, "categories_list": categories_list}