# views.py


from django.shortcuts import render, redirect
from clinic_dash_pro.models import GustoPayroll
from clinic_dash_pro.ingestion.gusto import gusto_payroll


def clinicdashpro_home(request):
    return render(request, "clinic_dash_pro/home.html")


def upload_gusto(request):
    if request.method == "POST":

        gusto_file = request.FILES.get("gusto")

        if not gusto_file or not gusto_file.name.endswith(".csv"):
            return render(request, "clinic_dash_pro/upload_gusto.html", {
                "errors": ["Gusto file must be a CSV"]
            })

        # Run ingestion
        inserted, skipped = gusto_payroll(gusto_file)

        # Store counts in session
        request.session["gusto_inserted"] = inserted
        request.session["gusto_skipped"] = skipped

        return redirect("gusto_upload_success")

    return render(request, "clinic_dash_pro/upload_gusto.html")


def gusto_upload_success(request):
    inserted = request.session.get("gusto_inserted", 0)
    skipped = request.session.get("gusto_skipped", 0)

    count = GustoPayroll.objects.count()

    if count > 0:
        start = GustoPayroll.objects.earliest(
            "payroll_period_start").payroll_period_start
        end = GustoPayroll.objects.latest(
            "payroll_period_end").payroll_period_end
    else:
        start = end = None

    return render(request, "clinic_dash_pro/gusto_upload_success.html", {
        "count": count,
        "start": start,
        "end": end,
        "inserted": inserted,
        "skipped": skipped,
    })
