from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db.models import Prefetch, Q
from ..models import UserProfile, EmployerProfile, JobApplication, SavedJob, JobListing
from ..forms import UserProfileForm, EmployerProfileForm
import logging
import os
import tempfile
import traceback
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from jobsy.storage_backends import PrivateMediaStorage, PublicMediaStorage
import mimetypes
import boto3
from botocore.exceptions import ClientError
from django.utils import timezone

logger = logging.getLogger(__name__)

@login_required
def profile(request):
    """
    Display and manage user profile based on role
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get or create user profile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=request.user)
        user_profile.save()
    
    # Check if it's an AJAX request for CV upload
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Initialize form
    form = UserProfileForm(instance=user_profile)
    
    # Handle form submission
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'user_profile':
            form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            
            # Handle profile picture update for candidates
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                user_profile.profile_picture = profile_picture
                user_profile.save()
            
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({'success': True})
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
        
        elif form_type == 'employer_form' and user_profile.role == 'employer':
            employer_form = EmployerProfileForm(request.POST, request.FILES, instance=user_profile.employer_profile)
            
            # Also handle profile picture update
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                user_profile.profile_picture = profile_picture
                user_profile.save()
            
            if employer_form.is_valid():
                employer_form.save()
                messages.success(request, "Company profile updated successfully!")
                return redirect('profile')
    
    # Get filters from query params
    name_filter = request.GET.get('name', '')
    status_filter = request.GET.get('status', '')
    tab = request.GET.get('tab', 'profile')
    template_param = request.GET.get('template', '')
    
    # Get user's applications with proper joins
    applications = JobApplication.objects.filter(
        user=request.user
    ).select_related(
        'job',
        'job__employer'
    ).order_by('-applied_at')
    
    # Apply name filter if provided
    if name_filter:
        name_filter_q = Q(job__title__icontains=name_filter)
        # Also search in job_title for deleted jobs
        name_filter_q |= Q(job_title__icontains=name_filter)
        # Search in company name as well
        name_filter_q |= Q(job__company__icontains=name_filter)
        name_filter_q |= Q(job_company__icontains=name_filter)
        applications = applications.filter(name_filter_q)
    
    # Apply status filter if provided
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Get user's saved jobs with proper joins
    saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related(
        'job',
        'job__employer'
    ).order_by('-saved_at')
    
    # Determine if employer profile form should be shown
    is_employer = (user_profile.role == 'employer')
    employer_form = None
    if is_employer:
        try:
            employer_form = EmployerProfileForm(instance=user_profile.employer_profile)
        except EmployerProfile.DoesNotExist:
            pass
    
    context = {
        'user_profile': user_profile,
        'profile_form': form,
        'applications': applications,
        'saved_jobs': saved_jobs,
        'employer_form': employer_form,
        'active_tab': tab,
        'name_filter': name_filter,
        'status_filter': status_filter,
        'using_s3': hasattr(settings, 'USE_S3') and settings.USE_S3,
        'category_choices': JobListing.CATEGORY_CHOICES,
        'experience_choices': JobListing.EXPERIENCE_CHOICES,
    }
    
    # Choose template based on user role or template parameter
    if template_param == 'employer':
        template = 'core/employer_edit_profile.html'
    elif template_param == 'user':
        template = 'core/user_profile.html'
    elif is_employer:
        template = 'core/employer_edit_profile.html'
    else:
        template = 'core/user_profile.html'
    
    return render(request, template, context)

@login_required
@require_POST
def remove_cv(request):
    """
    Remove CV file from user profile and storage
    """
    try:
        # Get the user's profile
        user_profile = request.user.userprofile
        
        # Check if there is a CV to remove
        if not user_profile.cv:
            logger.warning(f"No CV found to remove for user {request.user.username}")
            return JsonResponse({'success': False, 'error': 'No CV found'}, status=400)
        
        # Get the CV file path
        cv_path = user_profile.cv.name
        logger.info(f"Attempting to remove CV: {cv_path} for user {request.user.username}")
        
        # Delete from storage (handling both S3 and local storage)
        try:
            if hasattr(settings, 'USE_S3') and settings.USE_S3:
                # For S3 storage
                logger.info(f"Using S3 storage to delete file: {cv_path}")
                storage = PrivateMediaStorage()
                if storage.exists(cv_path):
                    storage.delete(cv_path)
                    logger.info(f"Successfully deleted CV from S3: {cv_path}")
                else:
                    logger.warning(f"CV file not found in S3: {cv_path}")
            else:
                # For local storage
                logger.info(f"Using local storage to delete file")
                if default_storage.exists(cv_path):
                    default_storage.delete(cv_path)
                    logger.info(f"Successfully deleted CV from local storage: {cv_path}")
                else:
                    logger.warning(f"CV file not found in local storage: {cv_path}")
        except Exception as e:
            # Log the error but continue to update the profile
            logger.error(f"Error deleting CV file: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Update the profile fields regardless of delete success
        user_profile.cv = None
        user_profile.save(update_fields=['cv'])
        
        logger.info(f"CV successfully removed for user {request.user.username}")
        
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            return JsonResponse({'success': True, 'message': "CV removed successfully."})
        else:
            messages.success(request, "CV removed successfully.")
            return redirect('profile')
    except Exception as e:
        logger.error(f"Error removing CV: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def get_application_rejection_reasons(request, application_id):
    """API endpoint to get rejection reasons for an application"""
    # Get the application and verify ownership
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check if the application belongs to the current user
    if application.user != request.user:
        return JsonResponse({'error': 'You do not have permission to view this application'}, status=403)
    
    # Get rejection reasons with their display names
    reasons = [reason.get_name_display() for reason in application.rejection_reasons.all()]
    
    # Return as JSON
    return JsonResponse({
        'reasons': reasons,
        'feedback': application.feedback
    })

@login_required
@user_passes_test(lambda u: hasattr(u, 'userprofile') and u.userprofile.role == 'employer')
def view_cv_employer(request, profile_id):
    """
    Display a job seeker's CV to an employer
    Requires employer to have an active premium+ job
    """
    try:
        # Verify premium+ access
        employer_profile = request.user.userprofile.employer_profile
        has_premium_plus = JobListing.objects.filter(
            employer=employer_profile,
            premium_level='premium_plus',
            status='approved',
            deleted_at__isnull=True,
            expires_at__gt=timezone.now()  # Only count non-expired jobs
        ).exists()
        
        if not has_premium_plus:
            messages.error(request, "CV viewing is only available for employers with active Premium+ job listings.")
            return redirect('cv_database')
        
        # Get the profile
        user_profile = get_object_or_404(UserProfile, id=profile_id, role='candidate', visible_to_employers=True)
        
        # Check if CV exists
        if not user_profile.cv:
            messages.error(request, "This user has not uploaded a CV.")
            return redirect('cv_database')
        
        # Get the file path
        file_path = user_profile.cv.name
        file_name = os.path.basename(file_path)
        
        # Check if using S3
        if getattr(settings, 'USE_S3', False):
            # Generate a signed URL for the CV
            s3 = boto3.client(
                's3',
                region_name=settings.AWS_S3_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            
            try:
                # Generate a signed URL that expires in 1 hour (3600 seconds)
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': file_path,
                    },
                    ExpiresIn=3600
                )
                
                # Redirect to the signed URL
                return redirect(url)
            except ClientError as e:
                logger.error(f"Error generating S3 presigned URL: {str(e)}")
                raise e
        
        else:
            # Local storage case
            if default_storage.exists(file_path):
                # Get the file path
                file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
                
                # Open the file and create the response
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                response = HttpResponse(file_content, content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{file_name}"'
                return response
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
    
    except Exception as e:
        logger.error(f"Error displaying CV: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, f"Error displaying CV: {str(e)}")
        return redirect('cv_database')