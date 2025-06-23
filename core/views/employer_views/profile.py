from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from core.models import EmployerProfile, JobListing
from .dashboard import is_employer
import logging

logger = logging.getLogger(__name__)

def company_profile(request, employer_id):
    """
    Public view for a company profile
    """
    employer_profile = get_object_or_404(EmployerProfile, id=employer_id)
    
    # Get active jobs for this employer
    active_jobs = JobListing.objects.filter(
        employer=employer_profile,
        status='approved'
    ).order_by('-posted_at')
    
    context = {
        'employer_profile': employer_profile,
        'active_jobs': active_jobs,
    }
    return render(request, 'core/company_profile.html', context)

@login_required
@user_passes_test(is_employer)
def get_job_details(request, job_id):
    """
    AJAX endpoint to get job details
    """
    employer_profile = request.user.userprofile.employer_profile
    
    try:
        job = JobListing.objects.get(id=job_id, employer=employer_profile)
        
        # Count applications by status
        applications_count = job.applications.count()
        unread_applications_count = job.applications.filter(is_read=False).count()
        
        data = {
            'success': True,
            'job': {
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'category': job.category,
                'status': job.status,
                'status_display': job.get_status_display(),
                'posted_at': job.posted_at.strftime('%Y-%m-%d %H:%M'),
                'expires_at': job.expires_at.strftime('%Y-%m-%d %H:%M') if job.expires_at else None,
                'days_until_expiration': job.days_until_expiration(),
                'is_expired': job.is_expired(),
                'applications_count': applications_count,
                'unread_applications_count': unread_applications_count,
                'view_count': job.view_count,
            }
        }
        return JsonResponse(data)
    except JobListing.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Job not found'}, status=404) 