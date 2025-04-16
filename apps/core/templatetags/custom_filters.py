# apps/core/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the arg."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''  # Return empty string for invalid inputs