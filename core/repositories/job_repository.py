from django.db.models import Q
from core.models import JobListing
from django.utils import timezone

class JobRepository:
    """
    Repository class for job-related database operations
    This follows the Repository pattern to abstract data access
    """
    
    @staticmethod
    def get_active_jobs(filters=None):
        """
        Get all active job listings with optional filtering
        
        Args:
            filters (dict): Optional dictionary of filters to apply
            
        Returns:
            QuerySet: Filtered job listings
        """
        # Include both approved jobs and extended_review jobs that haven't expired yet
        query = JobListing.objects.filter(
            Q(status='approved') | 
            # Include extended_review jobs that haven't expired yet
            Q(status='extended_review', expires_at__gt=timezone.now())
        ).exclude(status='expired')  # Explicitly exclude expired jobs from public listings
        
        if filters:
            query = JobRepository._apply_job_filters(query, filters)
        
        return query.order_by('-premium_level', '-posted_at')
    
    @staticmethod
    def get_job_by_id(job_id):
        """
        Get a job listing by ID
        
        Args:
            job_id (int): ID of the job listing
            
        Returns:
            JobListing: The job listing, or None if not found
        """
        try:
            return JobListing.objects.get(id=job_id)
        except JobListing.DoesNotExist:
            return None
    
    @staticmethod
    def get_employer_jobs(employer_profile, include_deleted=False):
        """
        Get all jobs for an employer
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            include_deleted (bool): Whether to include soft-deleted jobs
            
        Returns:
            QuerySet: Job listings for the employer
        """
        if include_deleted:
            return JobListing.all_objects.filter(employer=employer_profile)
        else:
            return JobListing.objects.filter(
                employer=employer_profile,
                deleted_at__isnull=True  # Explicitly exclude deleted jobs
            )
    
    @staticmethod
    def search_jobs(query_string, employer_profile=None):
        """
        Search for jobs by title, company, location, or category
        
        Args:
            query_string (str): Search query
            employer_profile (EmployerProfile): Optional employer profile to filter by
            
        Returns:
            QuerySet: Filtered job listings
        """
        search_filter = (
            Q(title__icontains=query_string) |
            Q(company__icontains=query_string) |
            Q(location__icontains=query_string) |
            Q(category__icontains=query_string)
        )
        
        if employer_profile:
            return JobListing.objects.filter(search_filter, employer=employer_profile)
        else:
            return JobListing.objects.filter(search_filter, status='approved')
    
    @staticmethod
    def _apply_job_filters(query, filters):
        """
        Apply filters to a job query
        
        Args:
            query (QuerySet): The initial query
            filters (dict): Dictionary of filters to apply
            
        Returns:
            QuerySet: Filtered query
        """
        if 'category' in filters and filters['category']:
            query = query.filter(category=filters['category'])
            
        if 'location' in filters and filters['location']:
            query = query.filter(location=filters['location'])
            
        if 'experience' in filters and filters['experience']:
            query = query.filter(experience=filters['experience'])
            
        if 'job_preferences' in filters and filters['job_preferences']:
            query = query.filter(job_preferences=filters['job_preferences'])
            
        if 'considers_students' in filters:
            query = query.filter(considers_students=filters['considers_students'])
            
        if 'search' in filters and filters['search']:
            search_term = filters['search']
            query = query.filter(
                Q(title__icontains=search_term) | 
                Q(company__icontains=search_term)
            )
            
        return query 