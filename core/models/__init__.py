from core.models.base import SoftDeletionModel, SoftDeletionQuerySet, SoftDeletionManager
from core.models.job import JobListing, RejectionReason
from core.models.user import UserProfile
from core.models.employer import EmployerProfile
from core.models.application import JobApplication, SavedJob, CVAccess
from core.models.blog import BlogPost, BlogCategory, BlogPostCategory
from core.models.pricing import (
    PricingPackage, PricingFeature, ComparisonTable, ComparisonRow,
    PricingPackageTranslation, PricingFeatureTranslation, 
    ComparisonTableTranslation, ComparisonRowTranslation
)
from core.models.auth import EmailVerificationToken
from core.models.static_pages import StaticPage
from core.models.notification import EmployerNotification, CandidateNotification

# For backward compatibility, expose all models at the module level
__all__ = [
    'SoftDeletionModel',
    'SoftDeletionQuerySet',
    'SoftDeletionManager',
    'JobListing',
    'RejectionReason',
    'UserProfile',
    'EmployerProfile',
    'JobApplication',
    'SavedJob',
    'CVAccess',
    'BlogPost',
    'BlogCategory',
    'BlogPostCategory',
    'PricingPackage',
    'PricingFeature',
    'ComparisonTable',
    'ComparisonRow',
    'PricingPackageTranslation',
    'PricingFeatureTranslation',
    'ComparisonTableTranslation',
    'ComparisonRowTranslation',
    'EmailVerificationToken',
    'StaticPage',
    'EmployerNotification',
    'CandidateNotification',
] 