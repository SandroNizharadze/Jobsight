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
    if 'desired_field' in request.GET and request.GET['desired_field']:
        filters['desired_field'] = request.GET['desired_field']
        
    if 'field_experience' in request.GET and request.GET['field_experience']:
        filters['field_experience'] = request.GET['field_experience']
        
    if 'search' in request.GET and request.GET['search']:
        filters['search'] = request.GET['search']
    
    # Get candidates using the service
    candidates = EmployerService.get_cv_database_candidates(
        employer_profile=employer_profile,
        filters=filters
    )
    
    # Get choices for filter dropdowns
    field_choices = JobListing.CATEGORY_CHOICES
    experience_choices = JobListing.EXPERIENCE_CHOICES
    
    context = {
        'employer_profile': employer_profile,
        'candidates': candidates,
        'field_choices': field_choices,
        'experience_choices': experience_choices,
        'filters': filters,
    }
    
    return render(request, 'core/cv_database.html', context) 