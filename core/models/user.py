from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_ckeditor_5.fields import CKEditor5Field

# Import storage backends if S3 is enabled
if hasattr(settings, 'USE_S3') and settings.USE_S3:
    from jobsy.storage_backends import PublicMediaStorage, PrivateMediaStorage
else:
    PublicMediaStorage = None
    PrivateMediaStorage = None

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('candidate', _('Candidate')),
        ('employer', _('Employer')),
        ('admin', _('Admin')),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("მომხმარებელი"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate', db_index=True, verbose_name=_("როლი"))
    is_email_verified = models.BooleanField(default=False, verbose_name=_("ელ-ფოსტა დადასტურებულია"))
    
    # Field for email notifications consent
    email_notifications = models.BooleanField(default=False, verbose_name=_("თანახმა ვარ მივიღო ელ-ფოსტის შეტყობინებები"))
    
    # Use PublicMediaStorage for profile pictures when S3 is enabled
    if PublicMediaStorage:
        profile_picture = models.ImageField(
            upload_to='profile_pictures/', 
            storage=PublicMediaStorage(),
            blank=True, 
            null=True, 
            verbose_name=_("პროფილის სურათი")
        )
    else:
        profile_picture = models.ImageField(
            upload_to='profile_pictures/', 
            blank=True, 
            null=True, 
            verbose_name=_("პროფილის სურათი")
        )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("შექმნის თარიღი"))
    
    # CV field - always use PrivateMediaStorage to ensure S3 storage regardless of USE_S3 setting
    if PrivateMediaStorage:
        cv = models.FileField(
            upload_to='cvs/', 
            storage=PrivateMediaStorage(),
            blank=True, 
            null=True, 
            verbose_name=_("CV")
        )
    else:
        cv = models.FileField(
            upload_to='cvs/',
            blank=True,
            null=True,
            verbose_name=_("CV")
        )
    
    # New fields for CV database functionality
    desired_field = models.CharField(
        max_length=100, 
        choices=[], # This will be set to JobListing.CATEGORY_CHOICES in __init__.py
        blank=True, 
        null=True, 
        verbose_name=_("სასურველი სფერო")
    )
    field_experience = models.CharField(
        max_length=100, 
        choices=[], # This will be set to JobListing.EXPERIENCE_CHOICES in __init__.py
        blank=True, 
        null=True, 
        verbose_name=_("გამოცდილება")
    )
    visible_to_employers = models.BooleanField(
        default=False,
        verbose_name=_("ხილვადია დამსაქმებლებისთვის")
    )
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def is_profile_complete(self):
        """Check if the user profile has all required fields filled in"""
        return bool(self.user.first_name and self.user.last_name and self.user.email)
    
    def save(self, *args, **kwargs):
        # If this is a new profile, set role based on email domain
        if not self.pk:
            email = self.user.email.lower()
            # Check if the email is from an admin domain
            admin_domains = getattr(settings, 'ADMIN_EMAIL_DOMAINS', [])
            if any(email.endswith(domain) for domain in admin_domains):
                self.role = 'admin'
        
        # If user is superuser, ensure they have admin role
        if self.user.is_superuser and self.role != 'admin':
            self.role = 'admin'
            
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("მომხმარებლის პროფილი")
        verbose_name_plural = _("მომხმარებლების პროფილები")


# Signal to create user profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance) 