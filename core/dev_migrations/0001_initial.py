from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoftDeletionModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('jobseeker', 'Job Seeker'), ('employer', 'Employer')], max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('is_email_verified', models.BooleanField(default=False)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('cv', models.FileField(blank=True, null=True, upload_to='cvs/')),
                ('desired_field', models.CharField(blank=True, max_length=100, null=True)),
                ('field_experience', models.CharField(blank=True, max_length=100, null=True)),
                ('visible_to_employers', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='EmployerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('company_website', models.URLField(blank=True, null=True)),
                ('company_description', models.TextField(blank=True, null=True)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('company_size', models.CharField(blank=True, max_length=50, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('has_cv_database_access', models.BooleanField(default=False)),
                ('show_phone_number', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employer_profile', to='core.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='RejectionReason',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobListing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('posted_at', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('premium_level', models.IntegerField(default=0)),
                ('view_count', models.IntegerField(default=0)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_listings', to='core.employerprofile')),
            ],
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_letter', models.TextField(blank=True, null=True)),
                ('cv', models.FileField(upload_to='cvs/')),
                ('applied_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('interview', 'Interview'), ('rejected', 'Rejected'), ('hired', 'Hired')], default='pending', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='core.joblisting')),
                ('rejection_reason', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.rejectionreason')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='auth.user')),
            ],
        ),
    ] 