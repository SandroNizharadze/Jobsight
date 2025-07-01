from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.models import JobListing, RejectionReason
from core.repositories.job_repository import JobRepository
from core.repositories.application_repository import ApplicationRepository
from core.repositories.notification_repository import NotificationRepository
from .dashboard import is_employer
import json
import logging

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(is_employer)
def job_applications(request, job_id):
    """
    View applications for a specific job
    """
    employer_profile = request.user.userprofile.employer_profile
    job = get_object_or_404(JobListing, id=job_id, employer=employer_profile)
    
    # Get status filter from request
    status_filter = request.GET.get('status')
    
    # Get applications using the repository
    applications = ApplicationRepository.get_applications_by_job(
        job_id=job_id,
        status_filter=status_filter
    )
    
    # Get application counts by status
    status_counts = ApplicationRepository.get_application_counts_by_status(job_id=job_id)
    
    # Get all possible rejection reasons
    rejection_reasons = RejectionReason.objects.all()
    
    context = {
        'job': job,
        'applications': applications,
        'rejection_reasons': rejection_reasons,
        'status_counts': status_counts,
        'current_status_filter': status_filter,
    }
    return render(request, 'core/job_applications.html', context)

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
            # Handle possible list values from form data
            if 'rejection_reasons' in request.POST:
                data['rejection_reasons'] = request.POST.getlist('rejection_reasons')
        
        new_status = data.get('status')
        old_status = application.status
        rejection_reason_ids = data.get('rejection_reasons', [])
        feedback = data.get('feedback', '')
        
        # Validate the status
        valid_statuses = [choice[0] for choice in application._meta.get_field('status').choices]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        
        # Update the application
        application.status = new_status
        application.feedback = feedback
        application.is_read = True
        application.save()
        
        # Update rejection reasons if provided
        if rejection_reason_ids:
            # Clear existing reasons
            application.rejection_reasons.clear()
            
            # Add new reasons
            for reason_id in rejection_reason_ids:
                try:
                    reason = RejectionReason.objects.get(id=reason_id)
                    application.rejection_reasons.add(reason)
                except RejectionReason.DoesNotExist:
                    logger.warning(f"Rejection reason with ID {reason_id} does not exist")
        
        # Create notification for candidate if status changed to interview or reserve
        if application.user and new_status != old_status:
            job_name = application.job.title if application.job else application.job_title
            company_name = application.job.company if application.job else application.job_company
            
            if new_status == 'გასაუბრება':
                # Create interview invitation notification
                message = f"თქვენი განაცხადი '{job_name}' პოზიციაზე კომპანიაში '{company_name}' შეიცვალა. თქვენ მოგიწვიეს გასაუბრებაზე."
                NotificationRepository.create_interview_invitation_notification(
                    user=application.user,
                    application=application,
                    message=message
                )
                logger.info(f"Created interview invitation notification for user {application.user.id}")
            
            elif new_status == 'რეზერვი':
                # Create application status update notification
                message = f"თქვენი განაცხადი '{job_name}' პოზიციაზე კომპანიაში '{company_name}' შეიცვალა. თქვენი განაცხადი გადავიდა რეზერვში."
                NotificationRepository.create_application_status_notification(
                    user=application.user,
                    application=application,
                    message=message
                )
                logger.info(f"Created application status update notification for user {application.user.id}")
        
        return JsonResponse({
            'success': True, 
            'message': 'Application status updated',
            'new_status': application.get_status_display()
        })
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
    
    # Get the application
    application = get_object_or_404(
        ApplicationRepository.get_applications_by_employer(employer_profile),
        id=application_id
    )
    
    # Mark as read if not already
    if not application.is_read:
        ApplicationRepository.mark_application_as_read(application_id)
    
    # Mark as viewed
    ApplicationRepository.mark_application_as_viewed(application_id)
    
    # Get all possible rejection reasons
    rejection_reasons = RejectionReason.objects.all()
    
    context = {
        'application': application,
        'rejection_reasons': rejection_reasons,
    }
    return render(request, 'core/application_detail.html', context) 