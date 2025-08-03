from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.models import JobListing, JobApplication, RejectionReason
from core.repositories.job_repository import JobRepository
from core.repositories.application_repository import ApplicationRepository
from core.repositories.notification_repository import NotificationRepository
from .dashboard import is_employer
import json
import logging
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(is_employer)
def job_applications(request, job_id):
    """
    View applications for a specific job
    """
    employer_profile = request.user.userprofile.employer_profile
    job = get_object_or_404(JobRepository.get_jobs_by_employer(employer_profile), id=job_id)
    
    # Get applications for this job
    applications = ApplicationRepository.get_applications_by_job(job)
    
    # Get all rejection reasons
    rejection_reasons = RejectionReason.objects.all()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        applications = applications.filter(status=status_filter)
    
    # Search by name or email if provided
    search_query = request.GET.get('search')
    if search_query:
        applications = applications.filter(
            Q(user__first_name__icontains=search_query) | 
            Q(user__last_name__icontains=search_query) | 
            Q(user__email__icontains=search_query) |
            Q(guest_name__icontains=search_query) |
            Q(guest_email__icontains=search_query)
        )
    
    # Mark applications as read
    for application in applications:
        if not application.is_read:
            application.is_read = True
            application.save()
    
    # Mark applications as viewed
    # for application in applications:
    #     if not application.is_viewed:
    #         application.is_viewed = True
    #         application.save()
    #         logger.info(f"Marked application {application.id} as viewed for job {job_id}")
    
    return render(request, 'core/job_applications.html', {
        'job': job,
        'applications': applications,
        'rejection_reasons': rejection_reasons,
        'status_filter': status_filter,
        'search_query': search_query,
    })

@login_required
@user_passes_test(is_employer)
@require_POST
def update_application_status(request, application_id):
    """
    Update the status of a job application
    """
    employer_profile = request.user.userprofile.employer_profile
    application = get_object_or_404(
        ApplicationRepository.get_applications_by_employer(employer_profile),
        id=application_id
    )
    
    try:
        # Try to parse JSON data first
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Fall back to form data if not JSON
            data = request.POST.dict()
        
        new_status = data.get('status')
        old_status = application.status
        
        # Validate status
        if new_status not in ['განხილვის_პროცესში', 'გასაუბრება', 'რეზერვი']:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
        # Update application status
        application.status = new_status
        
        # Handle rejection reasons if provided and status is 'რეზერვი'
        if new_status == 'რეზერვი' and 'rejection_reasons' in data:
            # Clear existing rejection reasons
            application.rejection_reasons.clear()
            
            # Add new rejection reasons
            reasons = data.get('rejection_reasons', [])
            if isinstance(reasons, list):
                for reason_id in reasons:
                    try:
                        # Get reason by ID instead of name
                        reason = RejectionReason.objects.get(id=reason_id)
                        application.rejection_reasons.add(reason)
                    except RejectionReason.DoesNotExist:
                        logger.warning(f"Rejection reason with ID {reason_id} not found")
                    except ValueError:
                        # Handle case where the value might not be a valid integer
                        logger.warning(f"Invalid rejection reason ID format: {reason_id}")
            
            # Add feedback if provided
            feedback = data.get('feedback', '')
            if feedback:
                application.feedback = feedback
        
        application.save()
        
        # Mark as read if not already
        if not application.is_read:
            application.is_read = True
            application.save()
        
        # Create notification for candidate if status changed
        if old_status != new_status and application.user:
            notification_text = ''
            
            if new_status == 'გასაუბრება':
                notification_text = f"თქვენი განაცხადი ვაკანსიაზე '{application.job.title}' გადავიდა გასაუბრების ეტაპზე"
            elif new_status == 'რეზერვი':
                notification_text = f"თქვენი განაცხადი ვაკანსიაზე '{application.job.title}' გადავიდა რეზერვში"
            
            if notification_text:
                NotificationRepository.create_application_status_notification(
                    user=application.user,
                    application=application,
                    message=notification_text
                )
        
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"Error updating application status: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@user_passes_test(is_employer)
def application_detail(request, application_id):
    """
    View details of a specific application
    """
    employer_profile = request.user.userprofile.employer_profile
    application = get_object_or_404(
        ApplicationRepository.get_applications_by_employer(employer_profile),
        id=application_id
    )
    
    # Get all rejection reasons
    rejection_reasons = RejectionReason.objects.all()
    
    # Mark as read if not already
    if not application.is_read:
        application.is_read = True
        application.save()
    
    # Mark as viewed if not already
    if not application.is_viewed:
        application.is_viewed = True
        application.save(update_fields=['is_viewed'])
        logger.info(f"Marked application {application.id} as viewed when accessed by employer {employer_profile.id}")
    
    return render(request, 'core/application_detail.html', {
        'application': application,
        'rejection_reasons': rejection_reasons,
    }) 