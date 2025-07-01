from core.views.employer_views.dashboard import employer_dashboard, employer_home
from core.views.employer_views.job_management import post_job, delete_job, extend_job, restore_job, deleted_jobs
from core.views.employer_views.application_management import update_application_status, application_detail
from core.views.employer_views.cv_database import cv_database
from core.views.employer_views.profile import company_profile, get_job_details
from core.views.employer_views.notification_views import mark_notifications_as_read, mark_job_notifications_as_read, mark_notification_as_read

# Define job_applications directly in this file to avoid circular imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Case, When, Value, IntegerField
from core.models import JobListing, JobApplication
from .dashboard import is_employer

@login_required
@user_passes_test(is_employer)
def job_applications(request, job_id):
    """
    Display all applications for a specific job
    """
    # Get the job and verify ownership
    job = get_object_or_404(JobListing.all_objects, id=job_id)
    employer_profile = request.user.userprofile.employer_profile
    
    if job.employer != employer_profile:
        messages.error(request, "You don't have permission to view applications for this job.")
        return redirect('employer_dashboard')
    
    # Get applications for this job
    applications = JobApplication.objects.filter(job=job).select_related('user', 'job')
    
    # Apply filters if provided
    if 'status' in request.GET and request.GET['status']:
        applications = applications.filter(status=request.GET['status'])
    
    if 'search' in request.GET and request.GET['search']:
        search_query = request.GET['search']
        applications = applications.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(guest_name__icontains=search_query) |
            Q(guest_email__icontains=search_query)
        )
    
    # Sort applications by status with custom order
    applications = applications.annotate(
        status_order=Case(
            When(status='გასაუბრება', then=Value(1)),     # Interview - first priority
            When(status='რეზერვი', then=Value(2)),        # Reserve - second priority
            When(status='განხილვის_პროცესში', then=Value(3)),  # In review - third priority
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('status_order', '-applied_at')
    
    # Mark all applications as read
    unread_applications = applications.filter(is_read=False)
    if unread_applications.exists():
        unread_applications.update(is_read=True)
    
    # Mark all notifications for this job as read
    from core.repositories.notification_repository import NotificationRepository
    NotificationRepository.mark_job_notifications_as_read(employer_profile, job_id)
    
    # Get counts for each status
    total_applications = applications.count()
    review_applications = applications.filter(status='განხილვის_პროცესში').count()
    interview_applications = applications.filter(status='გასაუბრება').count()
    reserve_applications = applications.filter(status='რეზერვი').count()
    
    context = {
        'job': job,
        'applications': applications,
        'total_applications': total_applications,
        'review_applications': review_applications,
        'interview_applications': interview_applications,
        'reserve_applications': reserve_applications,
        'is_deleted': job.deleted_at is not None,
    }
    
    return render(request, 'core/employer_applications.html', context)

# For backward compatibility, expose all views at the module level
__all__ = [
    'employer_dashboard', 'employer_home',
    'post_job', 'delete_job', 'extend_job', 'restore_job', 'deleted_jobs',
    'job_applications', 'update_application_status', 'application_detail',
    'cv_database',
    'company_profile', 'get_job_details',
    'mark_notifications_as_read', 'mark_job_notifications_as_read', 'mark_notification_as_read',
] 