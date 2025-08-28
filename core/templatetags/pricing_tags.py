from django import template
from django.utils.translation import get_language
from core.models import (
    PricingPackage, PricingFeature, ComparisonTable, ComparisonRow
)

register = template.Library()

@register.simple_tag
def get_translated_package_name(package, language_code=None):
    """Get translated package name for the specified language"""
    if not language_code:
        language_code = get_language()
    
    try:
        return package.get_translated_name(language_code)
    except:
        return package.name

@register.simple_tag
def get_translated_package_description(package, language_code=None):
    """Get translated package description for the specified language"""
    if not language_code:
        language_code = get_language()
    
    try:
        return package.get_translated_description(language_code)
    except:
        return package.description

@register.simple_tag
def get_translated_feature_text(feature, language_code=None):
    """Get translated feature text for the specified language"""
    if not language_code:
        language_code = get_language()
    
    try:
        return feature.get_translated_text(language_code)
    except:
        return feature.text

@register.simple_tag
def get_translated_comparison_title(table, language_code=None):
    """Get translated comparison table title for the specified language"""
    if not language_code:
        language_code = get_language()
    
    try:
        return table.get_translated_title(language_code)
    except:
        return table.title

@register.simple_tag
def get_translated_comparison_subtitle(table, language_code=None):
    """Get translated comparison table subtitle for the specified language"""
    if not language_code:
        language_code = get_language()
    
    try:
        return table.get_translated_subtitle(language_code)
    except:
        return table.subtitle

@register.simple_tag
def get_translated_row_feature_name(row, language_code=None):
    """Get translated row feature name for the specified language"""
    if not language_code:
        language_code = get_language()
    
    try:
        return row.get_translated_feature_name(language_code)
    except:
        return row.feature_name

@register.simple_tag
def get_translated_row_value(row, package_type, language_code=None):
    """Get translated row value for the specified package type and language"""
    if not language_code:
        language_code = get_language()
    
    try:
        if package_type == 'standard':
            return row.get_translated_standard_value(language_code)
        elif package_type == 'premium':
            return row.get_translated_premium_value(language_code)
        elif package_type == 'premium_plus':
            return row.get_translated_premium_plus_value(language_code)
        else:
            return getattr(row, f'{package_type}_value', '')
    except:
        return getattr(row, f'{package_type}_value', '')
