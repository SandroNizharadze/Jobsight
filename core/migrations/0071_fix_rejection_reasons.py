# Generated manually

from django.db import migrations, models
import re

def generate_unique_codes(apps, schema_editor):
    RejectionReason = apps.get_model('core', 'RejectionReason')
    
    # Get all existing rejection reasons
    reasons = list(RejectionReason.objects.all())
    
    # First, rename the name field to avoid unique constraint issues
    for i, reason in enumerate(reasons):
        # Generate a temporary unique name to avoid conflicts
        temp_name = f"temp_name_{i}_{reason.pk}"
        RejectionReason.objects.filter(pk=reason.pk).update(name=temp_name)
    
    # Now update each record with proper code and name
    for reason in reasons:
        original_name = reason.get_name_display() if hasattr(reason, 'get_name_display') else reason.name
        
        # Generate code from original name
        code = re.sub(r'\s+', '_', original_name.lower())
        code = re.sub(r'[^\w_]', '', code)
        
        # Ensure uniqueness
        base_code = code
        counter = 1
        while RejectionReason.objects.filter(code=code).exclude(pk=reason.pk).exists():
            code = f"{base_code}_{counter}"
            counter += 1
        
        # Update with original name and new code
        RejectionReason.objects.filter(pk=reason.pk).update(
            name=original_name,
            code=code
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_candidatenotification'),
    ]

    operations = [
        # First, make the name field non-unique to avoid conflicts
        migrations.AlterField(
            model_name='rejectionreason',
            name='name',
            field=models.CharField(max_length=255, verbose_name='მიზეზი'),
        ),
        # Add the code field with a non-conflicting default
        migrations.AddField(
            model_name='rejectionreason',
            name='code',
            field=models.CharField(default='temp_code', max_length=100, verbose_name='კოდი'),
            preserve_default=False,
        ),
        # Run the data migration to set unique codes
        migrations.RunPython(generate_unique_codes, migrations.RunPython.noop),
        # Now make the code field unique
        migrations.AlterField(
            model_name='rejectionreason',
            name='code',
            field=models.CharField(max_length=100, unique=True, verbose_name='კოდი'),
        ),
    ] 