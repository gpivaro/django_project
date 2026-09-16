# views.py

from django.shortcuts import render, redirect
from clinic_dash_pro.models import GustoPayroll
from clinic_dash_pro.ingestion.gusto import gusto_payroll


def clinicdashpro_home(request):
    """
    Render the ClinicDashPro home page.

    This is the landing page for the app and does not perform
    any data processing. It simply returns the home template.
    """
    return render(request, "clinic_dash_pro/home.html")


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
        inserted, skipped = gusto_payroll(gusto_file)

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
