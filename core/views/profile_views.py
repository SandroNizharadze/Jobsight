from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse, FileResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.db.models import Prefetch, Q
from ..models import UserProfile, EmployerProfile, JobApplication, SavedJob, JobListing, CVAccess
from ..forms import UserProfileForm, EmployerProfileForm
from django.utils.translation import gettext_lazy as _
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
from django.contrib.auth import logout
import uuid
from core.repositories.employer_repository import EmployerRepository
from core.repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

@login_required
def profile(request):
    """
    View for user profile page
    """
    user_profile = request.user.userprofile
    
    # Handle form submission
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form_type == 'user_profile':
            # Get first_name and last_name from the form
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            
            # Update User model fields
            if first_name or last_name:
                user = request.user
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                user.save(update_fields=['first_name', 'last_name'])
            
            # Handle regular form submission for UserProfile
            form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                if is_ajax:
                    return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
                messages.success(request, _("Profile updated successfully"))
                return redirect(request.path_info + ('?tab=settings' if request.GET.get('tab') == 'settings' else ''))
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'errors': form.errors})
                messages.error(request, _("Error updating profile. Please check the form and try again."))
        
        elif form_type == 'cv_settings':
            # Handle CV settings form submission
            desired_field = request.POST.get('desired_field', '')
            field_experience = request.POST.get('field_experience', '')
            visible_to_employers = request.POST.get('visible_to_employers') == 'on'
            
            # Update user profile
            user_profile.desired_field = desired_field
            user_profile.field_experience = field_experience
            user_profile.visible_to_employers = visible_to_employers
            user_profile.save(update_fields=['desired_field', 'field_experience', 'visible_to_employers'])
            
            messages.success(request, _("Settings saved successfully"), extra_tags='settings_saved')
            return redirect(request.path_info + ('?tab=profile' if not request.GET.get('tab') else ''))
        
        # If not AJAX, continue to render the page with the updated form
    else:
        form = UserProfileForm(instance=user_profile)
    
    # Get tab from URL parameter
    tab = request.GET.get('tab', '')
    template_param = request.GET.get('template', '')
    
    # Get filters for applications
    name_filter = request.GET.get('name', '')
    status_filter = request.GET.get('status', '')
    
    # Get applications with proper joins
    applications = JobApplication.objects.filter(
        user=request.user
    ).select_related(
        'job',
        'job__employer'
    ).order_by('-applied_at')
    
    # Apply filters if provided
    if name_filter:
        applications = applications.filter(job__title__icontains=name_filter)
    
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
    
    # If tab is applications or saved_jobs and user is a candidate, mark notifications as read
    if user_profile.role == 'candidate' and tab in ['applications', 'saved_jobs'] and tab == 'applications':
        NotificationRepository.mark_all_candidate_notifications_as_read(request.user)
    
    context = {
        'user_profile': user_profile,
        'profile_form': form,
        'applications': applications,
        'saved_jobs': saved_jobs,
        'employer_form': employer_form,
        'active_tab': tab or 'profile',
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
        if tab == 'applications':
            template = 'core/user_profile_applications.html'
        elif tab == 'saved_jobs':
            template = 'core/user_profile_saved_jobs.html'
        elif tab == 'settings':
            template = 'core/user_profile_settings.html'
        else:
            template = 'core/user_profile_cv.html'
    elif is_employer:
        template = 'core/employer_edit_profile.html'
    else:
        if tab == 'applications':
            template = 'core/user_profile_applications.html'
        elif tab == 'saved_jobs':
            template = 'core/user_profile_saved_jobs.html'
        elif tab == 'settings':
            template = 'core/user_profile_settings.html'
        else:
            template = 'core/user_profile_cv.html'
    
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
    
    # Get rejection reasons names
    reasons = [reason.name for reason in application.rejection_reasons.all()]
    
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
    Requires employer to have direct CV database access
    """
    try:
        # Verify access
        employer_profile = request.user.userprofile.employer_profile
        
        # Check if employer has direct access to CV database
        has_direct_access = employer_profile.has_cv_database_access
        
        if not has_direct_access:
            messages.error(request, _("You don't have access to view candidate CVs. Please purchase CV database access."))
            return redirect('employer_dashboard')
            
        # Get the profile
        profile = get_object_or_404(UserProfile, pk=profile_id, visible_to_employers=True)
        
        # Check if CV exists
        if not profile.cv:
            messages.error(request, _("This candidate doesn't have a CV uploaded."))
            return redirect('cv_database')
        
        # Log this access
        EmployerRepository.track_cv_access(employer_profile, profile)
        
        # Update application status to "ნანახი" if currently in "განხილვის_პროცესში" state
        if hasattr(profile, 'user'):
            applications = JobApplication.objects.filter(
                user=profile.user,
                job__employer=employer_profile,
                is_viewed=False
            )
            
            for application in applications:
                application.is_viewed = True
                application.save(update_fields=['is_viewed'])
                logger.info(f"Marked application {application.id} as viewed for user {profile.user.id}")
        
        # Get the CV file
        cv_file = profile.cv
        
        # Get the file name
        file_name = os.path.basename(cv_file.name)
        
        # Check if using S3
        if settings.USE_S3:
            try:
                # For S3 storage, we need to create a signed URL
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                # The key should be the full path in S3
                # If the path already has media/private/ prefix, use it directly
                if cv_file.name.startswith('media/private/'):
                    s3_key = cv_file.name
                else:
                    s3_key = f"media/private/{cv_file.name}"
                
                # Generate a signed URL
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                        'Key': s3_key
                    },
                    ExpiresIn=3600  # URL expires in 1 hour
                )
                
                # Redirect to the signed URL
                return redirect(url)
                
            except Exception as e:
                logging.error(f"Error generating S3 signed URL: {str(e)}")
                logging.error(traceback.format_exc())
                messages.error(request, _("Error accessing the CV file. Please try again later."))
                return redirect('cv_database')
        else:
            # For local storage
            try:
                # Open the file and serve it
                response = FileResponse(cv_file.open('rb'))
                content_type, encoding = mimetypes.guess_type(file_name)
                if content_type:
                    response['Content-Type'] = content_type
                response['Content-Disposition'] = f'inline; filename="{file_name}"'
                return response
            except Exception as e:
                logging.error(f"Error serving local CV file: {str(e)}")
                messages.error(request, _("Error accessing the CV file. Please try again later."))
                return redirect('cv_database')
                
    except Exception as e:
        logging.error(f"Error in view_cv_employer: {str(e)}")
        logging.error(traceback.format_exc())
        messages.error(request, _("An error occurred. Please try again later."))
        return redirect('employer_dashboard')

@login_required
@require_POST
def delete_account(request):
    """
    Delete user account by anonymizing personal data and removing files
    """
    try:
        user = request.user
        
        # Get confirmation from the form
        confirmation = request.POST.get('confirmation', '').lower()
        if confirmation != 'delete':
            messages.error(request, _("Please type 'delete' to confirm account deletion."))
            return redirect('profile')
        
        # Check if user has a profile
        try:
            user_profile = user.userprofile
            is_employer = user_profile.role == 'employer'
            
            # Remove CV file if exists
            if user_profile.cv:
                # Get the CV file path
                cv_path = user_profile.cv.name
                logger.info(f"Removing CV for deleted account: {cv_path}")
                
                try:
                    if hasattr(settings, 'USE_S3') and settings.USE_S3:
                        # For S3 storage
                        storage = PrivateMediaStorage()
                        if storage.exists(cv_path):
                            storage.delete(cv_path)
                    else:
                        # For local storage
                        if default_storage.exists(cv_path):
                            default_storage.delete(cv_path)
                except Exception as e:
                    logger.error(f"Error deleting CV file during account deletion: {str(e)}")
                
                # Clear CV field
                user_profile.cv = None
            
            # Remove profile picture if exists
            if user_profile.profile_picture:
                try:
                    picture_path = user_profile.profile_picture.name
                    logger.info(f"Removing profile picture for deleted account: {picture_path}")
                    
                    if hasattr(settings, 'USE_S3') and settings.USE_S3:
                        storage = PublicMediaStorage()
                        if storage.exists(picture_path):
                            storage.delete(picture_path)
                    else:
                        if default_storage.exists(picture_path):
                            default_storage.delete(picture_path)
                    
                    user_profile.profile_picture = None
                except Exception as e:
                    logger.error(f"Error deleting profile picture during account deletion: {str(e)}")
            
            # Handle employer-specific data if applicable
            if is_employer and hasattr(user_profile, 'employer_profile'):
                employer_profile = user_profile.employer_profile
                
                # Remove company logo if exists
                if employer_profile.company_logo:
                    try:
                        logo_path = employer_profile.company_logo.name
                        logger.info(f"Removing company logo for deleted account: {logo_path}")
                        
                        if hasattr(settings, 'USE_S3') and settings.USE_S3:
                            storage = PublicMediaStorage()
                            if storage.exists(logo_path):
                                storage.delete(logo_path)
                        else:
                            if default_storage.exists(logo_path):
                                default_storage.delete(logo_path)
                        
                        employer_profile.company_logo = None
                    except Exception as e:
                        logger.error(f"Error deleting company logo during account deletion: {str(e)}")
                
                # Anonymize employer profile data
                employer_profile.company_name = f"Deleted Employer {uuid.uuid4().hex[:8]}"
                employer_profile.company_id = None
                employer_profile.phone_number = None
                employer_profile.company_website = None
                employer_profile.company_description = None
                employer_profile.save()
            
            # Anonymize user data
            user.email = f"deleted_{uuid.uuid4().hex[:8]}@deleted.user"
            user.first_name = "Deleted"
            user.last_name = "User"
            user.username = f"deleted_user_{uuid.uuid4().hex[:8]}"
            user.set_unusable_password()
            user.save()
            
            # Save profile changes
            user_profile.save()
            
            # Log the user out
            logout(request)
            
            messages.success(request, _("Your account has been successfully deleted. All personal information has been removed."))
            return redirect('login')
            
        except UserProfile.DoesNotExist:
            logger.error(f"Attempted to delete account without profile: {user.username}")
            messages.error(request, _("Error: User profile not found."))
            return redirect('profile')
            
    except Exception as e:
        logger.error(f"Error during account deletion: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, _("An error occurred while deleting your account. Please try again or contact support."))
        return redirect('profile')

@login_required
@require_POST
def update_employer_profile(request):
    """
    Special view to handle employer profile updates with Georgian text
    """
    try:
        # Get user profile
        user_profile = request.user.userprofile
        
        # Ensure user is an employer
        if user_profile.role != 'employer':
            messages.error(request, "Only employers can update company profiles.")
            return redirect('profile')
        
        # Get employer profile
        try:
            employer_profile = user_profile.employer_profile
        except EmployerProfile.DoesNotExist:
            messages.error(request, "Employer profile not found.")
            return redirect('profile')
        
        # Process the form data
        form = EmployerProfileForm(request.POST, request.FILES, instance=employer_profile)
        
        # Handle profile picture update
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            user_profile.profile_picture = profile_picture
            user_profile.save()
        
        # Get the company description directly from the form
        company_description = request.POST.get('company_description', '')
        
        # Log the company description
        logger.info(f"Company description: {company_description[:100]}...")
        
        if form.is_valid():
            # Save form but don't commit yet
            profile = form.save(commit=False)
            
            # Use our processed company description
            if company_description:
                profile.company_description = company_description
            
            # Save the profile
            profile.save()
            
            messages.success(request, "Company profile updated successfully!")
        else:
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, "Error updating company profile. Please check the form and try again.")
        
        return redirect('profile')
    
    except Exception as e:
        logger.error(f"Error in update_employer_profile: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, "An error occurred while updating your profile.")
        return redirect('profile')

@login_required
def mark_candidate_notifications_as_read(request):
    """
    Mark all notifications as read for the candidate
    """
    if request.user.userprofile.role != 'candidate':
        return HttpResponseForbidden("Access denied")
    
    count = NotificationRepository.mark_all_candidate_notifications_as_read(request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'count': count})
    
    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def mark_candidate_notification_as_read(request, notification_id):
    """
    Mark a specific notification as read
    """
    if request.user.userprofile.role != 'candidate':
        return HttpResponseForbidden("Access denied")
    
    success = NotificationRepository.mark_candidate_notification_as_read(notification_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': success})
    
    # Redirect back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'profile'))