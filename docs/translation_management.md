# Translation Management

This document explains how to manage translations in the Jobsy application, particularly for dynamic content managed through the Django admin interface.

## Overview

The application supports two types of translations:

1. **Static translations**: Managed through Django's built-in i18n system using `.po` files
2. **Dynamic translations**: Managed through the database for content that is controlled via the Django admin interface

## Dynamic Content Translation

For dynamic content like pricing packages, features, and comparison tables, translations are stored in the database in separate translation models:

- `PricingPackageTranslation`
- `PricingFeatureTranslation`
- `ComparisonTableTranslation`
- `ComparisonRowTranslation`

These translations can be managed directly through the Django admin interface or updated using management commands.

## Production Translation Update

To update translations in a production environment, use the provided script:

```bash
./update_translations.sh
```

This script runs the `update_production_translations` management command, which:

1. Creates translation records for any missing entries
2. Updates existing translations based on a predefined mapping

### Manual Update via Django Admin

Administrators can also update translations directly through the Django admin interface:

1. Log in to the Django admin
2. Navigate to the respective model (e.g., Comparison Rows)
3. Edit a row
4. Scroll down to the "Translations" inline section
5. Update the translations for each language

### Adding New Translations

If you need to add translations for new content:

1. Add the Georgian content through the Django admin interface
2. Run the translation update script to create initial English translations
3. Verify and adjust the translations as needed through the admin interface

## Translation Fallback

If a translation is not available for a specific language:

1. The system will attempt to use the translation from the database
2. If no database translation exists, it will fall back to the original content (typically in Georgian)
3. For some specific content, custom template tags (`pricing_tags.py`) provide additional fallback mechanisms

## Supported Languages

Currently, the application supports:

- Georgian (`ka`)
- English (`en`)

## Adding Support for New Languages

To add support for a new language:

1. Add the language to `LANGUAGES` in settings.py
2. Update the `LANGUAGE_CHOICES` in each translation model
3. Create initial translations using management commands or the admin interface
