from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary by key
    Usage: {{ mydict|get_item:key }}
    """
    return dictionary.get(key, '')

@register.filter
def remove_trailing_zeros(value):
    """
    Remove trailing zeros from a decimal number.
    """
    if isinstance(value, (int, float, Decimal)):
        value = str(value)
    if '.' in value:
        return value.rstrip('0').rstrip('.') if '.' in value else value
    return value

@register.filter
def filter_by_text(queryset, text):
    """
    Filter a queryset of PricingFeature objects by their text field.
    """
    return [item for item in queryset if item.text == text] 