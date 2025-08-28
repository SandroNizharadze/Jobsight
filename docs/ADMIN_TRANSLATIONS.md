# Admin-Controlled Translation System

This document describes the admin-controlled translation system implemented for pricing packages and other content in the Jobsight application.

## Overview

The translation system allows administrators to manage translations directly through the Django admin interface, without requiring code changes or developer intervention. This is particularly useful for content that needs frequent updates or is managed by non-technical staff.

## Supported Models

The following models now support admin-controlled translations:

### 1. PricingPackage
- **Fields**: `name`, `description`
- **Languages**: Georgian (ka), English (en)
- **Admin Interface**: Inline translations within the PricingPackage admin

### 2. PricingFeature
- **Fields**: `text`
- **Languages**: Georgian (ka), English (en)
- **Admin Interface**: Inline translations within the PricingFeature admin

### 3. ComparisonTable
- **Fields**: `title`, `subtitle`
- **Languages**: Georgian (ka), English (en)
- **Admin Interface**: Inline translations within the ComparisonTable admin

### 4. ComparisonRow
- **Fields**: `feature_name`, `standard_value`, `premium_value`, `premium_plus_value`
- **Languages**: Georgian (ka), English (en)
- **Admin Interface**: Inline translations within the ComparisonRow admin

## How to Use

### For Administrators

1. **Access the Admin Interface**
   - Go to `/admin/` and log in with admin credentials
   - Navigate to the relevant model (e.g., "Pricing Packages")

2. **Add/Edit Translations**
   - When editing a pricing package, you'll see a "Translations" section
   - Add translations for English language
   - Leave fields blank if no translation is needed (will fall back to original Georgian text)

3. **Manage Features**
   - Features have their own admin section with inline translations
   - Each feature can be translated independently

### For Developers

#### Using Template Tags

The system provides template tags for easy access to translated content:

```html
{% load pricing_tags %}

<!-- Get translated package name -->
<h3>{% get_translated_package_name package %}</h3>

<!-- Get translated package description -->
<p>{% get_translated_package_description package %}</p>

<!-- Get translated feature text -->
<span>{% get_translated_feature_text feature %}</span>

<!-- Get translated comparison table title -->
<h2>{% get_translated_comparison_title table %}</h2>

<!-- Get translated row values -->
<td>{% get_translated_row_value row 'standard' %}</td>
<td>{% get_translated_row_value row 'premium' %}</td>
<td>{% get_translated_row_value row 'premium_plus' %}</td>
```

#### Using Python Code

You can also access translations directly in Python code:

```python
# Get translated package name
package_name = package.get_translated_name('en')  # English
package_name = package.get_translated_name('ka')  # Georgian (default)

# Get translated feature text
feature_text = feature.get_translated_text('en')

# Get translated comparison table title
table_title = table.get_translated_title('en')
```

## Language Codes

- `ka` - Georgian (default language)
- `en` - English

## Fallback Behavior

If a translation is not available for a specific language:
1. The system will return the original Georgian text
2. No errors will be thrown
3. The application will continue to function normally

## Adding New Languages

To add support for additional languages:

1. **Update the Model Choices**
   - Add the new language code to `LANGUAGE_CHOICES` in the relevant translation model
   - Example: `('fr', _('French'))`

2. **Create Migration**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Update Template Tags** (if needed)
   - Modify the template tags to handle the new language

## Management Commands

### Create Initial Translations

To populate the translation tables with initial data:

```bash
python manage.py create_pricing_translations
```

This command will:
- Create English translations for all existing pricing packages
- Create translations for all existing features
- Create translations for comparison tables and rows

### Load Initial Data

To create the base pricing packages and features:

```bash
python manage.py load_initial_data
```

## Best Practices

1. **Always Provide Georgian Text**
   - Georgian text serves as the fallback for missing translations
   - Ensure all Georgian content is properly written and reviewed

2. **Keep Translations Updated**
   - Regularly review and update translations
   - Ensure consistency across different languages

3. **Use Meaningful Translation Keys**
   - When adding new translatable content, use clear, descriptive field names
   - Consider the context in which the text will be used

4. **Test All Languages**
   - After making changes, test the application in all supported languages
   - Ensure no text appears in the wrong language

## Troubleshooting

### Common Issues

1. **Translations Not Showing**
   - Check if translation records exist in the database
   - Verify the language code is correct
   - Ensure the template is using the correct template tags

2. **Fallback to Georgian**
   - This is normal behavior when translations are missing
   - Add the missing translations through the admin interface

3. **Admin Interface Not Loading**
   - Check if migrations have been applied
   - Verify the admin configuration is correct

### Debugging

To debug translation issues:

1. **Check Database**
   ```python
   # In Django shell
   from core.models import PricingPackageTranslation
   PricingPackageTranslation.objects.filter(package__package_type='standard')
   ```

2. **Check Template Context**
   - Ensure the correct objects are being passed to templates
   - Verify template tags are loaded correctly

3. **Check Language Settings**
   - Verify Django's language settings
   - Check if the language switcher is working correctly

## Future Enhancements

Potential improvements to the translation system:

1. **Bulk Translation Import/Export**
   - CSV import/export for translations
   - Translation memory system

2. **Translation Workflow**
   - Translation approval process
   - Translation status tracking

3. **Additional Content Types**
   - Blog posts
   - Static pages
   - User-facing messages

4. **Translation Analytics**
   - Track which translations are most used
   - Identify missing translations

## Support

For questions or issues with the translation system:

1. Check this documentation first
2. Review the admin interface configuration
3. Check the database for missing translation records
4. Contact the development team if issues persist
