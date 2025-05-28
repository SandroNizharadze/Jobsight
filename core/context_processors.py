from core.models import JobListing
from django.utils import timezone

def employer_premium_status(request):
    """
    Add employer premium status to the template context.
    """
    context = {
        'has_premium_plus_access': False
    }
    
    if request.user.is_authenticated:
        try:
            # Check if user is an employer
            if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'employer':
                employer_profile = request.user.userprofile.employer_profile
                
                # Check if employer has at least one active premium+ job that's not expired
                has_premium_plus = JobListing.objects.filter(
                    employer=employer_profile,
                    premium_level='premium_plus',
                    status='approved',  # Only count approved jobs
                    deleted_at__isnull=True,  # Don't count deleted jobs
                ).filter(
                    # Either has no expiration date or hasn't expired yet
                    expires_at__gt=timezone.now()
                ).exists()
                
                context['has_premium_plus_access'] = has_premium_plus
        except:
            pass
    
    return context 