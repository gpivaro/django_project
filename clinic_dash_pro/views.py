# views.py

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from clinic_dash_pro.models import GustoPayroll, XeroTransaction, JaneStaffSale, JaneProcessedClaim
from clinic_dash_pro.ingestion.gusto import gusto_ingest
from clinic_dash_pro.ingestion.xero import xero_ingest
from clinic_dash_pro.ingestion.jane import jane_staff_sales_ingest, jane_processed_claims_ingest
from datetime import date, timedelta


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
    jane_sales_status = get_model_status(JaneStaffSale, "purchase_date")
    jane_claims_status = get_model_status(JaneProcessedClaim, "payment_date")

    context = {
        "gusto": gusto_status,
        "xero": xero_status,
        "jane_sales": jane_sales_status,
        "jane_claims": jane_claims_status,
    }

    return render(request, "clinic_dash_pro/home.html", context)


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

        # Run ingestion pipeline
        inserted, skipped = gusto_ingest(gusto_file)

        # Store ingestion results in session
        request.session["gusto_inserted"] = inserted
        request.session["gusto_skipped"] = skipped

        # Redirect to success page
        return redirect("gusto_upload_success")

    # GET request → show upload form
    return render(request, "clinic_dash_pro/upload_gusto.html")


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
    inserted = request.session.get("gusto_inserted", 0)
    skipped = request.session.get("gusto_skipped", 0)

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
    return render(request, "clinic_dash_pro/gusto_upload_success.html", {
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
    })


def upload_xero(request):
    if request.method == "POST":

        xero_file = request.FILES.get("xero")

        if not xero_file or not xero_file.name.endswith(".xlsx"):
            return render(request, "clinic_dash_pro/upload_xero.html", {
                "errors": ["Xero file must be an Excel .xlsx file"]
            })

        inserted, skipped = xero_ingest(xero_file)

        request.session["xero_inserted"] = inserted
        request.session["xero_skipped"] = skipped

        return redirect("xero_upload_success")

    return render(request, "clinic_dash_pro/upload_xero.html")


def xero_upload_success(request):
    inserted = request.session.get("xero_inserted", 0)
    skipped = request.session.get("xero_skipped", 0)

    count = XeroTransaction.objects.count()

    if count > 0:
        start = XeroTransaction.objects.earliest("date").date
        end = XeroTransaction.objects.latest("date").date
    else:
        start = end = None

    return render(request, "clinic_dash_pro/xero_upload_success.html", {
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
    })


def upload_jane_staff_sales(request):
    if request.method == "POST":

        jane_file = request.FILES.get("jane_staff_sales")

        if not jane_file or not jane_file.name.endswith(".csv"):
            return render(request, "clinic_dash_pro/upload_jane_sales.html", {
                "errors": ["Jane Sales file must be a CSV file"]
            })

        inserted, skipped = jane_staff_sales_ingest(jane_file)

        request.session["jane_sales_inserted"] = inserted
        request.session["jane_sales_skipped"] = skipped

        return redirect("jane_staff_sales_upload_success")

    return render(request, "clinic_dash_pro/upload_jane_staff_sales.html")


def jane_staff_sales_upload_success(request):
    inserted = request.session.get("jane_sales_inserted", 0)
    skipped = request.session.get("jane_sales_skipped", 0)

    count = JaneStaffSale.objects.count()

    if count > 0:
        start = JaneStaffSale.objects.earliest("purchase_date").purchase_date
        end = JaneStaffSale.objects.latest("purchase_date").purchase_date
    else:
        start = end = None

    return render(request, "clinic_dash_pro/jane_staff_sales_upload_success.html", {
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
    })


def upload_jane_processed_claims(request):
    if request.method == "POST":

        jane_file = request.FILES.get("jane_processed_claims")

        if not jane_file or not jane_file.name.endswith(".csv"):
            return render(request, "clinic_dash_pro/upload_jane_processed_claims.html", {
                "errors": ["Jane Processed Claims file must be a CSV file"]
            })

        inserted, skipped = jane_processed_claims_ingest(jane_file)

        request.session["jane_claims_inserted"] = inserted
        request.session["jane_claims_skipped"] = skipped

        return redirect("jane_processed_claims_upload_success")

    return render(request, "clinic_dash_pro/upload_jane_processed_claims.html")


def jane_processed_claims_upload_success(request):
    inserted = request.session.get("jane_claims_inserted", 0)
    skipped = request.session.get("jane_claims_skipped", 0)

    count = JaneProcessedClaim.objects.count()

    if count > 0:
        start = JaneProcessedClaim.objects.earliest(
            "payment_date").payment_date
        end = JaneProcessedClaim.objects.latest("payment_date").payment_date
    else:
        start = end = None

    return render(request, "clinic_dash_pro/jane_processed_claims_upload_success.html", {
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
    })


def gusto_list(request):
    return generic_list_view(
        request,
        GustoPayroll,
        "Gusto Payroll Records",
        "payroll_period_start"
    )


def xero_list(request):
    return generic_list_view(
        request,
        XeroTransaction,
        "Xero Transactions",
        "date"
    )


def jane_sales_list(request):
    return generic_list_view(
        request,
        JaneStaffSale,
        "Jane Sales Records",
        "purchase_date"
    )


def jane_claims_list(request):
    return generic_list_view(
        request,
        JaneProcessedClaim,
        "Jane Processed Claims",
        "payment_date"
    )


def generic_list_view(request, model, title, date_field):
    # Filtering
    q = request.GET.get("q", "").strip()

    queryset = model.objects.all()

    if q:
        queryset = queryset.filter(
            Q(id__icontains=q) |
            Q(hash_key__icontains=q) |
            Q(insert_date__icontains=q)
        )

    # Sorting
    sort = request.GET.get("sort", date_field)
    if sort.startswith("-"):
        queryset = queryset.order_by(sort)
    else:
        queryset = queryset.order_by(sort)

    # Pagination
    paginator = Paginator(queryset, 50)
    page = request.GET.get("page")
    items = paginator.get_page(page)

    # Get all fields dynamically
    EXCLUDE_FIELDS = ("id", "hash_key", "insert_date")

    fields = [
        f.name for f in model._meta.get_fields()
        if f.concrete and f.name not in EXCLUDE_FIELDS
    ]

    return render(request, "clinic_dash_pro/list_view.html", {
        "title": title,
        "items": items,
        "fields": fields,
        "sort": sort,
        "q": q,
    })
