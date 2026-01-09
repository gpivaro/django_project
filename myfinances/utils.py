from myfinances.models import Statements
from django.http import HttpResponse
from datetime import date, timedelta
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.contrib.auth.models import Group
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


def banktransactions_upload(request, user_group):
    """
    Handle CSV upload of bank transactions with group‑scoped duplicate detection.

    Fixes:
    - Skip invalid rows BEFORE duplicate check (NaT, NaN, missing fields)
    - Prevent MySQL errors when comparing NaN values
    """

    csv_file = request.FILES.get("file")
    acct_last4 = request.POST.get("acct_last4")

    # Validate file type
    if not csv_file or not csv_file.name.lower().endswith(".csv"):
        messages.error(request, "THIS IS NOT A CSV FILE")
        return

    # Read CSV
    try:
        transactions_df = pd.read_csv(
            csv_file,
            encoding="utf-8",
            skiprows=1,
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
            quotechar='"',
        )
    except Exception as e:
        messages.error(request, f"Error reading CSV: {e}")
        return

    # Drop unused column
    transactions_df.drop(columns=["N/A"], inplace=True)

    # Normalize date
    transactions_df["Date"] = pd.to_datetime(
        transactions_df["Posting Date"], errors="coerce"
    )
    transactions_df.drop(columns=["Posting Date"], inplace=True)

    # Convert numeric fields
    transactions_df["Balance"] = pd.to_numeric(
        transactions_df["Balance"], errors="coerce"
    )
    transactions_df["Amount"] = pd.to_numeric(
        transactions_df["Amount"], errors="coerce"
    )

    # Add account info
    transactions_df["Acct_Info"] = acct_last4

    uploaded_count = 0
    declined_count = 0

    # Process each row
    for tx in transactions_df.to_dict("records"):

        # ------------------------------------------------------------------
        # ⭐ VALIDATION: Skip invalid rows BEFORE duplicate check
        # ------------------------------------------------------------------

        # Skip invalid date
        if pd.isna(tx["Date"]):
            declined_count += 1
            continue

        # Skip invalid amount or balance
        if pd.isna(tx["Amount"]) or pd.isna(tx["Balance"]):
            declined_count += 1
            continue

        try:
            Posting_Date = tx["Date"].date()
            Amount = float(tx["Amount"])
            Balance = float(tx["Balance"])
        except Exception:
            declined_count += 1
            continue

        # ------------------------------------------------------------------
        # ⭐ GROUP‑SCOPED DUPLICATE CHECK
        # ------------------------------------------------------------------
        exists = Statements.objects.filter(
            user_group=user_group,
            Details=tx["Details"],
            Posting_Date=Posting_Date,
            Description=tx["Description"],
            Amount=Amount,
            Balance=Balance,
            Acct_Info=tx["Acct_Info"],
            Type=tx["Type"],
        ).exists()

        if exists:
            declined_count += 1
            continue

        # Create new Statement
        Statements.objects.create(
            Details=tx["Details"],
            Posting_Date=Posting_Date,
            Description=tx["Description"],
            Amount=Amount,
            Type=tx["Type"],
            Balance=Balance,
            Check_Slip=tx.get("Check", ""),
            Owner=request.user,
            Acct_Info=tx["Acct_Info"],
            user_group=user_group
        )

        uploaded_count += 1

    # Report results
    messages.success(
        request,
        f"Upload complete: {uploaded_count} records added, {declined_count} records declined."
    )


def apply_account_filter(request, qs):
    """
    Applies account filtering to a queryset based on ?acct=XXXX.
    Returns (filtered_qs, selected_acct).
    """
    selected_acct = request.GET.get("acct", "")

    if selected_acct:
        qs = qs.filter(Acct_Info=selected_acct)

    return qs, selected_acct


def get_filtered_queryset(request):
    """
    Return a queryset of Statements filtered by:
    - The user's group membership (security boundary)
    - Optional date range (Posting_Date)
    - Optional category name

    Notes:
    ------
    • Account filtering is intentionally NOT done here.
      The BalanceSheetView applies account filtering via
      `get_selected_accounts()` using Acct_Info__in, which
      correctly supports multi-account selection.

    • This function must remain side‑effect free and only
      apply filters that are universally valid across all
      Balance Sheet operations (CSV export, charts, totals).
    """

    # ------------------------------------------------------------
    # 1. Base queryset: always group‑scoped for security
    # ------------------------------------------------------------
    qs = Statements.objects.filter(
        user_group__in=request.user.groups.all()
    )

    # ------------------------------------------------------------
    # 2. Extract raw GET parameters
    # ------------------------------------------------------------
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    category = request.GET.get("category")

    # ------------------------------------------------------------
    # 3. Parse dates safely
    # ------------------------------------------------------------
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # If user provides only a start date, assume "until today"
    if start_date and not end_date:
        end_date = now().date()

    # ------------------------------------------------------------
    # 4. Apply date filtering using the correct model field
    # ------------------------------------------------------------
    if start_date and end_date:
        qs = qs.filter(Posting_Date__range=[start_date, end_date])

    # ------------------------------------------------------------
    # 5. Apply category filtering
    # ------------------------------------------------------------
    if category and category != "all":
        qs = qs.filter(Category__name=category)

    return qs


def get_category_totals(qs):
    totals = (
        qs.values("Category_id", "Category__name", "Category__label")
          .annotate(total_amount=Sum("Amount"))
          .order_by("Category__name")
    )
    grand_total = sum(row["total_amount"] or 0 for row in totals)
    return totals, grand_total


def get_label_summary(qs):
    return (
        qs.values("Category__label")
          .annotate(total_amount=Sum("Amount"))
          .order_by("-total_amount")
    )


def get_chart_data(qs):
    monthly_data = (
        qs.annotate(month=TruncMonth("Posting_Date"))
          .values("month", "Category__label")
          .annotate(total_amount=Sum("Amount"))
          .order_by("month", "Category__label")
    )

    chart_data = {}
    for row in monthly_data:
        month = row["month"].strftime("%Y-%m")
        label = row["Category__label"]
        chart_data.setdefault(label, {})[month] = float(
            row["total_amount"] or 0)

    return chart_data


def get_predefined_ranges():
    today = now().date()

    current_month_start = today.replace(day=1)
    current_month_end = today

    first_day_this_month = today.replace(day=1)
    last_month_end = first_day_this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    month = today.month - 3
    year = today.year
    if month <= 0:
        month += 12
        year -= 1
    three_months_start = date(year, month, 1)
    three_months_end = last_month_end

    last_year_start = date(today.year - 1, 1, 1)
    last_year_end = date(today.year - 1, 12, 31)

    current_year_start = date(today.year, 1, 1)
    current_year_end = today

    return {
        "today": today,
        "current_month_start": current_month_start,
        "current_month_end": current_month_end,
        "last_month_start": last_month_start,
        "last_month_end": last_month_end,
        "three_months_start": three_months_start,
        "three_months_end": three_months_end,
        "last_year_start": last_year_start,
        "last_year_end": last_year_end,
        "current_year_start": current_year_start,
        "current_year_end": current_year_end,
    }


def export_balance_sheet_csv(category_totals, start_date_str, end_date_str, acct_info, category):
    timestamp = now().strftime("%Y%m%d_%H%M%S")
    filename = f"balance_sheet_{timestamp}.csv"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    writer.writerow([
        f"Balance Sheet Export ({timestamp})",
        f"Start Date: {start_date_str or 'N/A'}",
        f"End Date: {end_date_str or 'N/A'}",
        f"Account: {acct_info or 'All'}",
        f"Category: {category or 'All'}",
        f"Generated: {now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Records: {len(category_totals)}"
    ])
    writer.writerow([])
    writer.writerow(["Category", "Label", "Total"])

    for row in category_totals:
        writer.writerow([
            row["Category__name"] or "Uncategorized",
            row["Category__label"],
            f"{row['total_amount']:.2f}"
        ])

    grand_total = sum(row["total_amount"] or 0 for row in category_totals)
    writer.writerow(["TOTAL", "", f"{grand_total:.2f}"])

    return response
