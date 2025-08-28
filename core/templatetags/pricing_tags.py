from django import template
from django.utils.translation import get_language, gettext as _
from django.db.models import Q
from core.models import (
    PricingPackage, PricingFeature, ComparisonTable, ComparisonRow, ComparisonRowTranslation
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

@register.filter
def translate_feature(text):
    """Translate feature text directly using gettext"""
    return _(text)

@register.simple_tag
def get_feature_translation(feature_name, language_code=None):
    """Get translation for a feature name from ComparisonRowTranslation"""
    if not language_code:
        language_code = get_language()
    
    if language_code == 'ka':
        return feature_name
    
    try:
        # Find a row with this feature name
        row = ComparisonRow.objects.filter(feature_name=feature_name).first()
        if row:
            translation = ComparisonRowTranslation.objects.filter(
                row=row, 
                language_code=language_code
            ).first()
            if translation and translation.feature_name:
                return translation.feature_name
    except:
        pass
    
    # Fallback to gettext translation
    return _(feature_name)

@register.simple_tag
def get_value_translation(value, feature_name=None, language_code=None):
    """Get translation for a value from ComparisonRowTranslation"""
    if not language_code:
        language_code = get_language()
    
    if language_code == 'ka' or not value:
        return value
    
    try:
        # Try to find a translation for this value
        translations = ComparisonRowTranslation.objects.filter(
            Q(standard_value=value) | 
            Q(premium_value=value) | 
            Q(premium_plus_value=value),
            language_code=language_code
        )
        
        if translations.exists():
            for translation in translations:
                # Check which field matches
                if translation.row.standard_value == value:
                    return translation.standard_value
                elif translation.row.premium_value == value:
                    return translation.premium_value
                elif translation.row.premium_plus_value == value:
                    return translation.premium_plus_value
    except:
        pass
    
    # Fallback to gettext translation
    return _(value)