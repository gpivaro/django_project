# getattr_extras.py


from django import template

register = template.Library()


@register.filter
def get_field(obj, attr):
    # Support dict rows (DataFrame)
    if isinstance(obj, dict):
        return obj.get(attr, "")

    # Support Django model instances
    return getattr(obj, attr, "")
