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
                
                # Use has_cv_database_access flag for determining premium+ access
                context['has_premium_plus_access'] = employer_profile.has_cv_database_access
        except:
            pass
    
    return context 

def language_attributes(request):
    """
    Add language-specific HTML attributes to the context.
    This helps with font selection based on language.
    """
    return {
        'lang_attr': f'lang="{request.LANGUAGE_CODE}"',
    } 