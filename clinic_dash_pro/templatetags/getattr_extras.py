# getattr_extras.py

from django import template
register = template.Library()


@register.filter(name="get_field")
def get_field(obj, attr):
    return getattr(obj, attr)
