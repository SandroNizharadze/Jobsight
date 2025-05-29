from django import template
from django.utils.translation import get_language, gettext
from django.utils.safestring import mark_safe
import re

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

@register.simple_tag(takes_context=True)
def lang_attr(context):
    """
    Returns the language attribute for the current language.
    Example usage: <span {% lang_attr %}>Text</span>
    """
    request = context.get('request')
    if request:
        return f'lang="{request.LANGUAGE_CODE}"'
    return f'lang="{get_language()}"'

@register.filter
def is_georgian(text):
    """
    Checks if the text contains Georgian characters
    Example usage: {% if text|is_georgian %}<span class="georgian-text">{{ text }}</span>{% endif %}
    """
    if not text:
        return False
    # Georgian Unicode range: U+10A0 to U+10FF
    return bool(re.search('[\u10A0-\u10FF]', str(text)))

@register.filter(is_safe=True)
def with_lang_class(text):
    """
    Adds appropriate language class based on text content
    Example usage: {{ text|with_lang_class }}
    """
    if not text:
        return text
    
    if re.search('[\u10A0-\u10FF]', str(text)):
        return mark_safe(f'<span class="georgian-text">{text}</span>')
    return text

@register.simple_tag
def trans_with_font(text):
    """
    Translates text and applies appropriate font class
    Example usage: {% trans_with_font "Hello" %}
    """
    translated = gettext(text)
    if re.search('[\u10A0-\u10FF]', translated):
        return mark_safe(f'<span class="georgian-text">{translated}</span>')
    return translated 