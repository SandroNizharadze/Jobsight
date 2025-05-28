from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import JobListing, UserProfile, EmployerProfile, JobApplication, SavedJob, RejectionReason
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
from core.models import PricingPackage, PricingFeature

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
                 'user_profile__user__email', 'created_at', 'deleted_at')

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
    resource_class = EmployerProfileResource
    list_display = ('company_name', 'get_employer_email', 'industry', 'company_size', 
                   'location', 'get_deleted_state')
    search_fields = ('company_name', 'user_profile__user__email')
    list_filter = ('company_size', 'industry', ('deleted_at', admin.EmptyFieldListFilter))
    actions = ['restore_selected']

    def get_employer_email(self, obj):
        return obj.user_profile.user.email
    get_employer_email.short_description = 'Employer Email'

@admin.register(JobListing)
class JobListingAdmin(SoftDeletionAdmin):
    resource_class = JobListingResource
    list_display = ('title', 'company', 'get_employer', 'salary_range', 'location', 
                   'category', 'experience', 'job_preferences', 'get_students_status',
                   'premium_level', 'posted_at', 'get_status', 'get_cv_count', 'get_expiration')
    list_filter = (('posted_at', DateRangeFilter), ('deleted_at', admin.EmptyFieldListFilter), 
                  'employer__company_name', 'location', 'category', 'experience', 
                  'job_preferences', 'considers_students', 'premium_level', 'status')
    search_fields = ('title', 'company', 'description', 'location')
    date_hierarchy = 'posted_at'
    actions = ['restore_selected', 'extend_expiration', 'mark_as_expired', 'reactivate_expired_jobs']

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
        elif obj.status == 'rejected':
            return format_html('<span style="color: red; font-weight: bold;">Rejected</span>')
        else:
            return obj.get_status_display()
    get_status.short_description = 'Status'
    
    def get_cv_count(self, obj):
        return obj.applications.count()
    get_cv_count.short_description = 'CV Count'

    def extend_expiration(self, request, queryset):
        """Extend the expiration date of selected jobs by 30 days"""
        count = 0
        for job in queryset:
            job.extend_expiration(days=30)
            count += 1
        self.message_user(request, f"Extended expiration for {count} jobs by 30 days.")
    extend_expiration.short_description = "Extend expiration by 30 days"
    
    def mark_as_expired(self, request, queryset):
        """Mark selected jobs as expired"""
        count = queryset.update(status='expired')
        self.message_user(request, f"Marked {count} jobs as expired.")
    mark_as_expired.short_description = "Mark selected jobs as expired"
    
    def reactivate_expired_jobs(self, request, queryset):
        """Reactivate expired jobs - change status to approved and extend by 30 days"""
        count = 0
        for job in queryset.filter(status='expired'):
            job.status = 'approved'
            job.extend_expiration(days=30)
            job.save()
            count += 1
        self.message_user(request, f"Reactivated {count} expired jobs.")
    reactivate_expired_jobs.short_description = "Reactivate expired jobs (extend by 30 days)"
    
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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'user_name', 'role', 'has_cv', 'desired_field_display', 'field_experience_display', 'visible_to_employers')
    list_filter = ('role', 'visible_to_employers', 'desired_field', 'field_experience')
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