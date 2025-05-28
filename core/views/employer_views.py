from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Prefetch, Q, Case, When, Value, IntegerField, F
from ..models import JobListing, EmployerProfile, JobApplication, UserProfile, RejectionReason
from ..forms import JobListingForm, EmployerProfileForm
import logging
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseForbidden, JsonResponse
import json
from collections import defaultdict
import calendar
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

def is_employer(user):
    """
    Check if a user has employer role and associated employer profile
    """
    try:
        return (user.is_authenticated and 
                hasattr(user, 'userprofile') and 
                user.userprofile.role == 'employer' and
                hasattr(user.userprofile, 'employer_profile'))
    except:
        return False

@login_required
@user_passes_test(is_employer)
def employer_home(request):
    """
    Display the employer metrics/summary page (not job management)
    """
    employer_profile = request.user.userprofile.employer_profile
    jobs = JobListing.objects.filter(employer=employer_profile)

    # Metrics
    total_jobs = jobs.count()
    active_jobs = jobs.filter(status='approved').count()
    total_applicants = JobApplication.objects.filter(job__employer=employer_profile).count()
    unread_applicants = JobApplication.objects.filter(job__employer=employer_profile, is_read=False).count()
    avg_applicants = round(total_applicants / total_jobs, 2) if total_jobs > 0 else 0
    
    # All jobs for this employer ordered by most recent first
    all_jobs = jobs.order_by('-posted_at')
    
    # Sort jobs by status (approved first, then pending review, then rejected)
    all_jobs = jobs.annotate(
        status_order=Case(
            When(status='approved', then=Value(1)),
            When(status='pending_review', then=Value(2)),
            When(status='rejected', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        ),
        unread_applications_count=Count(
            'applications',
            filter=Q(applications__is_read=False)
        )
    ).select_related('employer').order_by('status_order', '-posted_at')
    
    # Recent applicants (last 5)
    recent_applicants = JobApplication.objects.filter(
        job__employer=employer_profile
    ).select_related('job', 'user').order_by('-applied_at')[:5]

    # Chart data - Applications over time (last 6 months)
    now = timezone.now()
    six_months_ago = now - timedelta(days=180)
    applications_by_month = JobApplication.objects.filter(
        job__employer=employer_profile,
        applied_at__gte=six_months_ago
    ).extra({
        'month': "EXTRACT(MONTH FROM applied_at)",
        'year': "EXTRACT(YEAR FROM applied_at)"
    }).values('month', 'year').annotate(count=Count('id')).order_by('year', 'month')
    
    # Format data for the chart
    months_data = defaultdict(int)
    for item in applications_by_month:
        month_num = int(item['month'])
        month_name = calendar.month_abbr[month_num]
        year = int(item['year'])
        key = f"{month_name} {year}"
        months_data[key] = item['count']
    
    # Get the last 6 months in chronological order
    last_6_months = []
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        month_key = f"{calendar.month_abbr[month_date.month]} {month_date.year}"
        last_6_months.append(month_key)
    
    # Prepare chart data
    chart_labels = last_6_months
    chart_data = [months_data.get(month, 0) for month in last_6_months]
    
    # Application status distribution
    status_distribution = JobApplication.objects.filter(
        job__employer=employer_profile
    ).values('status').annotate(count=Count('id'))
    
    status_labels = []
    status_data = []
    status_colors = []
    
    for status in status_distribution:
        if status['status'] == 'განხილვის_პროცესში':
            status_labels.append('In Review')
            status_colors.append('rgba(245, 158, 11, 0.7)')
        elif status['status'] == 'გასაუბრება':
            status_labels.append('Interview')
            status_colors.append('rgba(16, 185, 129, 0.7)')
        elif status['status'] == 'რეზერვი':
            status_labels.append('Reserve')
            status_colors.append('rgba(239, 68, 68, 0.7)')
        else:
            # Skip any legacy status values that don't match current choices
            continue
        status_data.append(status['count'])
    
    # Job category performance
    category_performance = JobApplication.objects.filter(
        job__employer=employer_profile
    ).values('job__category').annotate(count=Count('id')).order_by('-count')[:5]
    
    category_labels = [item['job__category'] for item in category_performance]
    category_data = [item['count'] for item in category_performance]
    
    # Applicant sources (registered vs guest)
    registered_count = JobApplication.objects.filter(
        job__employer=employer_profile,
        user__isnull=False
    ).count()
    
    guest_count = JobApplication.objects.filter(
        job__employer=employer_profile,
        user__isnull=True
    ).count()
    
    source_labels = ['Registered Users', 'Guest Applications']
    source_data = [registered_count, guest_count]
    source_colors = [
        'rgba(59, 130, 246, 0.7)',
        'rgba(16, 185, 129, 0.7)'
    ]

    # Convert Python lists to JSON for the template
    chart_labels_json = json.dumps(chart_labels)
    chart_data_json = json.dumps(chart_data)
    status_labels_json = json.dumps(status_labels)
    status_data_json = json.dumps(status_data)
    status_colors_json = json.dumps(status_colors)
    category_labels_json = json.dumps(category_labels)
    category_data_json = json.dumps(category_data)
    source_labels_json = json.dumps(source_labels)
    source_data_json = json.dumps(source_data)
    source_colors_json = json.dumps(source_colors)

    context = {
        'employer_profile': employer_profile,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'unread_applicants': unread_applicants,
        'avg_applicants': avg_applicants,
        'all_jobs': all_jobs,
        'recent_applicants': recent_applicants,
        # Chart data
        'chart_labels': chart_labels_json,
        'chart_data': chart_data_json,
        'status_labels': status_labels_json,
        'status_data': status_data_json,
        'status_colors': status_colors_json,
        'category_labels': category_labels_json,
        'category_data': category_data_json,
        'source_labels': source_labels_json,
        'source_data': source_data_json,
        'source_colors': source_colors_json,
    }
    return render(request, 'core/employer_home.html', context)

@login_required
@user_passes_test(is_employer)
def employer_dashboard(request):
    """
    Display the employer dashboard with detailed analytics
    """
    employer_profile = request.user.userprofile.employer_profile

    # Get all jobs for this employer, including deleted ones
    all_jobs = JobListing.all_objects.filter(
        employer=employer_profile
    ).annotate(
        applications_count=Count('applications'),
        unread_applications_count=Count('applications', filter=Q(applications__is_read=False)),
        status_order=Case(
            When(status='approved', then=Value(1)),
            When(status='pending_review', then=Value(2)),
            When(status='rejected', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        ),
    ).select_related(
        'employer'  # Include employer data to reduce queries
    ).order_by('status_order', '-posted_at')
    
    # Process jobs to add expiration info
    for job in all_jobs:
        job.is_expired_status = job.is_expired()
        job.days_until_expiration_value = job.days_until_expiration()
        job.is_deleted = job.deleted_at is not None
    
    # Get active jobs (not deleted)
    jobs = JobListing.objects.filter(
        employer=employer_profile
    ).annotate(
        applications_count=Count('applications'),
        unread_applications_count=Count('applications', filter=Q(applications__is_read=False)),
        status_order=Case(
            When(status='approved', then=Value(1)),
            When(status='pending_review', then=Value(2)),
            When(status='rejected', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        ),
    ).select_related(
        'employer'  # Include employer data to reduce queries
    ).order_by('status_order', '-posted_at')

    # Metrics
    active_jobs = jobs.filter(status='approved').count()
    total_applicants = JobApplication.objects.filter(job__employer=employer_profile).count()
    avg_applicants = (
        total_applicants / active_jobs if active_jobs > 0 else 0
    )
    # Jobs expiring soon (example: jobs expiring in next 7 days)
    soon = timezone.now() + timedelta(days=7)
    jobs_expiring_soon = jobs.filter(
        expires_at__lte=soon, 
        expires_at__gte=timezone.now(),
        status='approved'
    ).count()
    
    # Count expired jobs
    expired_jobs_count = jobs.filter(status='expired').count()
    
    # Count deleted jobs
    deleted_jobs_count = JobListing.all_objects.filter(
        employer=employer_profile,
        deleted_at__isnull=False
    ).count()

    # Recent applicants (last 5)
    recent_applicants = JobApplication.objects.filter(
        job__employer=employer_profile
    ).select_related('user', 'job').order_by('-applied_at')[:5]

    context = {
        'employer_profile': employer_profile,
        'jobs': jobs,
        'all_jobs': all_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'avg_applicants': avg_applicants,
        'jobs_expiring_soon': jobs_expiring_soon,
        'expired_jobs_count': expired_jobs_count,
        'deleted_jobs_count': deleted_jobs_count,
        'recent_applicants': recent_applicants,
    }
    return render(request, 'core/employer_profile.html', context)

@login_required
@user_passes_test(is_employer)
def post_job(request):
    """
    Handle job posting form submission
    """
    # Get premium level from URL parameter if available
    premium_level = request.GET.get('premium_level', 'standard')
    
    # Validate premium level value
    if premium_level not in ['standard', 'premium', 'premium_plus']:
        premium_level = 'standard'
    
    if request.method == 'POST':
        form = JobListingForm(request.POST)
        if form.is_valid():
            # Create the job but don't save to DB yet
            job = form.save(commit=False)
            
            # Set the employer and company
            employer_profile = request.user.userprofile.employer_profile
            job.employer = employer_profile
            job.company = employer_profile.company_name
            
            # Ensure georgian_language_only is set
            if job.georgian_language_only is None:
                job.georgian_language_only = False
            
            # Save to DB
            job.save()
            
            messages.success(request, "Job posting submitted for review!")
            return redirect('employer_dashboard')
    else:
        # Initialize form with premium level from URL
        form = JobListingForm(initial={'premium_level': premium_level})
    
    context = {
        'form': form,
        'selected_premium_level': premium_level,
    }
    
    return render(request, 'core/post_job.html', context)

@login_required
@user_passes_test(is_employer)
@require_POST
def delete_job(request, job_id):
    """
    Handle deletion of a job listing
    """
    # Get the job and verify ownership
    job = get_object_or_404(JobListing, id=job_id)
    employer_profile = request.user.userprofile.employer_profile
    
    if job.employer != employer_profile:
        messages.error(request, "You don't have permission to delete this job.")
        return redirect('employer_dashboard')
    
    # Delete the job
    job.delete()
    
    messages.success(request, "Job listing has been deleted.")
    return redirect('employer_dashboard')

@login_required
@user_passes_test(is_employer)
@require_POST
def extend_job(request, job_id):
    """
    Handle extension of a job's expiration date
    """
    # Get the job and verify ownership
    job = get_object_or_404(JobListing, id=job_id)
    employer_profile = request.user.userprofile.employer_profile
    
    if job.employer != employer_profile:
        messages.error(request, "You don't have permission to extend this job.")
        return redirect('employer_dashboard')
    
    # Only allow extension if job is approved
    if job.status != 'approved':
        messages.error(request, "Only approved jobs can have their expiration date extended.")
        return redirect('employer_dashboard')
    
    # Check if job is expired
    is_expired = job.is_expired()
    
    if is_expired:
        # If job is expired, change status to pending_review
        job.status = 'pending_review'
        # Save the job to update its status
        job.save()
        messages.success(request, "Your job has been submitted for review. An admin will extend it soon.")
    else:
        # Extend the job by 30 days
        job.extend_expiration(days=30)
        # Get the new expiration date
        new_expiration = job.expires_at.strftime('%B %d, %Y')
        messages.success(request, f"Job listing expiration extended to {new_expiration}.")
    
    return redirect('employer_dashboard')

@login_required
@user_passes_test(is_employer)
def job_applications(request, job_id):
    """
    Display all applications for a specific job
    """
    # Get the job and verify ownership
    job = get_object_or_404(JobListing, id=job_id)
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
    }
    
    return render(request, 'core/employer_applications.html', context)

@login_required
@user_passes_test(is_employer)
@require_POST
def update_application_status(request, application_id):
    """
    Update the status of a job application
    """
    # Get the application and verify permission
    application = get_object_or_404(JobApplication, id=application_id)
    employer_profile = request.user.userprofile.employer_profile
    
    # Check if the application belongs to a job owned by this employer
    if application.job.employer != employer_profile:
        return HttpResponseForbidden("You don't have permission to update this application.")
    
    # Update the status
    new_status = request.POST.get('status')
    if new_status in dict(JobApplication.STATUS_CHOICES):
        application.status = new_status
        
        # If status is changed to "რეზერვი" (reserve) and no rejection reasons are provided yet,
        # return JSON response to request rejection reasons
        if new_status == 'რეზერვი' and 'rejection_reasons' not in request.POST:
            # Check if this is a guest application
            is_guest = application.user is None
            
            if is_guest:
                # For guest applications, just update the status without requesting reasons
                application.save()
                return JsonResponse({'success': True})
            else:
                # For registered users, save the status change and request rejection reasons
                application.save()
                
                # Get all available rejection reasons
                reasons = [{'id': key, 'name': value} for key, value in dict(RejectionReason.REASON_CHOICES).items()]
                
                return JsonResponse({
                    'status': 'need_rejection_reasons',
                    'application_id': application_id,
                    'reasons': reasons
                })
        
        # If rejection reasons are provided, save them
        if new_status == 'რეზერვი' and 'rejection_reasons' in request.POST:
            # Clear existing reasons
            application.rejection_reasons.clear()
            
            # Add new reasons
            reason_ids = request.POST.getlist('rejection_reasons')
            for reason_id in reason_ids:
                try:
                    # Create or get the reason by its choice key
                    reason, created = RejectionReason.objects.get_or_create(name=reason_id)
                    application.rejection_reasons.add(reason)
                except Exception:
                    pass
            
            # Save feedback if provided and not a guest user
            is_guest = request.POST.get('is_guest') == 'true'
            if 'feedback' in request.POST and not is_guest and application.user:
                application.feedback = request.POST.get('feedback')
        
        application.save()
        messages.success(request, "Application status updated successfully.")
    else:
        messages.error(request, "Invalid status value provided.")
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # Redirect back to the applications page
    return redirect('job_applications', job_id=application.job.id)

@login_required
@user_passes_test(is_employer)
def get_job_details(request, job_id):
    """
    API endpoint to return job details in JSON format
    """
    # Get the job and verify ownership
    job = get_object_or_404(JobListing, id=job_id)
    employer_profile = request.user.userprofile.employer_profile
    
    if job.employer != employer_profile:
        return JsonResponse({"error": "You don't have permission to edit this job."}, status=403)
    
    # Return job details as JSON
    job_data = {
        'title': job.title,
        'description': job.description,
        'location': job.location,
        'category': job.category,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'salary_type': job.salary_type,
        'experience': job.experience,
        'job_preferences': job.job_preferences,
        'considers_students': job.considers_students,
        'georgian_language_only': job.georgian_language_only,
        'premium_level': job.premium_level,
    }
    
    return JsonResponse(job_data) 

def company_profile(request, employer_id):
    """
    Display the public company profile page for an employer
    """
    # Get the employer profile
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    
    # Get active job listings for this employer
    jobs = JobListing.objects.filter(employer=employer, status='approved').order_by('-posted_at')
    
    # Count of open jobs
    open_jobs_count = jobs.count()
    
    context = {
        'company': employer,
        'jobs': jobs,
        'open_jobs_count': open_jobs_count,
    }
    
    return render(request, 'core/employer_profile_public.html', context) 

@login_required
@user_passes_test(is_employer)
def application_detail(request, application_id):
    """
    Display detailed information about a specific application
    """
    # Get the application and verify permission
    application = get_object_or_404(JobApplication.objects.select_related('user', 'job'), id=application_id)
    employer_profile = request.user.userprofile.employer_profile
    
    # Check if the application belongs to a job owned by this employer
    if application.job.employer != employer_profile:
        messages.error(request, "You don't have permission to view this application.")
        return redirect('employer_dashboard')
    
    context = {
        'application': application,
        'job': application.job,
    }
    
    return render(request, 'core/employer_application_detail.html', context) 

@login_required
@user_passes_test(is_employer)
@require_POST
def restore_job(request, job_id):
    """
    Handle restoration of a deleted job listing
    """
    # Get the job and verify ownership
    job = get_object_or_404(JobListing.all_objects, id=job_id)
    employer_profile = request.user.userprofile.employer_profile
    
    if job.employer != employer_profile:
        messages.error(request, "You don't have permission to restore this job.")
        return redirect('employer_dashboard')
    
    # Check if job is deleted
    if job.deleted_at is None:
        messages.error(request, "This job is not deleted.")
        return redirect('employer_dashboard')
    
    # Restore the job (set deleted_at to None)
    job.deleted_at = None
    job.status = 'pending_review'
    job.save()
    
    messages.success(request, "Job listing has been restored.")
    return redirect('employer_dashboard')

@login_required
@user_passes_test(is_employer)
def cv_database(request):
    """
    Display a database of candidate CVs for employers
    Only shows CVs where user has opted in to be visible to employers
    Only accessible to employers with at least one premium+ job
    """
    employer_profile = request.user.userprofile.employer_profile
    
    # Check if employer has at least one premium+ job
    has_premium_plus = JobListing.objects.filter(
        employer=employer_profile,
        premium_level='premium_plus',
        status='approved',  # Only count approved jobs
        deleted_at__isnull=True  # Don't count deleted jobs
    ).exists()
    
    if not has_premium_plus:
        messages.error(request, "CV Database is only available for Premium+ employers. Please upgrade to Premium+ to access this feature.")
        messages.info(request, "Visit our <a href='/pricing/' class='underline text-blue-600 hover:text-blue-800'>pricing page</a> to learn more about Premium+ benefits.", extra_tags='safe')
        return redirect('employer_dashboard')
    
    # Get user profiles with CVs that are visible to employers
    profiles = UserProfile.objects.filter(
        role='candidate',
        cv__isnull=False,
        visible_to_employers=True
    ).select_related('user')
    
    # Apply filters if provided
    field_filter = request.GET.get('field', '')
    experience_filter = request.GET.get('experience', '')
    
    if field_filter:
        profiles = profiles.filter(desired_field=field_filter)
    
    if experience_filter:
        profiles = profiles.filter(field_experience=experience_filter)
    
    # Prepare context
    context = {
        'profiles': profiles,
        'all_fields': [value for value, _ in JobListing.CATEGORY_CHOICES],
        'all_experiences': [value for value, _ in JobListing.EXPERIENCE_CHOICES],
        'field_filter': field_filter,
        'experience_filter': experience_filter,
        'field_choices': dict(JobListing.CATEGORY_CHOICES),
        'experience_choices': dict(JobListing.EXPERIENCE_CHOICES),
    }
    
    return render(request, 'core/cv_database.html', context) 