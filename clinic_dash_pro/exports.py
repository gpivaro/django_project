# exports.py
import pandas as pd
from django.http import HttpResponse
from django.apps import apps
from datetime import datetime

import pandas as pd


def sanitize_dataframe(df):
    """Convert tz-aware datetimes to naive, and Periods to strings."""
    for col in df.columns:
        # Convert pandas Period → string
        if isinstance(df[col].dtype, pd.PeriodDtype):
            df[col] = df[col].astype(str)

        # Convert timezone-aware datetimes → naive
        if pd.api.types.is_datetime64tz_dtype(df[col]):
            df[col] = df[col].dt.tz_convert(None)

        # Convert Python datetime/date objects → string-safe
        if df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: x.replace(tzinfo=None) if hasattr(
                    x, "tzinfo") and x.tzinfo else x
            )

    return df


def build_filename(name, ext):
    """Normalize name + add timestamp + extension."""
    safe_name = name.replace(" ", "_").lower()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return f"{safe_name}_{timestamp}.{ext}"


def export_csv(request, model_name):
    Model = apps.get_model("clinic_dash_pro", model_name)
    qs = Model.objects.all().values()
    df = pd.DataFrame(list(qs))

    filename = build_filename(model_name, "csv")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    df.to_csv(path_or_buf=response, index=False)
    return response


def export_excel(request, model_name):
    Model = apps.get_model("clinic_dash_pro", model_name)
    qs = Model.objects.all().values()
    df = pd.DataFrame(list(qs))

    df = sanitize_dataframe(df)

    filename = build_filename(model_name, "xlsx")

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    return response


def export_df_csv(request):
    rows = request.session.get("df_export", [])
    fields = request.session.get("df_fields", [])
    df = pd.DataFrame(rows, columns=fields)

    # Use page title if provided, otherwise fallback
    title = request.GET.get("title", "dataframe")
    filename = build_filename(title, "csv")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    df.to_csv(path_or_buf=response, index=False)
    return response


def export_df_excel(request):
    rows = request.session.get("df_export", [])
    fields = request.session.get("df_fields", [])
    df = pd.DataFrame(rows, columns=fields)

    title = request.GET.get("title", "dataframe")
    filename = build_filename(title, "xlsx")

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    return response
