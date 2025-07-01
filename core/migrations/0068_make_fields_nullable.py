from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_alter_joblisting_last_extended_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joblisting',
            name='fields',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='joblisting',
            name='interests',
            field=models.CharField(max_length=255, blank=True, null=True),
        ),
    ] 