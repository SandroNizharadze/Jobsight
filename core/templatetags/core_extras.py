from django import template

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
    Removes trailing zeros from decimal values
    Example: 500.00 becomes 500, 500.50 remains 500.5
    Usage: {{ value|remove_trailing_zeros }}
    """
    if value is None:
        return value
        
    try:
        # Convert to string and check if it's a decimal with .00
        str_value = str(value)
        if str_value.endswith('.00'):
            return int(float(str_value))
        # For other decimal values, remove trailing zeros
        if '.' in str_value:
            return str_value.rstrip('0').rstrip('.') if '.' in str_value else str_value
        return value
    except (ValueError, TypeError):
        return value 