# This file is maintained for backward compatibility
# The actual models have been moved to the core/models/ directory

from core.models.base import SoftDeletionModel, SoftDeletionQuerySet, SoftDeletionManager
from core.models.job import JobListing, RejectionReason
from core.models.user import UserProfile
from core.models.employer import EmployerProfile
from core.models.application import JobApplication, SavedJob, CVAccess
from core.models.blog import BlogPost, BlogCategory, BlogPostCategory
from core.models.pricing import PricingPackage, PricingFeature, ComparisonTable, ComparisonRow
from core.models.auth import EmailVerificationToken
from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

# For backward compatibility, expose all models at the module level
__all__ = [
    'SoftDeletionModel', 'SoftDeletionQuerySet', 'SoftDeletionManager',
    'JobListing', 'RejectionReason',
    'UserProfile', 'EmployerProfile',
    'JobApplication', 'SavedJob', 'CVAccess',
    'BlogPost', 'BlogCategory', 'BlogPostCategory',
    'PricingPackage', 'PricingFeature', 'ComparisonTable', 'ComparisonRow',
    'EmailVerificationToken',
]

class StaticPage(models.Model):
    PRIVACY_POLICY = 'privacy_policy'
    TERMS_CONDITIONS = 'terms_conditions'
    
    PAGE_TYPES = [
        (PRIVACY_POLICY, _('Privacy Policy')),
        (TERMS_CONDITIONS, _('Terms & Conditions')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    page_type = models.CharField(
        _('Page Type'),
        max_length=50,
        choices=PAGE_TYPES,
        unique=True
    )
    content = RichTextField(_('Content'))
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True)
    
    class Meta:
        verbose_name = _('Static Page')
        verbose_name_plural = _('Static Pages')
    
    def __str__(self):
        return self.title

class RejectionReason(models.Model):
    """
    Predefined reasons for rejecting a job application
    """
    REASON_CHOICES = [
        ('არასაკმარისი_კვალიფიკაცია', 'არასაკმარისი კვალიფიკაცია'),
        ('გამოცდილების_ნაკლებობა', 'გამოცდილების ნაკლებობა'),
        ('უნარების_შეუსაბამობა', 'უნარების შეუსაბამობა'),
        ('სხვა_კანდიდატი_შეირჩა', 'სხვა კანდიდატი შეირჩა'),
        ('პოზიცია_შეივსო', 'პოზიცია შეივსო'),
        ('ანაზღაურების_მოლოდინები', 'ანაზღაურების მოლოდინები'),
        ('კომუნიკაციის_პრობლემები', 'კომუნიკაციის პრობლემები'),
        ('პოზიცია_გაუქმდა', 'პოზიცია გაუქმდა'),
    ]
    
    reason = models.CharField(max_length=100, choices=REASON_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_reason_display()

class JobApplication(models.Model):
    """
    Job application model for both registered users and guest applicants
    """
    STATUS_CHOICES = [
        ('განხილვის_პროცესში', 'განხილვის პროცესში'),
        ('გასაუბრება', 'გასაუბრება'),
        ('რეზერვი', 'რეზერვი'),
    ]
    
    # Common fields for both registered and guest users
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='განხილვის_პროცესში')
    applied_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)
    rejection_reasons = models.ManyToManyField(RejectionReason, blank=True)
    
    # Registered user fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='applications')
    
    # Guest applicant fields
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    guest_phone = models.CharField(max_length=50, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_at']
        
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()} - {self.job.title}"
        return f"{self.guest_name} - {self.job.title}"
    
    def is_guest_application(self):
        return self.user is None