from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from core.models import JobApplication
from core.services.employer_service import EmployerService
import json
import logging
import calendar
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
from core.repositories.notification_repository import NotificationRepository

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
        'total_jobs': metrics['total_jobs'],
        'active_jobs': metrics['active_jobs'],
        'total_applicants': metrics['total_applicants'],
        'unread_applicants': metrics['unread_applicants'],
        'avg_applicants': metrics['avg_applicants'],
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
    ).exclude(
        status='expired'  # Exclude expired jobs
    )
    
    # Process jobs to add helper attributes for template
    all_jobs = []
    
    # Get notification counts
    unread_notification_count = NotificationRepository.get_unread_notification_count(employer_profile)
    
    for job in jobs:
        # Check expiration date and add a convenience attribute
        if job.expires_at:
            job.is_expired_status = job.expires_at < timezone.now()
            job.days_until_expiration_value = max(0, (job.expires_at - timezone.now()).days)
        else:
            job.is_expired_status = False
            job.days_until_expiration_value = None
        
        # Add unread notification count for this job
        job.unread_notification_count = NotificationRepository.get_unread_notification_count_by_job(
            employer_profile=employer_profile,
            job_id=job.id
        )
            
        all_jobs.append(job)
    
    context = {
        'employer_profile': employer_profile,
        'all_jobs': all_jobs,
        'search_query': search_query,
        'sort_option': sort_option,
        'unread_notification_count': unread_notification_count,
    }
    
    # If this is an AJAX request, only return the jobs container
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'core/partials/job_listings.html', context)
    
    # Otherwise return the full page
    return render(request, 'core/employer_profile.html', context) 