# Generated manually

from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration ensures compatibility with previous migrations that used CKEditor 4.
    Since we've removed the CKEditor 4 package, we need to make sure migrations don't fail.
    """

    dependencies = [
        ('core', '0052_fix_ckeditor_encoding'),
    ]

    operations = [
        # No operations needed - this is just a marker migration to ensure the migration history
        # is consistent after removing CKEditor 4
    ] 