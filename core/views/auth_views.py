from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from ..forms import RegistrationForm, EmployerRegistrationForm
from ..models import UserProfile, EmployerProfile
from .email_views import send_verification_email
import logging
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

def is_employer(user):
    """
    Check if a user has employer role and associated employer profile
    """
    try:
        return (user.is_authenticated and 
                hasattr(user, 'userprofile') and 
                user.userprofile.role == 'employer' and
                hasattr(user.userprofile, 'employer_profile'))
    except:
        return False

def login_view(request):
    """Handle user login with email or username"""
    if request.user.is_authenticated:
        if is_employer(request.user):
            return redirect('employer_home')
        return redirect('job_list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with username (which is email in our case)
            user = authenticate(username=username, password=password)
            
            # If that fails, try to find user by email and authenticate with their username
            if user is None:
                try:
                    user_by_email = User.objects.get(email=username)
                    user = authenticate(username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    user = None
            
            if user is not None:
                # Email verification is now optional and doesn't affect login
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    # No verification check needed - allow login regardless of verification status
                except UserProfile.DoesNotExist:
                    # This shouldn't happen, but just in case
                    messages.error(request, "User profile not found.")
                    return render(request, 'core/login.html', {'form': form})
                
                # Ensure backend is set
                if not hasattr(user, 'backend'):
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                if is_employer(user):
                    return redirect('employer_home')
                return redirect('job_list')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('job_list')

def register(request):
    """Handle user registration for both candidates and employers"""
    if request.user.is_authenticated:
        return redirect('job_list')
    
    # Check for user_type in the query parameters and set default form values
    default_user_type = request.GET.get('user_type', 'candidate')
    
    if request.method == 'POST':
        # Get user_type directly from POST data 
        user_type = request.POST.get('user_type', 'candidate')
        logger.info(f"Registration attempt with user_type: {user_type}")
        
        # Override ROLE based on user selection - this is crucial
        if user_type not in ['candidate', 'employer']:
            user_type = 'candidate'  # Default to candidate if invalid value
            logger.warning(f"Invalid user_type detected, defaulting to candidate")
        
        # We'll use a transaction to ensure everything happens atomically
        from django.db import transaction
        
        form = RegistrationForm(request.POST)
        employer_form = None
        
        if user_type == 'employer':
            employer_form = EmployerRegistrationForm(request.POST)
            
            logger.info(f"Processing employer registration")
            
            if form.is_valid() and employer_form.is_valid():
                try:
                    with transaction.atomic():
                        # Create the user first
                        user = form.save()
                        logger.info(f"Created user {user.username} (email: {user.email})")
                        
                        # Use the updated helper method to safely create/update profiles
                        # This handles any possible race conditions with signals
                        # First check if a UserProfile exists before calling create_for_user
                        if UserProfile.objects.filter(user=user).exists():
                            # If a profile exists but is not an employer, update it
                            profile = UserProfile.objects.get(user=user)
                            if profile.role != 'employer':
                                profile.role = 'employer'
                                profile.save()
                                logger.info(f"Updated existing profile for {user.username} to employer role")
                            
                            # Save email notification preference
                            profile.email_notifications = form.cleaned_data.get('email_notifications', False)
                            profile.save()
                                
                            # Now ensure an employer profile exists with our data
                            employer_profile, created = EmployerProfile.objects.get_or_create(
                                user_profile=profile,
                                defaults={
                                    'company_name': employer_form.cleaned_data.get('company_name'),
                                    'company_id': employer_form.cleaned_data.get('company_id'),
                                    'phone_number': employer_form.cleaned_data.get('phone_number')
                                }
                            )
                            if not created:
                                # Update existing employer profile
                                employer_profile.company_name = employer_form.cleaned_data.get('company_name')
                                employer_profile.company_id = employer_form.cleaned_data.get('company_id')
                                employer_profile.phone_number = employer_form.cleaned_data.get('phone_number')
                                employer_profile.save()
                            logger.info(f"{'Created' if created else 'Updated'} employer profile for {user.username}")
                        else:
                            # No profile exists, use our helper method
                            employer_profile = EmployerProfile.create_for_user(
                                user=user,
                                company_name=employer_form.cleaned_data.get('company_name'),
                                company_id=employer_form.cleaned_data.get('company_id'),
                                phone_number=employer_form.cleaned_data.get('phone_number')
                            )
                            # Save email notification preference
                            employer_profile.user_profile.email_notifications = form.cleaned_data.get('email_notifications', False)
                            employer_profile.user_profile.save()
                            
                            logger.info(f"Created new employer profile for {user.username}")
                            
                        # Verify the role was set correctly
                        user.refresh_from_db()
                        logger.info(f"Final role check: User {user.username} has role {user.userprofile.role}")
                        
                        # Send verification email
                        send_verification_email(request, user)
                        
                        # Log in the user
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user)
                        
                        # Final verification after login
                        logger.info(f"After login: User {user.username} has role {user.userprofile.role}")
                        
                        messages.success(request, _("Registration successful! Please check your email to verify your account."))
                        return redirect('job_list')
                except Exception as e:
                    logger.error(f"Error during registration: {str(e)}", exc_info=True)
                    messages.error(request, _("An error occurred during registration. Please try again."))
                    return render(request, 'core/register.html', {'form': form, 'employer_form': employer_form})
            else:
                messages.error(request, _("Please correct the errors below."))
        else:
            # Regular candidate registration
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Create the user
                        user = form.save()
                        logger.info(f"Created candidate user {user.username}")
                        
                        # Create or get UserProfile with candidate role
                        profile, created = UserProfile.objects.get_or_create(
                            user=user,
                            defaults={
                                'role': 'candidate',
                                'email_notifications': form.cleaned_data.get('email_notifications', False)
                            }
                        )
                        
                        # Make sure the role is set to candidate regardless
                        if not created:
                            profile.role = 'candidate'
                            profile.email_notifications = form.cleaned_data.get('email_notifications', False)
                            profile.save()
                            
                        logger.info(f"{'Created' if created else 'Using existing'} UserProfile with role 'candidate' for {user.username}")
                        
                        # Send verification email
                        send_verification_email(request, user)
                        
                        # Log in the user
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user)
                        
                        # Final verification after login
                        logger.info(f"After login: User {user.username} has role {user.userprofile.role}")
                        
                        messages.success(request, _("Registration successful! Please check your email to verify your account."))
                        return redirect('job_list')
                except Exception as e:
                    logger.error(f"Error during candidate registration: {str(e)}", exc_info=True)
                    messages.error(request, _("An error occurred during registration. Please try again."))
                    return render(request, 'core/register.html', {'form': form, 'employer_form': None})
            else:
                messages.error(request, _("Please correct the errors below."))
    else:
        form = RegistrationForm()
        employer_form = EmployerRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form, 'employer_form': employer_form})


@login_required
@require_http_methods(["GET"])
def session_status(request):
    """
    API endpoint to check session status and return time until expiry
    """
    try:
        # Get session expiry time
        session_expiry = request.session.get_expiry_date()
        if session_expiry:
            # Calculate seconds until expiry
            now = timezone.now()
            if session_expiry.tzinfo is None:
                session_expiry = timezone.make_aware(session_expiry)
            
            seconds_until_expiry = int((session_expiry - now).total_seconds())
            
            return JsonResponse({
                'session_expires_in': max(0, seconds_until_expiry),
                'session_expiry_date': session_expiry.isoformat(),
                'is_active': seconds_until_expiry > 0
            })
        else:
            return JsonResponse({
                'session_expires_in': None,
                'session_expiry_date': None,
                'is_active': True
            })
    except Exception as e:
        logger.error(f"Error checking session status: {str(e)}")
        return JsonResponse({'error': 'Failed to check session status'}, status=500)


@login_required
@require_http_methods(["POST"])
def extend_session(request):
    """
    API endpoint to extend the current session
    """
    try:
        # Update session expiry by accessing it (this triggers SESSION_SAVE_EVERY_REQUEST)
        request.session.modified = True
        
        # Get new expiry time
        session_expiry = request.session.get_expiry_date()
        if session_expiry:
            now = timezone.now()
            if session_expiry.tzinfo is None:
                session_expiry = timezone.make_aware(session_expiry)
            
            seconds_until_expiry = int((session_expiry - now).total_seconds())
            
            return JsonResponse({
                'success': True,
                'session_expires_in': max(0, seconds_until_expiry),
                'session_expiry_date': session_expiry.isoformat()
            })
        else:
            return JsonResponse({
                'success': True,
                'session_expires_in': None,
                'session_expiry_date': None
            })
    except Exception as e:
        logger.error(f"Error extending session: {str(e)}")
        return JsonResponse({'error': 'Failed to extend session'}, status=500) 