from core.models.base import SoftDeletionModel, SoftDeletionQuerySet, SoftDeletionManager
from core.models.job import JobListing, RejectionReason
from core.models.user import UserProfile
from core.models.employer import EmployerProfile
from core.models.application import JobApplication, SavedJob, CVAccess
from core.models.blog import BlogPost, BlogCategory, BlogPostCategory, BlogTag
from core.models.pricing import PricingPackage, PricingFeature, ComparisonTable, ComparisonRow
from core.models.auth import EmailVerificationToken
from core.models.static_pages import StaticPage

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
    'BlogTag',
    'PricingPackage',
    'PricingFeature',
    'ComparisonTable',
    'ComparisonRow',
    'EmailVerificationToken',
    'StaticPage',
] 