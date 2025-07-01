from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import JobListing, UserProfile, EmployerProfile, JobApplication, SavedJob, RejectionReason, PricingPackage, PricingFeature, ComparisonTable, ComparisonRow, BlogPost, BlogCategory, BlogPostCategory, EmployerNotification
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export import resources
from rangefilter.filters import DateRangeFilter
from django.utils.html import format_html
from django.db.models import Q
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django_ckeditor_5.widgets import CKEditor5Widget
from core.models import StaticPage
from datetime import timedelta
from django.utils import timezone

# Add a custom form for BlogPost with explicit CKEditorWidget
class BlogPostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = BlogPost
        fields = '__all__'

# Add a custom form for JobListing with explicit CKEditorWidget
class JobListingAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = JobListing
        fields = '__all__'

# Add a custom form for EmployerProfile with explicit CKEditorWidget
class EmployerProfileAdminForm(forms.ModelForm):
    company_description = forms.CharField(widget=CKEditorWidget(), required=False)
    
    class Meta:
        model = EmployerProfile
        fields = '__all__'

# Add a historical data view to the admin site
@staff_member_required
def historical_data_view(request):
    # Get all jobs, including deleted ones
    all_jobs = JobListing.all_objects.all().order_by('-posted_at')
    active_jobs = JobListing.objects.all().count()
    deleted_jobs = all_jobs.filter(deleted_at__isnull=False).count()
    total_jobs = all_jobs.count()
    
    # Get all employers, including deleted ones
    all_employers = EmployerProfile.all_objects.all().order_by('-created_at')
    active_employers = EmployerProfile.objects.all().count()
    deleted_employers = all_employers.filter(deleted_at__isnull=False).count()
    total_employers = all_employers.count()
    
    # Get all applications, including those for deleted jobs
    all_applications = JobApplication.objects.all().order_by('-applied_at')
    applications_with_deleted_jobs = all_applications.filter(job__isnull=True).count()
    total_applications = all_applications.count()
    
    # Get all saved jobs, including those for deleted jobs
    all_saved_jobs = SavedJob.objects.all().order_by('-saved_at')
    saved_with_deleted_jobs = all_saved_jobs.filter(job__isnull=True).count()
    total_saved = all_saved_jobs.count()
    
    context = {
        'title': 'Historical Data',
        'all_jobs': all_jobs[:100],  # Limit to the first 100 for performance
        'active_jobs': active_jobs,
        'deleted_jobs': deleted_jobs,
        'total_jobs': total_jobs,
        'all_employers': all_employers[:100],  # Limit to the first 100 for performance
        'active_employers': active_employers,
        'deleted_employers': deleted_employers,
        'total_employers': total_employers,
        'applications_with_deleted_jobs': applications_with_deleted_jobs,
        'total_applications': total_applications,
        'saved_with_deleted_jobs': saved_with_deleted_jobs,
        'total_saved': total_saved,
    }
    return TemplateResponse(request, 'admin/historical_data.html', context)

# Resources for model export
class JobListingResource(resources.ModelResource):
    class Meta:
        model = JobListing
        fields = ('id', 'title', 'company', 'description', 'salary_min', 'salary_max', 
                  'salary_type', 'category', 'location', 'posted_at', 'experience',
                  'job_preferences', 'considers_students', 'status', 'premium_level',
                  'deleted_at')

class EmployerProfileResource(resources.ModelResource):
    class Meta:
        model = EmployerProfile
        fields = ('id', 'company_name', 'company_id', 'phone_number', 'company_website', 
                 'company_description', 'company_size', 'industry', 'location', 
                 'user_profile__user__email', 'has_cv_database_access', 'created_at', 'deleted_at')

class JobApplicationResource(resources.ModelResource):
    class Meta:
        model = JobApplication
        fields = ('id', 'job__title', 'job__company', 'job_title', 'job_company',
                 'user__email', 'guest_name', 'guest_email', 'status', 'applied_at')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ('role', 'profile_picture', 'cv', 'desired_field', 'field_experience', 'visible_to_employers')

class CustomUserAdmin(UserAdmin, ImportExportActionModelAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'get_role', 'get_company')
    actions = ['make_employer']

    def get_role(self, obj):
        try:
            role = obj.userprofile.role
            # Manual mapping instead of relying on get_role_display
            role_display = {
                'candidate': 'Candidate',
                'employer': 'Employer',
                'admin': 'Admin',
            }.get(role, role)
            return role_display
        except UserProfile.DoesNotExist:
            return '-'
    get_role.short_description = 'Role'

    def get_company(self, obj):
        try:
            if obj.userprofile.role == 'employer':
                return obj.userprofile.employer_profile.company_name
            return '-'
        except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist):
            return '-'
    get_company.short_description = 'Company'

    def make_employer(self, request, queryset):
        for user in queryset:
            try:
                profile = user.userprofile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            
            profile.role = 'employer'
            profile.save()  # This will automatically create the EmployerProfile
        
        self.message_user(request, f"Successfully made {queryset.count()} users employers.")
    make_employer.short_description = "Make selected users employers"

# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class SoftDeletionAdmin(ImportExportModelAdmin):
    """Base admin class for models with soft deletion"""
    
    def get_queryset(self, request):
        # Override to show all objects, including deleted ones
        qs = self.model.all_objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    
    def get_deleted_state(self, obj):
        if obj.deleted_at:
            return format_html('<span style="color: red;">Deleted</span>')
        return format_html('<span style="color: green;">Active</span>')
    get_deleted_state.short_description = 'Status'
    
    def restore_selected(self, request, queryset):
        count = queryset.filter(deleted_at__isnull=False).count()
        for obj in queryset.filter(deleted_at__isnull=False):
            obj.deleted_at = None
            obj.save()
        
        if count:
            self.message_user(request, f"Successfully restored {count} records.")
        else:
            self.message_user(request, "No deleted records were selected.")
    restore_selected.short_description = "Restore selected records"

@admin.register(EmployerProfile)
class EmployerProfileAdmin(SoftDeletionAdmin):
    form = EmployerProfileAdminForm
    resource_class = EmployerProfileResource
    list_display = ('company_name', 'get_employer_email', 'industry', 'company_size', 
                   'location', 'has_cv_database_access', 'get_deleted_state')
    search_fields = ('company_name', 'user_profile__user__email')
    list_filter = ('company_size', 'industry', 'has_cv_database_access', ('deleted_at', admin.EmptyFieldListFilter))
    actions = ['restore_selected']

    def get_employer_email(self, obj):
        return obj.user_profile.user.email
    get_employer_email.short_description = 'Employer Email'

@admin.register(JobListing)
class JobListingAdmin(SoftDeletionAdmin):
    form = JobListingAdminForm
    resource_class = JobListingResource
    list_display = ('title', 'company', 'get_employer', 'salary_range', 'location', 
                   'category', 'experience', 'job_preferences', 'get_students_status',
                   'premium_level', 'posted_at', 'get_status', 'get_cv_count', 'get_expiration')
    list_filter = (('posted_at', DateRangeFilter), ('deleted_at', admin.EmptyFieldListFilter), 
                  'employer__company_name', 'location', 'category', 'experience', 
                  'job_preferences', 'considers_students', 'premium_level', 'status')
    search_fields = ('title', 'company', 'description', 'location')
    date_hierarchy = 'posted_at'
    actions = ['restore_selected', 'extend_expiration', 'extend_expiration_no_bump', 'mark_as_expired', 'reactivate_expired_jobs']

    def salary_range(self, obj):
        if obj.salary_min and obj.salary_max:
            # Format values to remove trailing zeros
            min_val = str(obj.salary_min).rstrip('0').rstrip('.') if '.' in str(obj.salary_min) else obj.salary_min
            max_val = str(obj.salary_max).rstrip('0').rstrip('.') if '.' in str(obj.salary_max) else obj.salary_max
            return f"{min_val} - {max_val} ₾ {obj.salary_type}"
        elif obj.salary_min:
            min_val = str(obj.salary_min).rstrip('0').rstrip('.') if '.' in str(obj.salary_min) else obj.salary_min
            return f"{min_val} ₾ {obj.salary_type}"
        elif obj.salary_max:
            max_val = str(obj.salary_max).rstrip('0').rstrip('.') if '.' in str(obj.salary_max) else obj.salary_max
            return f"{max_val} ₾ {obj.salary_type}"
        return '-'
    salary_range.short_description = 'Salary'

    def get_employer(self, obj):
        if obj.employer:
            return obj.employer.user_profile.user.email
        return '-'
    get_employer.short_description = 'Posted by'
    
    def get_students_status(self, obj):
        if obj.considers_students:
            return format_html('<span style="color: green; font-weight: bold;">✓ {}</span>', _('კი'))
        else:
            return format_html('<span style="color: #666;">✗ {}</span>', _('არა'))
    get_students_status.short_description = _('სტუდენტური')
    
    def get_status(self, obj):
        if obj.deleted_at:
            return format_html('<span style="color: red; font-weight: bold;">Deleted</span>')
        elif obj.status == 'approved':
            return format_html('<span style="color: green; font-weight: bold;">Active</span>')
        elif obj.status == 'pending_review':
            return format_html('<span style="color: orange; font-weight: bold;">In Review</span>')
        elif obj.status == 'extended_review':
            return format_html('<span style="color: purple; font-weight: bold;">Extended (Under Review)</span>')
        elif obj.status == 'rejected':
            return format_html('<span style="color: red; font-weight: bold;">Rejected</span>')
        else:
            return obj.get_status_display()
    get_status.short_description = 'Status'
    
    def get_cv_count(self, obj):
        return obj.applications.count()
    get_cv_count.short_description = 'CV Count'

    def save_model(self, request, obj, form, change):
        """
        Override save_model to grant CV database access when premium+ job is approved
        and create notifications for status changes
        """
        # Check if this is a status change
        if change and 'status' in form.changed_data:
            old_job = JobListing.objects.get(pk=obj.pk)
            old_status = old_job.status
            new_status = obj.status
            
            # If status changed from pending_review/extended_review to approved/rejected
            if old_status in ['pending_review', 'extended_review'] and new_status in ['approved', 'rejected']:
                # Create notification for the employer
                from core.repositories.notification_repository import NotificationRepository
                
                if new_status == 'approved':
                    message = f"Your job '{obj.title}' has been approved and is now live."
                else:  # rejected
                    message = f"Your job '{obj.title}' has been rejected. Please check admin feedback."
                
                NotificationRepository.create_job_status_notification(
                    employer_profile=obj.employer,
                    job=obj,
                    message=message
                )
        
        # Check if this is a status change to 'approved' for a premium+ job
        if 'status' in form.changed_data and obj.status == 'approved' and obj.premium_level == 'premium_plus':
            # Grant CV database access to the employer
            employer_profile = obj.employer
            if employer_profile and not employer_profile.has_cv_database_access:
                employer_profile.has_cv_database_access = True
                employer_profile.save()
                self.message_user(request, f"CV database access granted to {employer_profile.company_name}", level='success')
        
        # Call the parent class save_model method to save the job
        super().save_model(request, obj, form, change)

    def extend_expiration(self, request, queryset):
        """Extend the expiration date of selected jobs by 30 days"""
        count = 0
        for job in queryset:
            # If job is expired, also update its status
            if job.status == 'expired':
                job.status = 'approved'
                job.expires_at = timezone.now() + timedelta(days=30)
                job.last_extended_at = timezone.now()  # Set last extended time
                job.save(update_fields=['expires_at', 'status', 'last_extended_at'])
            else:
                job.extend_expiration(days=30, bump_to_top=True)
            count += 1
        self.message_user(request, f"Extended expiration for {count} jobs by 30 days and bumped to top.")
    extend_expiration.short_description = "Extend expiration by 30 days and bump to top"
    
    def extend_expiration_no_bump(self, request, queryset):
        """Extend the expiration date of selected jobs by 30 days without bumping to top"""
        count = 0
        for job in queryset:
            # If job is expired, also update its status
            if job.status == 'expired':
                job.status = 'approved'
                job.expires_at = timezone.now() + timedelta(days=30)
                job.save(update_fields=['expires_at', 'status'])
            else:
                job.extend_expiration(days=30, bump_to_top=False)
            count += 1
        self.message_user(request, f"Extended expiration for {count} jobs by 30 days without changing position.")
    extend_expiration_no_bump.short_description = "Extend expiration by 30 days (keep position)"
    
    def mark_as_expired(self, request, queryset):
        """Mark selected jobs as expired"""
        count = queryset.update(status='expired')
        self.message_user(request, f"Marked {count} jobs as expired.")
    mark_as_expired.short_description = "Mark selected jobs as expired"
    
    def reactivate_expired_jobs(self, request, queryset):
        """Reactivate expired or extended jobs - change status to approved and extend by 30 days"""
        count = 0
        for job in queryset.filter(status__in=['expired', 'extended_review']):
            job.status = 'approved'
            job.expires_at = timezone.now() + timedelta(days=30)
            job.last_extended_at = timezone.now()  # Set last extended time to bump to top
            job.save(update_fields=['status', 'expires_at', 'last_extended_at'])
            count += 1
        self.message_user(request, f"Reactivated {count} expired or extended jobs.")
    reactivate_expired_jobs.short_description = "Reactivate expired or extended jobs (extend by 30 days)"
    
    def get_expiration(self, obj):
        if obj.expires_at:
            days = obj.days_until_expiration()
            if days is not None:
                if days <= 0:
                    return format_html('<span style="color: red; font-weight: bold;">Expired</span>')
                elif days <= 7:
                    return format_html('<span style="color: orange; font-weight: bold;">{} days left</span>', days)
                else:
                    return format_html('{} days left', days)
        return '-'
    get_expiration.short_description = 'Expiration'

@admin.register(JobApplication)
class JobApplicationAdmin(ImportExportModelAdmin):
    resource_class = JobApplicationResource
    list_display = ('get_job_title', 'get_company', 'get_applicant', 'status', 'applied_at', 'get_rejection_reasons')
    list_filter = (('applied_at', DateRangeFilter), 'status', 'rejection_reasons')
    search_fields = ('job_title', 'job_company', 'job__title', 'job__company', 'user__email', 'guest_name', 'guest_email')
    date_hierarchy = 'applied_at'
    filter_horizontal = ('rejection_reasons',)
    
    def get_job_title(self, obj):
        if obj.job:
            return obj.job.title
        return obj.job_title or "Deleted Job"
    get_job_title.short_description = 'Job Title'
    
    def get_company(self, obj):
        if obj.job:
            return obj.job.company
        return obj.job_company or "Deleted Company"
    get_company.short_description = 'Company'
    
    def get_applicant(self, obj):
        if obj.user:
            return obj.user.email
        return f"{obj.guest_name} ({obj.guest_email})"
    get_applicant.short_description = 'Applicant'
    
    def get_rejection_reasons(self, obj):
        if obj.status == 'რეზერვი' and obj.rejection_reasons.exists():
            reasons = ", ".join([reason.get_name_display() for reason in obj.rejection_reasons.all()])
            return format_html('<span style="color: #d9534f;">{}</span>', reasons)
        return "-"
    get_rejection_reasons.short_description = 'Rejection Reasons'

@admin.register(SavedJob)
class SavedJobAdmin(ImportExportModelAdmin):
    list_display = ('get_user_email', 'get_job_title', 'get_company', 'saved_at')
    list_filter = (('saved_at', DateRangeFilter), 'user')
    search_fields = ('job_title', 'job_company', 'job__title', 'job__company', 'user__email')
    date_hierarchy = 'saved_at'
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User'
    
    def get_job_title(self, obj):
        if obj.job:
            return obj.job.title
        return obj.job_title or "Deleted Job"
    get_job_title.short_description = 'Job Title'
    
    def get_company(self, obj):
        if obj.job:
            return obj.job.company
        return obj.job_company or "Deleted Company"
    get_company.short_description = 'Company'

class RejectionReasonAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(RejectionReason, RejectionReasonAdmin)

class PricingFeatureInline(admin.TabularInline):
    model = PricingFeature
    extra = 1
    fields = ('text', 'is_included', 'display_order')

@admin.register(PricingPackage)
class PricingPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'get_price_display', 'is_popular', 'is_free', 'has_discount_badge', 'is_active', 'display_order')
    list_filter = ('package_type', 'is_active', 'is_popular', 'is_free', 'has_discount_badge')
    search_fields = ('name', 'description')
    ordering = ('display_order', 'package_type')
    inlines = [PricingFeatureInline]
    fieldsets = (
        (None, {
            'fields': ('package_type', 'name', 'description', 'display_order')
        }),
        (_('Pricing Options'), {
            'fields': ('current_price', 'original_price', 'is_free')
        }),
        (_('Display Options'), {
            'fields': ('is_popular', 'is_active', 'has_discount_badge')
        }),
    )
    
    def get_price_display(self, obj):
        if obj.is_free:
            return _("Free")
        if obj.has_discount():
            return f"{obj.original_price} → {obj.current_price}"
        return f"{obj.current_price}"
    get_price_display.short_description = _("Price")

class ComparisonRowInline(admin.TabularInline):
    model = ComparisonRow
    extra = 1
    fields = ('feature_name', 'display_type', 'display_order', 
              'standard_value', 'standard_included',
              'premium_value', 'premium_included', 
              'premium_plus_value', 'premium_plus_included')

@admin.register(ComparisonTable)
class ComparisonTableAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title', 'subtitle')
    inlines = [ComparisonRowInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'is_active')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_name', 'role', 'has_cv', 'desired_field_display', 'field_experience_display', 'visible_to_employers', 'email_notifications')
    list_filter = ('role', 'visible_to_employers', 'desired_field', 'field_experience', 'email_notifications')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'desired_field', 'field_experience')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    user_name.short_description = 'Name'
    
    def has_cv(self, obj):
        return bool(obj.cv)
    has_cv.boolean = True
    has_cv.short_description = 'Has CV'
    
    def desired_field_display(self, obj):
        if obj.desired_field:
            for field_value, field_display in JobListing.CATEGORY_CHOICES:
                if field_value == obj.desired_field:
                    return field_display
        return '-'
    desired_field_display.short_description = 'Desired Field'
    
    def field_experience_display(self, obj):
        if obj.field_experience:
            for exp_value, exp_display in JobListing.EXPERIENCE_CHOICES:
                if exp_value == obj.field_experience:
                    return exp_display
        return '-'
    field_experience_display.short_description = 'Experience Level'

class BlogPostCategoryInline(admin.TabularInline):
    model = BlogPostCategory
    extra = 1

class BlogPostAdmin(SoftDeletionAdmin):
    form = BlogPostAdminForm
    list_display = ('title', 'author', 'status', 'published_at', 'view_count', 'get_deleted_state')
    list_filter = ('status', ('published_at', DateRangeFilter), ('deleted_at', admin.EmptyFieldListFilter))
    search_fields = ('title', 'content', 'excerpt', 'meta_description', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    actions = ['restore_selected', 'publish_posts', 'unpublish_posts']
    inlines = [BlogPostCategoryInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status', 'content')
        }),
        (_('SEO Options'), {
            'fields': ('excerpt', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
        (_('Media'), {
            'fields': ('featured_image',)
        }),
        (_('Advanced options'), {
            'fields': ('allow_comments', 'view_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )
    
    def publish_posts(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f"{updated} posts have been published.")
    publish_posts.short_description = "Mark selected posts as published"
    
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} posts have been unpublished.")
    unpublish_posts.short_description = "Mark selected posts as draft"
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'

# Register the blog models
admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type', 'last_updated')
    list_filter = ('page_type',)
    search_fields = ('title', 'content')
    readonly_fields = ('last_updated',)

class EmployerNotificationResource(resources.ModelResource):
    class Meta:
        model = EmployerNotification
        fields = ('id', 'employer_profile__company_name', 'job_title', 
                 'notification_type', 'message', 'is_read', 'created_at')

@admin.register(EmployerNotification)
class EmployerNotificationAdmin(ImportExportModelAdmin):
    resource_class = EmployerNotificationResource
    list_display = ('get_employer', 'job_title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', ('created_at', DateRangeFilter))
    search_fields = ('employer_profile__company_name', 'job_title', 'message')
    date_hierarchy = 'created_at'
    
    def get_employer(self, obj):
        return obj.employer_profile.company_name
    get_employer.short_description = 'Employer'
    get_employer.admin_order_field = 'employer_profile__company_name'