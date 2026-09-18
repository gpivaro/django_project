# clinic_dash_pro\templatetags\format_extras.py

from django import template
register = template.Library()


@register.filter
def fmt_date(value):
    return value.strftime("%Y-%m-%d") if value else ""


@register.filter
def fmt_currency(value):
    return f"${value:,.2f}" if value is not None else ""


@register.filter
def currency(value):
    """Format numbers as currency: $1,234.56"""
    try:
        value = float(value)
        return f"${value:,.2f}"
    except (TypeError, ValueError):
        return value
