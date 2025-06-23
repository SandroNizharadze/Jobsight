from django.db.models import Count, Q, Case, When, Value, IntegerField
from django.utils import timezone
from core.models import EmployerProfile, JobListing, JobApplication, UserProfile, CVAccess
from core.repositories.job_repository import JobRepository
from core.repositories.application_repository import ApplicationRepository
from core.repositories.employer_repository import EmployerRepository

class EmployerService:
    """
    Service class for handling employer-related business logic
    This follows the Single Responsibility Principle by centralizing employer operations
    """
    
    @staticmethod
    def get_employer_jobs(employer_profile, include_deleted=False, search_query=None, sort_option=None):
        """
        Get all jobs for an employer with optional filtering and sorting
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            include_deleted (bool): Whether to include soft-deleted jobs
            search_query (str): Optional search term for filtering
            sort_option (str): Optional sort option
            
        Returns:
            QuerySet: Filtered and sorted job listings
        """
        # Get jobs from repository
        jobs_query = JobRepository.get_employer_jobs(
            employer_profile=employer_profile,
            include_deleted=include_deleted
        )
        
        # Apply search filter if provided
        if search_query:
            jobs_query = JobRepository.search_jobs(
                query_string=search_query,
                employer_profile=employer_profile
            )
        
        # Annotate with counts needed for sorting and display
        jobs_query = jobs_query.annotate(
            applications_count=Count('applications'),
            unread_applications_count=Count('applications', filter=Q(applications__is_read=False)),
            pending_applications_count=Count('applications', filter=Q(applications__status='განხილვის_პროცესში')),
            status_order=Case(
                When(status='approved', then=Value(1)),
                When(status='pending_review', then=Value(2)),
                When(status='rejected', then=Value(3)),
                When(status='expired', then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            ),
        )
        
        # Apply sorting
        if sort_option == 'date_desc':
            jobs_query = jobs_query.order_by('-posted_at')
        elif sort_option == 'date_asc':
            jobs_query = jobs_query.order_by('posted_at')
        elif sort_option == 'views_desc':
            jobs_query = jobs_query.order_by('-view_count')
        elif sort_option == 'applicants_desc':
            jobs_query = jobs_query.order_by('-applications_count')
        elif sort_option == 'status':
            jobs_query = jobs_query.order_by('status_order', '-posted_at')
        else:
            # Default sorting
            jobs_query = jobs_query.order_by('-posted_at')
        
        return jobs_query
    
    @staticmethod
    def get_employer_metrics(employer_profile):
        """
        Get metrics for an employer dashboard
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            
        Returns:
            dict: Dictionary of metrics
        """
        # Get jobs from repository
        jobs = JobRepository.get_employer_jobs(employer_profile)
        
        # Calculate metrics
        total_jobs = jobs.count()
        active_jobs = jobs.filter(status='approved').count()
        
        # Get applications from repository
        applications = ApplicationRepository.get_applications_by_employer(employer_profile)
        total_applicants = applications.count()
        unread_applicants = applications.filter(is_read=False).count()
        
        avg_applicants = round(total_applicants / total_jobs, 2) if total_jobs > 0 else 0
        
        return {
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applicants': total_applicants,
            'unread_applicants': unread_applicants,
            'avg_applicants': avg_applicants,
        }
    
    @staticmethod
    def get_cv_database_candidates(employer_profile, filters=None):
        """
        Get candidates from the CV database with optional filtering
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            filters (dict): Optional dictionary of filters to apply
            
        Returns:
            QuerySet: Filtered candidate profiles
        """
        # Get candidates from repository
        candidates = EmployerRepository.get_cv_database_candidates(filters)
        
        # Track CV access for each candidate
        for candidate in candidates:
            EmployerRepository.track_cv_access(
                employer_profile=employer_profile,
                candidate_profile=candidate
            )
        
        return candidates 