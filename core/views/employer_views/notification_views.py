from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from core.repositories.notification_repository import NotificationRepository
from .dashboard import is_employer
import logging

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(is_employer)
def mark_notifications_as_read(request):
    """
    Mark all notifications as read for the employer
    """
    employer_profile = request.user.userprofile.employer_profile
    count = NotificationRepository.mark_all_notifications_as_read(employer_profile)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': count})
    
    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'employer_dashboard'))

@login_required
@user_passes_test(is_employer)
def mark_job_notifications_as_read(request, job_id):
    """
    Mark all notifications for a specific job as read
    """
    employer_profile = request.user.userprofile.employer_profile
    count = NotificationRepository.mark_job_notifications_as_read(employer_profile, job_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': count})
    
    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'job_applications'))

@login_required
@user_passes_test(is_employer)
def mark_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    success = NotificationRepository.mark_notification_as_read(notification_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': success})
    
    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'employer_dashboard')) 