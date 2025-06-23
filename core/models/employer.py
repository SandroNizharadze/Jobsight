from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from core.models.base import SoftDeletionModel

# Import storage backends if S3 is enabled
if hasattr(settings, 'USE_S3') and settings.USE_S3:
    from jobsy.storage_backends import PublicMediaStorage, PrivateMediaStorage
else:
    PublicMediaStorage = None
    PrivateMediaStorage = None

class EmployerProfile(SoftDeletionModel):
    COMPANY_SIZE_CHOICES = [
        ('1-10', _('1-10 employees')),
        ('11-50', _('11-50 employees')),
        ('51-200', _('51-200 employees')),
        ('201-500', _('201-500 employees')),
        ('501-1000', _('501-1000 employees')),
        ('1001+', _('1001+ employees')),
    ]
    
    user_profile = models.OneToOneField('UserProfile', on_delete=models.CASCADE, related_name='employer_profile', verbose_name=_("მომხმარებლის პროფილი"))
    company_name = models.CharField(max_length=100, blank=True, db_index=True, verbose_name=_("კომპანიის დასახელება"))
    company_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("საიდენტიფიკაციო კოდი"))
    phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("მობილურის ნომერი"))
    show_phone_number = models.BooleanField(default=False, verbose_name=_("გამოჩნდეს ტელეფონის ნომერი პროფილზე"))
    company_website = models.URLField(blank=True, verbose_name=_("კომპანიის ვებსაიტი"))
    company_description = RichTextField(blank=True, verbose_name=_("კომპანიის აღწერა"))
    
    # Use PublicMediaStorage for company logos when S3 is enabled
    if PublicMediaStorage:
        company_logo = models.ImageField(
            upload_to='company_logos/', 
            storage=PublicMediaStorage(),
            blank=True, 
            null=True, 
            verbose_name=_("კომპანიის ლოგო")
        )
    else:
        company_logo = models.ImageField(
            upload_to='company_logos/', 
            blank=True, 
            null=True, 
            verbose_name=_("კომპანიის ლოგო")
        )
    
    company_size = models.CharField(max_length=50, choices=COMPANY_SIZE_CHOICES, blank=True, verbose_name=_("კომპანიის ზომა"))
    industry = models.CharField(max_length=100, blank=True, db_index=True, verbose_name=_("ინდუსტრია"))
    location = models.CharField(max_length=100, blank=True, db_index=True, verbose_name=_("მდებარეობა"))
    has_cv_database_access = models.BooleanField(default=False, verbose_name=_("წვდომა სივების ბაზაზე"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("შექმნის თარიღი"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("განახლების თარიღი"))
    
    def __str__(self):
        return f"{self.company_name} ({self.user_profile.user.username})"
    
    def save(self, *args, **kwargs):
        # Ensure company_description is properly handled for Georgian characters
        if self.company_description and isinstance(self.company_description, str):
            # Handle potential encoding issues with Georgian characters
            try:
                # Try to ensure the text is properly encoded
                self.company_description = self.company_description.encode('utf-8').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                # If there's an encoding issue, try to fix it or log the error
                pass
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("დამსაქმებლის პროფილი")
        verbose_name_plural = _("დამსაქმებლების პროფილები")
    
    @classmethod
    def create_for_user(cls, user, company_name="", company_id=None, phone_number=None):
        """
        Create an employer profile for a user, setting the role to 'employer'
        """
        from core.models import UserProfile
        
        # Ensure user has a profile
        try:
            user_profile = user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user)
        
        # Set role to employer
        user_profile.role = 'employer'
        user_profile.save()
        
        # Create employer profile if it doesn't exist
        employer_profile, created = cls.objects.get_or_create(
            user_profile=user_profile,
            defaults={
                'company_name': company_name,
                'company_id': company_id,
                'phone_number': phone_number
            }
        )
        
        return employer_profile


@receiver(post_save, sender='core.UserProfile')
def ensure_employer_profile(sender, instance, created, **kwargs):
    """
    Ensure that users with employer role have an employer profile
    """
    if instance.role == 'employer':
        # Import here to avoid circular import
        from core.models import EmployerProfile
        
        # Check if employer profile exists
        if not hasattr(instance, 'employer_profile'):
            # Create employer profile
            EmployerProfile.objects.create(user_profile=instance) 