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
    employer_profile = request.user.userprofile.employer_profile
    job = get_object_or_404(JobListing, id=job_id, employer=employer_profile)
    
    # Use the service to extend the job
    days = int(request.POST.get('days', 30))
    updated_job = JobService.extend_job_expiration(job_id=job_id, days=days)
    
    if updated_job:
        messages.success(request, f"Job listing extended by {days} days.")
    else:
        messages.error(request, "Failed to extend job listing.")
    
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