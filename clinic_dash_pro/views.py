# views.py

import pandas as pd
from datetime import date, timedelta
import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from clinic_dash_pro.models import GustoPayroll, XeroTransaction, JaneSessions, JaneProcessedClaim
from clinic_dash_pro.ingestion.gusto import gusto_ingest
from clinic_dash_pro.ingestion.xero import xero_ingest
from clinic_dash_pro.ingestion.jane import jane_sessions_ingest, jane_processed_claims_ingest
from clinic_dash_pro.reports.generate_reports import GenerateReport
from clinic_dash_pro.helper.helper import convert_df_to_dict, safe_report_call, make_json_safe

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse


@staff_member_required
def admin_only_view(request):
    return HttpResponse("Staff only")


@login_required
def clinicdashpro_home(request):

    def get_model_status(model, date_field):
        count = model.objects.count()

        if count == 0:
            return {
                "count": 0,
                "start": None,
                "end": None,
                "latest": None,
                "stale": True,
            }

        start = model.objects.earliest(date_field).__dict__[date_field]
        end = model.objects.latest(date_field).__dict__[date_field]
        latest = end

        stale = latest < (date.today() - timedelta(days=15))

        return {
            "count": count,
            "start": start,
            "end": end,
            "latest": latest,
            "stale": stale,
        }

    gusto_status = get_model_status(GustoPayroll, "payroll_period_end")
    xero_status = get_model_status(XeroTransaction, "date")
    jane_sessions_status = get_model_status(JaneSessions, "purchase_date")
    jane_claims_status = get_model_status(JaneProcessedClaim, "payment_date")

    context = {
        "gusto": gusto_status,
        "xero": xero_status,
        "jane_sessions": jane_sessions_status,
        "jane_claims": jane_claims_status,
    }

    return render(request, "clinic_dash_pro/home.html", context)


@login_required
def upload_gusto(request):
    """
    Handle Gusto payroll CSV uploads.

    Workflow:
    - If GET: render upload form.
    - If POST:
        1. Validate uploaded file.
        2. Run Gusto ingestion pipeline.
        3. Receive (inserted, skipped) counts.
        4. Store counts in session for the success page.
        5. Redirect to success page.

    The ingestion pipeline (gusto_payroll) handles:
    - Parsing CSV
    - Cleaning data
    - Normalizing names
    - Generating hash_key
    - Deduplication
    - Database insertion
    """
    if request.method == "POST":

        # Retrieve uploaded file
        gusto_file = request.FILES.get("gusto")

        # Validate file type
        if not gusto_file or not gusto_file.name.endswith(".csv"):
            return render(request, "clinic_dash_pro/upload_gusto.html", {
                "errors": ["Gusto file must be a CSV"]
            })

        request.session["upload_error"] = None
        try:
            inserted, skipped, updated = gusto_ingest(
                gusto_file)

            return redirect("gusto_upload_success")

        except Exception as err:
            # Capture the actual error message
            if isinstance(err, KeyError):
                error_message = f"Missing required column: {err}"
            else:
                error_message = f"Upload failed: {str(err)}"

            # Store error in session so success page can show it
            request.session["upload_error"] = error_message

            inserted = 0
            skipped = 0
            updated = 0

        # Success → store counts
        request.session["inserted_rows"] = inserted
        request.session["skipped_rows"] = skipped
        request.session["updated_rows"] = updated

        # Redirect to success page
        return redirect("gusto_upload_success")

    # GET request → show upload form
    return render(request, "clinic_dash_pro/upload_gusto.html")


@login_required
def gusto_upload_success(request):
    """
    Display results of the Gusto payroll upload.

    Shows:
    - Number of rows inserted during last upload
    - Number of duplicates skipped
    - Total rows in database
    - Earliest and latest payroll period dates

    Counts are retrieved from Django session, set in upload_gusto().
    """
    # Retrieve counts from session (default to 0)
    inserted = request.session.get("inserted_rows", 0)
    skipped = request.session.get("skipped_rows", 0)
    updated = request.session.get("updated_rows", 0)
    upload_error = request.session.get("upload_error")

    # Total rows in DB
    count = GustoPayroll.objects.count()

    # Determine payroll period range
    if count > 0:
        start = GustoPayroll.objects.earliest(
            "payroll_period_start"
        ).payroll_period_start

        end = GustoPayroll.objects.latest(
            "payroll_period_end"
        ).payroll_period_end
    else:
        start = end = None

    # Render success page
    return render(request, "clinic_dash_pro/upload_success.html", {
        "title": "Gusto Upload Completed",
        "subtitle": "Your Gusto Payroll File Was Processed",
        "data_description": "payroll",
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
        "updated": updated,
        "upload_additional_records_url": reverse("upload_gusto"),
        "upload_error": upload_error
    })


@login_required
def upload_xero(request):
    if request.method == "POST":

        xero_file = request.FILES.get("xero_transactions")

        if not xero_file or not xero_file.name.endswith(".xlsx"):
            return render(request, "clinic_dash_pro/upload_xero.html", {
                "errors": ["Xero file must be an Excel .xlsx file"]
            })

        request.session["upload_error"] = None
        try:
            inserted, skipped, updated = xero_ingest(
                xero_file)

            return redirect("xero_upload_success")

        except Exception as err:
            # Capture the actual error message
            if isinstance(err, KeyError):
                error_message = f"Missing required column: {err}"
            else:
                error_message = f"Upload failed: {str(err)}"

            # Store error in session so success page can show it
            request.session["upload_error"] = error_message

            inserted = 0
            skipped = 0
            updated = 0

        # Success → store counts
        request.session["inserted_rows"] = inserted
        request.session["skipped_rows"] = skipped
        request.session["updated_rows"] = updated

        return redirect("xero_upload_success")

    return render(request, "clinic_dash_pro/upload_xero.html")


@login_required
def xero_upload_success(request):
    inserted = request.session.get("inserted_rows", 0)
    skipped = request.session.get("skipped_rows", 0)
    updated = request.session.get("updated_rows", 0)
    upload_error = request.session.get("upload_error")

    count = XeroTransaction.objects.count()

    if count > 0:
        start = XeroTransaction.objects.earliest("date").date
        end = XeroTransaction.objects.latest("date").date
    else:
        start = end = None

    return render(request, "clinic_dash_pro/upload_success.html", {
        "title": "Xero Upload Completed",
        "subtitle": "Your Xero Transactions File Was Processed",
        "data_description": "categorized transactions",
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
        "updated": "",
        "upload_additional_records_url": reverse("upload_xero"),
        "upload_error": upload_error

    })


@login_required
def upload_jane_sessions(request):
    if request.method == "POST":

        jane_file = request.FILES.get("jane_staff_sessions")

        if not jane_file or not jane_file.name.endswith(".csv"):
            return render(request, "clinic_dash_pro/upload_jane_sessions.html", {
                "errors": ["Jane Sessions file must be a CSV file"]
            })

        request.session["upload_error"] = None
        try:
            inserted, skipped, updated = jane_sessions_ingest(
                jane_file)

            return redirect("jane_sessions_upload_success")

        except Exception as err:
            # Capture the actual error message
            if isinstance(err, KeyError):
                error_message = f"Missing required column: {err}"
            else:
                error_message = f"Upload failed: {str(err)}"

            # Store error in session so success page can show it
            request.session["upload_error"] = error_message

            inserted = 0
            skipped = 0
            updated = 0

        # Success → store counts
        request.session["inserted_rows"] = inserted
        request.session["skipped_rows"] = skipped
        request.session["updated_rows"] = updated

        return redirect("jane_sessions_upload_success")

    return render(request, "clinic_dash_pro/upload_jane_sessions.html")


@login_required
def jane_sessions_upload_success(request):
    inserted = request.session.get("inserted_rows", 0)
    skipped = request.session.get("skipped_rows", 0)
    updated = request.session.get("updated_rows", 0)
    upload_error = request.session.get("upload_error")

    count = JaneSessions.objects.count()

    if count > 0:
        start = JaneSessions.objects.earliest("purchase_date").purchase_date
        end = JaneSessions.objects.latest("purchase_date").purchase_date
    else:
        start = end = None

    return render(request, "clinic_dash_pro/upload_success.html", {
        "title": "Jane Sessions Upload Completed",
        "subtitle": "Your Jane Sessions File Was Processed",
        "data_description": "staff session",
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
        "updated": updated,
        "upload_additional_records_url": reverse("upload_jane_sessions"),
        "upload_error": upload_error
    })


@login_required
def upload_jane_processed_claims(request):
    if request.method == "POST":

        jane_file = request.FILES.get("jane_processed_claims")

        if not jane_file or not jane_file.name.endswith(".csv"):
            return render(request, "clinic_dash_pro/upload_jane_processed_claims.html", {
                "errors": ["Jane Processed Claims file must be a CSV file"]
            })

        request.session["upload_error"] = None
        try:
            inserted, skipped, updated = jane_processed_claims_ingest(
                jane_file)

        except Exception as err:
            # Capture the actual error message
            if isinstance(err, KeyError):
                error_message = f"Missing required column: {err}"
            else:
                error_message = f"Upload failed: {str(err)}"

            # Store error in session so success page can show it
            request.session["upload_error"] = error_message

            inserted = 0
            skipped = 0
            updated = 0

        # Success → store counts
        request.session["inserted_rows"] = inserted
        request.session["skipped_rows"] = skipped
        request.session["updated_rows"] = updated

        # Also show error immediately on upload page
        return redirect("jane_processed_claims_upload_success")

    # GET request → show upload page
    return render(request, "clinic_dash_pro/upload_jane_processed_claims.html")


@login_required
def jane_processed_claims_upload_success(request):
    inserted = request.session.get("inserted_rows", 0)
    skipped = request.session.get("skipped_rows", 0)
    updated = request.session.get("updated_rows", 0)
    upload_error = request.session.get("upload_error")

    count = JaneProcessedClaim.objects.count()

    if count > 0:
        start = JaneProcessedClaim.objects.earliest(
            "payment_date").payment_date
        end = JaneProcessedClaim.objects.latest("payment_date").payment_date
    else:
        start = end = None

    return render(request, "clinic_dash_pro/upload_success.html", {
        "title": "Jane Claims Upload Completed",
        "subtitle": "Your Jane Claims File Was Processed",
        "data_description": "insurance claim",
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
        "updated": updated,
        "upload_additional_records_url": reverse("upload_jane_processed_claims"),
        "upload_error": upload_error

    })


@login_required
def gusto_list(request):

    REMOVE_FIELDS = [
        "time_off_hours",
        "time_off_amount",
        "time_off_rate",
        "employee_type",
        "payment",
        "additional_earnings",
        "federal_income_tax_employee",
        "social_security_employee",
        "medicare_employee",
        "additional_medicare_employee",
        "social_security_employer",
        "medicare_employer",
        "tx_suta_employer",
        "futa_employer",
        "reimbursements",
        "donations",
        "check_amount",
        "insert_date",
        "hash_key",
        "id",
    ]

    return generic_list_view(
        request,
        model=GustoPayroll,
        title="Gusto Payroll Records",
        date_field="payroll_period_start",
        remove_fields=REMOVE_FIELDS,
        model_name="GustoPayroll"
    )


@login_required
def xero_list(request):

    REMOVE_FIELDS = [
        "account_type",
    ]

    return generic_list_view(
        request,
        model=XeroTransaction,
        title="Xero Transactions",
        date_field="date",
        remove_fields=REMOVE_FIELDS,
        model_name="XeroTransaction"
    )


@login_required
def jane_sessions_list(request):

    REMOVE_FIELDS = ["updated_date",]

    return generic_list_view(
        request,
        model=JaneSessions,
        title="Jane Sessions Records",
        date_field="purchase_date",
        remove_fields=REMOVE_FIELDS,
        model_name="JaneSessions"
    )


@login_required
def jane_claims_list(request):
    return generic_list_view(
        request,
        model=JaneProcessedClaim,
        title="Jane Processed Claims",
        date_field="payment_date",
        model_name="JaneProcessedClaim"
    )


@login_required
def revenue_details_view(request):

    # Pull data for all sources to process
    xero_data = XeroTransaction.objects.all().values()
    gusto_data = GustoPayroll.objects.all().values()
    jane_sessions_data = JaneSessions.objects.all().values()
    jane_claims_data = JaneProcessedClaim.objects.all().values()

    # Reporting engine
    reports = GenerateReport(
        gusto_data, jane_sessions_data, jane_claims_data, xero_data
    )

    # SAFETY WRAPPER — prevents crashes when DB is empty
    try:
        df = reports.get_revenue_details()
    except Exception:
        df = pd.DataFrame()  # safe fallback

    # SAFETY — if df is None or not a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()

    # SAFETY — convert Period columns → string
    for col in df.columns:
        try:
            if isinstance(df[col].dtype, pd.PeriodDtype):
                df[col] = df[col].astype(str)
        except Exception:
            pass

    # SAFETY — convert Python date/datetime → string
    for col in df.columns:
        try:
            if df[col].dtype == "object":
                df[col] = df[col].apply(
                    lambda x: x.isoformat()
                    if isinstance(x, (datetime.date, datetime.datetime))
                    else x
                )
        except Exception:
            pass

    # SAFETY — generic_list_view will handle empty df gracefully
    return generic_list_view(
        request,
        df=df,
        title="Revenue Details",
        date_field="purchase_date",
        remove_fields=["balance", "subtotal",
                       "Actual Collected", "applied_to"],
    )


@login_required
def generic_list_view(request, model=None, df=None, title="", date_field="", remove_fields=None, model_name=None):

    q = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", date_field)

    EXCLUDE_DEFAULT = ("id", "hash_key", "insert_date")
    EXCLUDE_FIELDS = set(EXCLUDE_DEFAULT) | set(remove_fields or [])

    is_df = df is not None

    # --- Fields ---
    if is_df:
        try:
            fields = [c for c in df.columns if c not in EXCLUDE_FIELDS]
        except Exception:
            fields = []
    else:
        fields = [
            f.name for f in model._meta.get_fields()
            if f.concrete and f.name not in EXCLUDE_FIELDS
        ]

    # --- Filtering ---
    if is_df:
        if q and fields:
            try:
                mask = False
                for f in fields:
                    if f in df.columns:
                        mask |= df[f].astype(str).str.contains(
                            q, case=False, na=False)
                df = df[mask]
            except Exception:
                pass

    else:
        queryset = model.objects.all()
        if q:
            search_filters = Q()
            for f in fields:
                search_filters |= Q(**{f"{f}__icontains": q})
            queryset = queryset.filter(search_filters)

        # Save filtered IDs for export
        request.session["filtered_ids"] = list(
            queryset.values_list("id", flat=True))

    # --- Sorting ---
    sort_field = sort.lstrip("-")
    ascending = not sort.startswith("-")

    if is_df:
        if sort_field in df.columns:
            try:
                df = df.sort_values(sort_field, ascending=ascending)
            except Exception:
                pass
    else:
        queryset = queryset.order_by(sort)

    # --- Save DF export data (JSON-safe) AFTER filtering + sorting ---
    if is_df:
        try:
            safe_records = []
            for row in df.to_dict("records"):
                safe_row = {k: make_json_safe(v) for k, v in row.items()}
                safe_records.append(safe_row)

            request.session["df_export"] = safe_records
            request.session["df_fields"] = fields

        except Exception:
            request.session["df_export"] = []
            request.session["df_fields"] = []

    # --- Pagination ---
    if is_df:
        try:
            items = Paginator(df.to_dict("records"), 50).get_page(
                request.GET.get("page"))
        except Exception:
            items = Paginator([], 50).get_page(request.GET.get("page"))
    else:
        items = Paginator(queryset, 50).get_page(request.GET.get("page"))

    return render(request, "clinic_dash_pro/list_view.html", {
        "title": title,
        "items": items,
        "fields": fields,
        "sort": sort,
        "q": q,
        "model_name": model_name,
    })


@login_required
def reports_home(request):

    # Pull data for all sources to process
    xero_data = XeroTransaction.objects.all().values()
    gusto_data = GustoPayroll.objects.all().values()
    jane_sessions_data = JaneSessions.objects.all().values()
    jane_claims_data = JaneProcessedClaim.objects.all().values()

    # Reporting engine
    reports = GenerateReport(
        gusto_data, jane_sessions_data, jane_claims_data, xero_data
    )

    # Safe report calls
    monthly_operational_expenses_assets = safe_report_call(
        reports.get_operational_report
    )

    unified_financials = safe_report_call(
        reports.get_unified_financials
    )

    therapist_profitability = safe_report_call(
        reports.get_analyze_unified_financials
    )

    operating_expenses_breakdown = safe_report_call(
        reports.get_operating_expenses_breakdown
    )

    income_statement = safe_report_call(
        reports.get_income_statement
    )

    revenue_details = safe_report_call(
        reports.get_revenue_details
    )

    context = {
        "monthly_operational_expenses_assets": convert_df_to_dict(monthly_operational_expenses_assets),
        "unified_financials": convert_df_to_dict(unified_financials),
        "therapist_profitability": convert_df_to_dict(therapist_profitability),
        "operating_expenses_breakdown": convert_df_to_dict(operating_expenses_breakdown),
        "income_statement": convert_df_to_dict(income_statement),
        "revenue_details": convert_df_to_dict(revenue_details),
    }

    return render(request, "clinic_dash_pro/report_home.html", context)
