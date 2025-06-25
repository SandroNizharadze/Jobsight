# This file is maintained for backward compatibility
# The actual models have been moved to the core/models/ directory

from core.models.base import SoftDeletionModel, SoftDeletionQuerySet, SoftDeletionManager
from core.models.job import JobListing, RejectionReason
from core.models.user import UserProfile
from core.models.employer import EmployerProfile
from core.models.application import JobApplication, SavedJob, CVAccess
from core.models.blog import BlogPost, BlogCategory, BlogPostCategory, BlogTag
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
    'BlogPost', 'BlogCategory', 'BlogPostCategory', 'BlogTag',
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