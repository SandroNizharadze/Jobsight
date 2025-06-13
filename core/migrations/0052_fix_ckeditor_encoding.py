# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration fixes encoding issues with CKEditor5 fields by ensuring
    proper database configuration for Georgian character support.
    """

    dependencies = [
        ('core', '0051_remove_jobapplication_cv_viewed_and_more'),
    ]

    operations = [
        # First, explicitly set the field to TextField to ensure clean state
        migrations.RunSQL(
            sql="""
            ALTER TABLE core_employerprofile 
            ALTER COLUMN company_description TYPE text 
            USING company_description::text;
            """,
            reverse_sql="""
            -- No reverse operation needed
            """
        ),
        
        # Ensure proper encoding for the text field
        migrations.RunSQL(
            sql="""
            -- Set client encoding to UTF-8 to ensure proper handling of Georgian characters
            SET client_encoding = 'UTF8';
            """,
            reverse_sql="""
            -- No reverse operation needed
            """
        ),
    ] 