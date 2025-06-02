from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Prefetch, Q
from ..models import UserProfile, EmployerProfile, JobApplication, SavedJob, JobListing, CVAccess
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
    Requires employer to have an active premium+ job or direct CV database access
    """
    try:
        # Verify access
        employer_profile = request.user.userprofile.employer_profile
        
        # Check if employer has direct access to CV database
        has_direct_access = employer_profile.has_cv_database_access
        
        # Check if employer has premium+ access
        has_premium_plus = JobListing.objects.filter(
            employer=employer_profile,
            premium_level='premium_plus',
            status='active',
            is_approved=True
        ).exists()
        
        if not (has_direct_access or has_premium_plus):
            messages.error(request, _("You don't have access to view candidate CVs. Please upgrade your subscription."))
            return redirect('employer_dashboard')
        
        # Get the profile
        profile = get_object_or_404(UserProfile, id=profile_id, visible_to_employers=True)
        
        # Check if profile has a CV
        if not profile.cv:
            messages.error(request, _("This candidate doesn't have a CV uploaded."))
            return redirect('cv_database')
        
        # Log this access for analytics
        CVAccess.objects.create(
            employer_profile=employer_profile,
            candidate_profile=profile
        )
        
        # Get the CV file
        cv_file = profile.cv
        
        # For S3 storage, generate a signed URL
        if settings.USE_S3:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            try:
                # Get the file key - remove any leading slash
                file_key = profile.cv.name
                if file_key.startswith('/'):
                    file_key = file_key[1:]
                
                # If the path doesn't include the media/private prefix needed for S3, add it
                if not file_key.startswith('media/private/'):
                    # Check for duplicate 'cvs/' in the path and fix it
                    if file_key.startswith('cvs/cvs/'):
                        file_key = file_key[4:]  # Remove the first 'cvs/'
                    
                    file_key = f'media/private/{file_key}'
                
                # Log the file key for debugging
                logger.info(f"Accessing S3 file with key: {file_key}")
                
                # Generate a signed URL that expires in 1 hour
                response = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': file_key
                    },
                    ExpiresIn=3600  # URL valid for 1 hour
                )
                
                # Redirect to the signed URL
                return redirect(response)
                
            except ClientError as e:
                logger.error(f"Error generating signed URL: {str(e)}")
                messages.error(request, _("There was an error accessing the CV file."))
                return redirect('cv_database')
        
        # For local storage, serve the file directly
        else:
            # Get the file path
            file_path = profile.cv.path
            
            # Check if file exists
            if not os.path.exists(file_path):
                messages.error(request, _("CV file not found."))
                return redirect('cv_database')
                
            # Serve the file
            return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            
    except Exception as e:
        logger.error(f"Error in view_cv_employer: {str(e)}")
        messages.error(request, _("An error occurred while trying to access the CV."))
        return redirect('cv_database')