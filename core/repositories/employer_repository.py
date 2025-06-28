from django.db.models import Count, Q
from core.models import EmployerProfile, UserProfile, CVAccess

class EmployerRepository:
    """
    Repository class for employer-related database operations
    This follows the Repository pattern to abstract data access
    """
    
    @staticmethod
    def get_employer_by_id(employer_id):
        """
        Get an employer profile by ID
        
        Args:
            employer_id (int): ID of the employer profile
            
        Returns:
            EmployerProfile: The employer profile, or None if not found
        """
        try:
            return EmployerProfile.objects.get(id=employer_id)
        except EmployerProfile.DoesNotExist:
            return None
    
    @staticmethod
    def get_employer_by_user_id(user_id):
        """
        Get an employer profile by user ID
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            EmployerProfile: The employer profile, or None if not found
        """
        try:
            return EmployerProfile.objects.get(user_profile__user_id=user_id)
        except EmployerProfile.DoesNotExist:
            return None
    
    @staticmethod
    def get_cv_database_candidates(filters=None):
        """
        Get candidates from the CV database with optional filtering
        
        Args:
            filters (dict): Optional dictionary of filters to apply
            
        Returns:
            QuerySet: Filtered candidate profiles
        """
        # Only return candidates who have opted in to the CV database
        candidates = UserProfile.objects.filter(
            role='candidate',
            visible_to_employers=True,
            cv__isnull=False
        )
        
        if filters:
            candidates = EmployerRepository._apply_candidate_filters(candidates, filters)
            
        return candidates.select_related('user')
    
    @staticmethod
    def track_cv_access(employer_profile, candidate_profile):
        """
        Track employer access to a candidate's CV
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            candidate_profile (UserProfile): The candidate profile
            
        Returns:
            CVAccess: The created or updated CV access record
        """
        # First try to get an existing record
        cv_access = CVAccess.objects.filter(
            employer_profile=employer_profile,
            candidate_profile=candidate_profile
        ).first()
        
        if cv_access:
            # Update the accessed_at timestamp
            cv_access.save(update_fields=['accessed_at'])
        else:
            # Create a new record
            cv_access = CVAccess.objects.create(
                employer_profile=employer_profile,
                candidate_profile=candidate_profile
            )
            
        return cv_access
    
    @staticmethod
    def _apply_candidate_filters(query, filters):
        """
        Apply filters to a candidate query
        
        Args:
            query (QuerySet): The initial query
            filters (dict): Dictionary of filters to apply
            
        Returns:
            QuerySet: Filtered query
        """
        if 'desired_field' in filters and filters['desired_field']:
            query = query.filter(desired_field=filters['desired_field'])
            
        if 'field_experience' in filters and filters['field_experience']:
            query = query.filter(field_experience=filters['field_experience'])
            
        if 'search' in filters and filters['search']:
            search_term = filters['search']
            query = query.filter(
                Q(user__first_name__icontains=search_term) |
                Q(user__last_name__icontains=search_term)
            )
            
        return query 