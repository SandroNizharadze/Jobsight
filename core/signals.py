from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import logging
import os
import secrets
import string

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile for a User if it doesn't already exist.
    This signal is a safety net for any user creation that doesn't explicitly
    create a UserProfile. The registration view should handle profile creation directly.
    """
    if created:
        # Use get_or_create to be absolutely sure we don't create duplicates
        try:
            # First check if a profile already exists to avoid transaction conflicts
            if UserProfile.objects.filter(user=instance).exists():
                logger.info(f"Signal: UserProfile already exists for {instance.username}, not creating a new one")
                return
                
            # Create a default profile if none exists
            profile, created = UserProfile.objects.get_or_create(
                user=instance,
                defaults={'role': 'candidate'}
            )
            if created:
                logger.info(f"Signal: Created default UserProfile for new user {instance.username}")
            else:
                logger.info(f"Signal: Found existing UserProfile for {instance.username}")
        except Exception as e:
            logger.error(f"Signal: Error creating UserProfile: {str(e)}")
            # Don't raise the exception - we don't want to break user creation
            # if profile creation fails

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the UserProfile when the User is saved.
    """
    if hasattr(instance, 'userprofile'):
        logger.info(f"Signal: Saving existing UserProfile for {instance.username} with role {instance.userprofile.role}")
        instance.userprofile.save()
    else:
        logger.warning(f"Signal: User {instance.username} has no UserProfile, this is unexpected")

def generate_secure_password(length=16):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Ensure admin user/profile exists after migrations
@receiver(post_migrate)
def ensure_admin_user(sender, **kwargs):
    # Skip admin creation in non-development environments unless explicitly enabled
    if os.environ.get('DISABLE_AUTO_ADMIN_CREATION', 'False') == 'True':
        return
    
    from django.contrib.auth.models import User
    from .models import UserProfile
    
    admin_username = os.environ.get('AUTO_ADMIN_USERNAME', 'admin')
    admin_email = os.environ.get('AUTO_ADMIN_EMAIL', 'admin@example.com')
    
    # Only set password for new users, use environment variable or generate a secure one
    admin_password = os.environ.get('AUTO_ADMIN_PASSWORD')
    if not admin_password:
        admin_password = generate_secure_password()
    
    try:
        admin_user, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': admin_email,
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password(admin_password)
            admin_user.save()
            print(f"Admin user '{admin_username}' created.")
            print(f"IMPORTANT: Admin password is '{admin_password}' - please save this somewhere secure!")
            print("This password will not be shown again.")
        else:
            # Only update privileges, not password for existing users
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            print(f"Admin user '{admin_username}' privileges ensured.")
        
        # Ensure UserProfile exists
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        print(f"UserProfile for '{admin_username}' ensured.")
    except Exception as e:
        print(f"Error managing admin user: {e}")