from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from core.models import JobApplication, RejectionReason, JobListing
from core.services.employer_service import EmployerService
import json
import logging
import calendar
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
from core.repositories.notification_repository import NotificationRepository
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
    
    # Get metrics using the service
    metrics = EmployerService.get_employer_metrics(employer_profile)
    
    # Get jobs using the service
    all_jobs = EmployerService.get_employer_jobs(
        employer_profile, 
        sort_option='status'
    )
    
    # Recent applicants (last 5)
    recent_applicants = JobApplication.objects.filter(
        job__employer=employer_profile
    ).select_related('job', 'user').order_by('-applied_at')[:5]

    # Get all rejection reasons
    rejection_reasons = RejectionReason.objects.all()

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
    
    # Define status mapping with consistent colors
    status_mapping = {
        'განხილვის_პროცესში': {
            'label': 'In Review',
            'color': 'rgba(245, 158, 11, 0.7)',  # amber/yellow
        },
        'გასაუბრება': {
            'label': 'Interview',
            'color': 'rgba(16, 185, 129, 0.7)',  # green
        },
        'რეზერვი': {
            'label': 'Reserve',
            'color': 'rgba(239, 68, 68, 0.7)',  # red
        },
    }
    
    # Create a dictionary to store counts by status type
    status_counts = {status: 0 for status in status_mapping.keys()}
    
    # Aggregate the status counts
    for status in status_distribution:
        if status['status'] in status_counts:
            status_counts[status['status']] = status['count']
    
    # Generate the arrays in a consistent order
    for status_key, status_info in status_mapping.items():
        status_labels.append(status_info['label'])
        status_data.append(status_counts[status_key])
        status_colors.append(status_info['color'])
    
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

    # Convert Python lists to JSON for the template with proper error handling
    try:
        chart_labels_json = json.dumps(chart_labels, cls=DjangoJSONEncoder)
        chart_data_json = json.dumps(chart_data, cls=DjangoJSONEncoder)
        status_labels_json = json.dumps(status_labels, cls=DjangoJSONEncoder)
        status_data_json = json.dumps(status_data, cls=DjangoJSONEncoder)
        status_colors_json = json.dumps(status_colors, cls=DjangoJSONEncoder)
        category_labels_json = json.dumps(category_labels, cls=DjangoJSONEncoder)
        category_data_json = json.dumps(category_data, cls=DjangoJSONEncoder)
        source_labels_json = json.dumps(source_labels, cls=DjangoJSONEncoder)
        source_data_json = json.dumps(source_data, cls=DjangoJSONEncoder)
        source_colors_json = json.dumps(source_colors, cls=DjangoJSONEncoder)
    except Exception as e:
        logger.error(f"Error encoding chart data to JSON: {e}")
        # Provide fallback empty arrays if JSON encoding fails
        chart_labels_json = "[]"
        chart_data_json = "[]"
        status_labels_json = "[]"
        status_data_json = "[]"
        status_colors_json = "[]"
        category_labels_json = "[]"
        category_data_json = "[]"
        source_labels_json = "[]"
        source_data_json = "[]"
        source_colors_json = "[]"

    context = {
        'employer_profile': employer_profile,
        'total_jobs': metrics['total_jobs'],
        'active_jobs': metrics['active_jobs'],
        'total_applicants': metrics['total_applicants'],
        'unread_applicants': metrics['unread_applicants'],
        'avg_applicants': metrics['avg_applicants'],
        'all_jobs': all_jobs,
        'recent_applicants': recent_applicants,
        'rejection_reasons': rejection_reasons,
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

    # Get search query from request
    search_query = request.GET.get('search', '')
    
    # Get sort option from request
    sort_option = request.GET.get('sort_by', 'date_desc')
    
    # Get jobs using the service
    jobs = EmployerService.get_employer_jobs(
        employer_profile=employer_profile,
        search_query=search_query,
        sort_option=sort_option
    ).filter(
        deleted_at__isnull=True  # Explicitly exclude deleted jobs
    )
    # Removed the .exclude(status='expired') to show expired jobs
    
    # Process jobs to add helper attributes for template
    all_jobs = []
    
    # Get notification counts
    unread_notification_count = NotificationRepository.get_unread_notification_count(employer_profile)
    
    for job in jobs:
        # Check expiration date and add a convenience attribute
        if job.expires_at:
            # Calculate days until expiration
            days_until_expiration = (job.expires_at - timezone.now()).days
            
            # Job is expired if it's past the expiration date (but don't override extended_review status)
            job.is_expired_status = days_until_expiration < 0
            
            # Show days remaining (minimum 0)
            job.days_until_expiration_value = max(0, days_until_expiration)
            
            # Update the status to 'expired' if the expiration date has passed but status isn't 'expired' yet
            # Don't change status if it's already in extended_review
            if job.is_expired_status and job.status != 'expired' and job.status != 'extended_review':
                job.status = 'expired'
                job.save(update_fields=['status'])
        else:
            job.is_expired_status = False
            job.days_until_expiration_value = None
        
        # Add unread notification count for this job
        job.unread_notification_count = NotificationRepository.get_unread_notification_count_by_job(
            employer_profile=employer_profile,
            job_id=job.id
        )
            
        all_jobs.append(job)
    
    # Get deleted jobs count for the template
    deleted_jobs_count = JobListing.all_objects.filter(
        employer=employer_profile,
        deleted_at__isnull=False
    ).count()
    
    context = {
        'employer_profile': employer_profile,
        'all_jobs': all_jobs,
        'search_query': search_query,
        'sort_option': sort_option,
        'unread_notification_count': unread_notification_count,
        'deleted_jobs_count': deleted_jobs_count,
    }
    
    # If this is an AJAX request, only return the jobs container
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'core/partials/job_listings.html', context)
    
    # Otherwise return the full page
    return render(request, 'core/employer_profile.html', context) 