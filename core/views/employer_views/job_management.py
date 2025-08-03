from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from core.models import JobListing
from core.forms import JobListingForm
from core.services.employer_service import EmployerService
from core.services.job_service import JobService
from .dashboard import is_employer
import logging
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(is_employer)
def post_job(request):
    """
    Create or edit a job listing
    """
    employer_profile = request.user.userprofile.employer_profile
    job_id = request.GET.get('job_id')
    job = None
    
    if job_id:
        # Edit existing job
        job = get_object_or_404(JobListing, id=job_id, employer=employer_profile)
        if request.method == 'POST':
            form = JobListingForm(request.POST, instance=job)
            if form.is_valid():
                job = form.save(commit=False)
                job.employer = employer_profile
                job.save()
                messages.success(request, "Job listing updated successfully!")
                return redirect('employer_dashboard')
        else:
            form = JobListingForm(instance=job)
    else:
        # Create new job
        if request.method == 'POST':
            form = JobListingForm(request.POST)
            if form.is_valid():
                job = form.save(commit=False)
                job.employer = employer_profile
                job.company = employer_profile.company_name
                job.save()
                messages.success(request, "Job listing created successfully!")
                return redirect('employer_dashboard')
        else:
            # Pre-fill company name from employer profile
            form = JobListingForm(initial={'company': employer_profile.company_name})
    
    context = {
        'form': form,
        'job': job,
        'is_edit': job is not None,
    }
    return render(request, 'core/post_job.html', context)

@login_required
@user_passes_test(is_employer)
@require_POST
def delete_job(request, job_id):
    """
    Soft delete a job listing (mark as deleted)
    """
    employer_profile = request.user.userprofile.employer_profile
    job = get_object_or_404(JobListing, id=job_id, employer=employer_profile)
    
    # Use the model's soft delete method
    job.delete()
    
    messages.success(request, "Job listing deleted successfully.")
    return redirect('employer_dashboard')

@login_required
@user_passes_test(is_employer)
@require_POST
def extend_job(request, job_id):
    """
    Extend the expiration date of a job listing
    """
    try:
        employer_profile = request.user.userprofile.employer_profile
        job = get_object_or_404(JobListing, id=job_id, employer=employer_profile)
        
        logger.info(f"Extending job {job_id} for employer {employer_profile.id}")
        logger.info(f"Current job status: {job.status}")
        logger.info(f"Expiration date: {job.expires_at}")
        
        # Check if the job is expired by date
        is_expired_by_date = job.expires_at and job.expires_at < timezone.now()
        logger.info(f"Is expired by date: {is_expired_by_date}")
        
        # First, ensure the status is updated to reflect expiration
        if is_expired_by_date and job.status != 'expired':
            logger.info(f"Updating job status to expired due to expiration date")
            job.status = 'expired'
            job.save(update_fields=['status'])
        
        # Only allow extension if job is approved or expired
        if job.status not in ['approved', 'expired']:
            logger.warning(f"Job {job_id} status {job.status} not eligible for extension")
            messages.error(request, "Only approved or expired jobs can have their expiration date extended.")
            return redirect('employer_dashboard')
        
        # For employer-initiated extensions, we just set status to extended_review
        # The admin will handle setting the new expiration date during review
        job.status = 'extended_review'
        job.save(update_fields=['status'])
        
        logger.info(f"Job {job_id} status updated to extended_review")
        messages.success(request, "Your extension request has been submitted. The job will remain active until its current expiration date, and an admin will review your extension request.")
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'success',
                'message': 'Job extension request submitted successfully',
                'new_status': job.status
            })
        
        return redirect('employer_dashboard')
        
    except Exception as e:
        logger.error(f"Error extending job {job_id}: {str(e)}", exc_info=True)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
        messages.error(request, f"Error extending job: {str(e)}")
        return redirect('employer_dashboard')

@login_required
@user_passes_test(is_employer)
def deleted_jobs(request):
    """
    View for showing deleted jobs
    """
    employer_profile = request.user.userprofile.employer_profile
    
    # Get search query from request
    search_query = request.GET.get('search', '')
    
    # Get sort option from request
    sort_option = request.GET.get('sort_by', 'date_desc')
    
    # Get deleted jobs using the service
    deleted_jobs = EmployerService.get_employer_jobs(
        employer_profile=employer_profile,
        include_deleted=True,
        search_query=search_query,
        sort_option=sort_option
    ).filter(deleted_at__isnull=False)
    
    context = {
        'employer_profile': employer_profile,
        'deleted_jobs': deleted_jobs,
        'search_query': search_query,
        'sort_option': sort_option,
    }
    
    return render(request, 'core/deleted_jobs.html', context)

@login_required
@user_passes_test(is_employer)
@require_POST
def restore_job(request, job_id):
    """
    Restore a deleted job listing
    """
    employer_profile = request.user.userprofile.employer_profile
    
    # Use all_objects manager to get deleted jobs
    job = get_object_or_404(JobListing.all_objects, id=job_id, employer=employer_profile)
    
    if not job.deleted_at:
        messages.warning(request, "This job is not deleted.")
        return redirect('employer_dashboard')
    
    # Restore the job by setting deleted_at to None
    job.deleted_at = None
    job.save(update_fields=['deleted_at'])
    
    messages.success(request, "Job listing restored successfully.")
    return redirect('employer_dashboard')