from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import JobListing
from core.services.employer_service import EmployerService
from .dashboard import is_employer
import logging

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(is_employer)
def cv_database(request):
    """
    View for accessing the CV database
    """
    employer_profile = request.user.userprofile.employer_profile
    
    # Check if employer has access to CV database
    if not employer_profile.has_cv_database_access:
        return render(request, 'core/cv_database_upgrade.html', {
            'employer_profile': employer_profile
        })
    
    # Get filter parameters from request
    filters = {}
    
    # Get field filter - the form uses 'field' but the model uses 'desired_field'
    field_filter = request.GET.get('field', '')
    if field_filter:
        filters['desired_field'] = field_filter
        
    # Get experience filter - the form uses 'experience' but the model uses 'field_experience'
    experience_filter = request.GET.get('experience', '')
    if experience_filter:
        filters['field_experience'] = experience_filter
        
    # Get search filter
    search_filter = request.GET.get('search', '')
    if search_filter:
        filters['search'] = search_filter
    
    # Get candidates using the service
    profiles = EmployerService.get_cv_database_candidates(
        employer_profile=employer_profile,
        filters=filters
    )
    
    # Get choices for filter dropdowns
    field_choices = dict(JobListing.CATEGORY_CHOICES)
    experience_choices = dict(JobListing.EXPERIENCE_CHOICES)
    
    context = {
        'employer_profile': employer_profile,
        'profiles': profiles,  # Changed from 'candidates' to 'profiles' to match the template
        'field_choices': field_choices,
        'experience_choices': experience_choices,
        'field_filter': field_filter,
        'experience_filter': experience_filter,
    }
    
    return render(request, 'core/cv_database.html', context) 