from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..models import JobListing, JobApplication, SavedJob
from ..forms import JobListingForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

def remove_from_query_string(query_dict, param):
    """Helper function to remove a parameter from query string"""
    query_dict = query_dict.copy()
    query_dict.pop(param, None)
    return '?' + query_dict.urlencode() if query_dict else '?'

def job_list(request):
    """
    Display the job listing page with filtering options
    """
    # Only show approved jobs to the public
    # Use select_related to fetch employer in the same query
    # Order by premium level (premium_plus first, then premium, then standard)
    jobs = JobListing.objects.filter(status='approved').select_related('employer').order_by(
        # Custom ordering for premium levels
        # This will put premium_plus first, then premium, then standard
        # Since it's in reverse alphabetical order: standard < premium < premium_plus
        '-premium_level', '-posted_at'
    )
    
    # Filter out expired jobs
    # Only show jobs that either don't have an expiration date yet or where the expiration date is in the future
    jobs = jobs.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()))
    
    # Initialize filtering context variables
    filtered = False
    active_filters = {}
    filter_remove_urls = {}
    show_filters = 'show_filters' in request.GET
    
    # Filter by premium level on main page (when filters are NOT being shown)
    # Premium filtering logic - only show premium and premium_plus jobs on main page
    if not show_filters:
        jobs = jobs.filter(premium_level__in=['premium', 'premium_plus'])
    
    # Apply filters based on request parameters
    if 'search' in request.GET and request.GET['search']:
        search_term = request.GET['search']
        jobs = jobs.filter(
            Q(title__icontains=search_term) | 
            Q(company__icontains=search_term) |
            Q(description__icontains=search_term)
        )
        filtered = True
        active_filters['საძიებო სიტყვა'] = search_term
        filter_remove_urls['საძიებო სიტყვა'] = remove_from_query_string(request.GET, 'search')
    
    if 'location' in request.GET and request.GET['location']:
        location = request.GET['location']
        jobs = jobs.filter(location=location)
        filtered = True
        active_filters['ლოკაცია'] = location
        filter_remove_urls['ლოკაცია'] = remove_from_query_string(request.GET, 'location')
    
    if 'category' in request.GET and request.GET['category']:
        category = request.GET['category']
        jobs = jobs.filter(category=category)
        filtered = True
        active_filters['კატეგორია'] = category
        filter_remove_urls['კატეგორია'] = remove_from_query_string(request.GET, 'category')
    
    if 'premium_level' in request.GET and request.GET['premium_level']:
        premium_level = request.GET['premium_level']
        jobs = jobs.filter(premium_level=premium_level)
        filtered = True
        premium_level_display = {
            'standard': 'Standard',
            'premium': 'Premium',
            'premium_plus': 'Premium +'
        }.get(premium_level, premium_level)
        active_filters['Premium Level'] = premium_level_display
        filter_remove_urls['Premium Level'] = remove_from_query_string(request.GET, 'premium_level')
    
    if 'experience' in request.GET and request.GET['experience']:
        experience = request.GET['experience']
        jobs = jobs.filter(experience=experience)
        filtered = True
        # Get the display name for the experience level
        experience_dict = dict(JobListing.EXPERIENCE_CHOICES)
        experience_display = experience_dict.get(experience, experience)
        active_filters['გამოცდილება'] = experience_display
        filter_remove_urls['გამოცდილება'] = remove_from_query_string(request.GET, 'experience')
    
    if 'salary_min' in request.GET and request.GET['salary_min'] and int(request.GET['salary_min']) > 0:
        salary_min = request.GET['salary_min']
        jobs = jobs.filter(salary_min__gte=salary_min)
        filtered = True
        active_filters['მინიმალური ანაზღაურება'] = f"₾ {salary_min}"
        filter_remove_urls['მინიმალური ანაზღაურება'] = remove_from_query_string(request.GET, 'salary_min')
    
    if 'job_preferences' in request.GET:
        job_preferences_list = request.GET.getlist('job_preferences')
        if job_preferences_list:
            jobs = jobs.filter(job_preferences__in=job_preferences_list)
            filtered = True
            active_filters['სამუშაო გრაფიკი'] = ', '.join(job_preferences_list)
            filter_remove_urls['სამუშაო გრაფიკი'] = remove_from_query_string(request.GET, 'job_preferences')
    
    # Filter by considers_students
    if 'considers_students' in request.GET and request.GET['considers_students'] == 'true':
        jobs = jobs.filter(considers_students=True)
        filtered = True
        active_filters['სტუდენტური'] = 'კი'
        filter_remove_urls['სტუდენტური'] = remove_from_query_string(request.GET, 'considers_students')
    
    # Filter by georgian_language_only
    if 'georgian_language_only' in request.GET and request.GET['georgian_language_only'] == 'true':
        jobs = jobs.filter(georgian_language_only=True)
        filtered = True
        active_filters['მხოლოდ ქართულენოვანი'] = 'კი'
        filter_remove_urls['მხოლოდ ქართულენოვანი'] = remove_from_query_string(request.GET, 'georgian_language_only')
    
    # Include expired jobs only if explicitly requested
    if 'show_expired' in request.GET and request.GET['show_expired'] == '1':
        jobs = JobListing.objects.filter(status='approved').select_related('employer')
        filtered = True
        active_filters['Show Expired'] = 'Yes'
        filter_remove_urls['Show Expired'] = remove_from_query_string(request.GET, 'show_expired')
    
    # After all filters are applied, ensure premium ordering is preserved
    # This guarantees premium jobs always appear at the top even after filtering
    jobs = jobs.order_by('-premium_level', '-posted_at')
    
    # Get selected job preferences
    selected_job_preferences = request.GET.getlist('job_preferences')
    
    # No pagination - display all jobs
    jobs_page = jobs
    
    # Check if user is an employer
    is_employer_user = False
    if request.user.is_authenticated:
        try:
            is_employer_user = (request.user.userprofile.role == 'employer' and 
                               hasattr(request.user.userprofile, 'employer_profile'))
        except:
            pass
    
    # Count jobs by premium level for display in template
    # These counts will be used to show/hide sections and display job counts
    premium_plus_count = jobs.filter(premium_level='premium_plus').count()
    premium_count = jobs.filter(premium_level='premium').count()
    standard_count = jobs.filter(Q(premium_level='standard') | Q(premium_level__isnull=True)).count()
    
    context = {
        'jobs': jobs_page,
        'is_employer': is_employer_user,
        'job_categories': JobListing.CATEGORY_CHOICES,
        'job_locations': JobListing.LOCATION_CHOICES,
        'job_experiences': JobListing.EXPERIENCE_CHOICES,
        'job_preferences': JobListing.JOB_PREFERENCE_CHOICES,
        'selected_job_preferences': selected_job_preferences,
        'filtered': filtered,
        'active_filters': active_filters,
        'filter_remove_urls': filter_remove_urls,
        'show_filters': show_filters,
        'premium_plus_count': premium_plus_count,
        'premium_count': premium_count,
        'standard_count': standard_count,
    }
    
    # Return the appropriate template based on the request type
    template = 'core/job_list.html'
    
    return render(request, template, context)

def job_detail(request, job_id):
    """
    Display details for a specific job listing
    """
    # Use select_related to fetch employer in the same query
    job = get_object_or_404(JobListing.objects.select_related('employer'), id=job_id, status='approved')
    
    # Increment view count
    job.view_count += 1
    job.save(update_fields=['view_count'])
    
    # Get similar jobs based on category and experience, only show approved
    # Also order by premium level
    similar_jobs = JobListing.objects.filter(
        status='approved',
        category=job.category
    ).exclude(id=job_id).select_related('employer').order_by('-premium_level', '-posted_at')[:5]
    
    # Check if job is saved by user
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedJob.objects.filter(user=request.user, job=job).exists()
    
    # Check if job is expired
    is_expired = job.is_expired()
    
    # Calculate days until expiration
    days_until_expiration = job.days_until_expiration() if hasattr(job, 'days_until_expiration') else None
    
    context = {
        'job': job,
        'similar_jobs': similar_jobs,
        'is_saved': is_saved,
        'is_expired': is_expired,
        'days_until_expiration': days_until_expiration,
    }
    return render(request, 'core/job_detail.html', context)

def apply_job(request, job_id):
    """
    Handle job application submission
    """
    # Use select_related to fetch employer in the same query
    job = get_object_or_404(JobListing.objects.select_related('employer'), id=job_id, status='approved')
    
    # Check if job is expired
    if job.is_expired():
        messages.error(request, "This job posting has expired and is no longer accepting applications.")
        return redirect('job_detail', job_id=job.id)
    
    if request.method == 'POST':
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if user has already applied
            existing_application = JobApplication.objects.filter(
                job=job,
                user=request.user
            ).exists()
            
            if existing_application:
                messages.warning(request, "You have already applied for this job.")
                return redirect('job_detail', job_id=job.id)
            
            # Process form data
            cover_letter = request.POST.get('cover_letter', '')
            
            # For authenticated users with CV, resume is not required
            if request.user.userprofile.cv:
                # Create application with profile CV
                application = JobApplication.objects.create(
                    job=job,
                    user=request.user,
                    cover_letter=cover_letter,
                    resume=request.user.userprofile.cv
                )
            else:
                # For authenticated users without CV, resume is required
                resume_file = request.FILES.get('resume')
                if not resume_file:
                    messages.error(request, "Resume is required.")
                    return redirect('job_detail', job_id=job.id)
                
                # Create application with uploaded resume
                application = JobApplication.objects.create(
                    job=job,
                    user=request.user,
                    cover_letter=cover_letter,
                    resume=resume_file
                )
            
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('job_detail', job_id=job.id)
        else:
            # Process guest application
            guest_name = request.POST.get('guest_name', '')
            guest_email = request.POST.get('guest_email', '')
            cover_letter = request.POST.get('cover_letter', '')
            resume_file = request.FILES.get('resume')
            
            if not all([guest_name, guest_email, resume_file]):
                messages.error(request, "Name, email and resume are required for guest application.")
                return redirect('job_detail', job_id=job.id)
            
            # Create guest application
            application = JobApplication.objects.create(
                job=job,
                guest_name=guest_name,
                guest_email=guest_email,
                cover_letter=cover_letter,
                resume=resume_file
            )
            
            messages.success(request, "Your application has been submitted successfully! Consider creating an account for better job tracking.")
            return redirect('job_detail', job_id=job.id)
    
    # If not POST, redirect to job detail page
    return redirect('job_detail', job_id=job.id)

@login_required
def save_job(request, job_id):
    """
    Save a job for a user
    """
    if request.method == 'POST':
        job = get_object_or_404(JobListing, id=job_id, status='approved')
        saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
        
        if created:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Job saved successfully'})
            messages.success(request, 'Job saved successfully')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Job already saved'})
            messages.info(request, 'Job already saved')
            
        return redirect('job_detail', job_id=job_id)
    return redirect('job_list')

@login_required
def unsave_job(request, job_id):
    """
    Remove a saved job for a user
    """
    if request.method == 'POST':
        job = get_object_or_404(JobListing, id=job_id)
        saved_job = SavedJob.objects.filter(user=request.user, job=job)
        
        if saved_job.exists():
            saved_job.delete()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Job removed from saved jobs'})
            messages.success(request, 'Job removed from saved jobs')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Job was not saved'})
            messages.info(request, 'Job was not saved')
            
        return redirect('job_detail', job_id=job_id)
    return redirect('job_list') 