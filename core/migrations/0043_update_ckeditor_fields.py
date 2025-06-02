# Generated manually on 2024-06-02

from django.db import migrations
from django_ckeditor_5.fields import CKEditor5Field


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_alter_blogpost_content_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='content',
            field=CKEditor5Field(verbose_name='კონტენტი'),
        ),
        migrations.AlterField(
            model_name='employerprofile',
            name='company_description',
            field=CKEditor5Field(blank=True, verbose_name='კომპანიის აღწერა'),
        ),
        migrations.AlterField(
            model_name='joblisting',
            name='description',
            field=CKEditor5Field(verbose_name='ვაკანსიის აღწერა'),
        ),
    ] 