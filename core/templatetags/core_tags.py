from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a template filter
    Example usage: {{ mydict|get_item:key_var }}
    """
    if not dictionary:
        return ''
    return dictionary.get(key, key) 