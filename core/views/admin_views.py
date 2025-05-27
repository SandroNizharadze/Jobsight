from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from ..models import UserProfile, EmployerProfile
import logging
import secrets
import string

logger = logging.getLogger(__name__)

def is_admin(user):
    """
    Check if a user is an admin (superuser or has admin role)
    """
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')

@login_required
@user_passes_test(is_admin)
def assign_employer(request, user_id):
    """
    Assign employer role to a user
    """
    target_user = get_object_or_404(User, id=user_id)
    
    try:
        # Get or create user profile
        user_profile, created = UserProfile.objects.get_or_create(user=target_user)
        
        # Update role to employer
        user_profile.role = 'employer'
        user_profile.save()
        
        # This will automatically create an EmployerProfile through the signal in UserProfile.save()
        
        messages.success(request, f"User {target_user.username} has been assigned the employer role.")
    except Exception as e:
        logger.error(f"Error assigning employer role: {str(e)}")
        messages.error(request, f"Error assigning employer role: {str(e)}")
    
    # Redirect back to the admin page
    return redirect('admin:auth_user_change', object_id=user_id)

def create_admin(request, secret_key):
    """
    Create an admin user - this is used for initial setup or recovery
    """
    # Check secret key from environment variable
    from django.conf import settings
    import os
    
    # Get the admin creation key from environment or settings
    admin_key = os.environ.get('ADMIN_CREATION_KEY', '')
    
    if not admin_key or secret_key != admin_key:
        return JsonResponse({'error': 'Invalid key'}, status=403)
    
    try:
        # Generate a secure random password
        def generate_secure_password(length=16):
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
            return ''.join(secrets.choice(alphabet) for _ in range(length))
        
        secure_password = generate_secure_password()
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@jobsy.ge',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        
        if created:
            # Set password if it's a new user
            admin_user.set_password(secure_password)
            admin_user.save()
            message = "Admin user created successfully"
        else:
            # Update existing user to ensure they have admin privileges
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            message = "Admin user updated successfully (password unchanged)"
        
        # Ensure admin user has UserProfile with admin role
        admin_profile, profile_created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        
        if not profile_created and admin_profile.role != 'admin':
            admin_profile.role = 'admin'
            admin_profile.save()
        
        response_data = {
            'success': True, 
            'message': message,
            'username': admin_user.username,
            'login_url': request.build_absolute_uri(reverse('login'))
        }
        
        # Only include password in the response if a new user was created
        if created:
            response_data['password'] = secure_password
            response_data['note'] = "Please save this password securely. It will not be shown again."
        
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500) 