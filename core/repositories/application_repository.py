from django.db.models import Count, Q
from core.models import JobApplication

class ApplicationRepository:
    """
    Repository class for job application-related database operations
    This follows the Repository pattern to abstract data access
    """
    
    @staticmethod
    def get_applications_by_job(job_id, status_filter=None):
        """
        Get all applications for a specific job
        
        Args:
            job_id (int): ID of the job
            status_filter (str): Optional status filter
            
        Returns:
            QuerySet: Filtered job applications
        """
        query = JobApplication.objects.filter(job_id=job_id).select_related('user')
        
        if status_filter:
            query = query.filter(status=status_filter)
            
        return query.order_by('-applied_at')
    
    @staticmethod
    def get_applications_by_employer(employer_profile, unread_only=False):
        """
        Get all applications for jobs posted by an employer
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            unread_only (bool): Whether to return only unread applications
            
        Returns:
            QuerySet: Filtered job applications
        """
        query = JobApplication.objects.filter(job__employer=employer_profile)
        
        if unread_only:
            query = query.filter(is_read=False)
            
        return query.select_related('job', 'user').order_by('-applied_at')
    
    @staticmethod
    def get_application_by_id(application_id):
        """
        Get a job application by ID
        
        Args:
            application_id (int): ID of the application
            
        Returns:
            JobApplication: The job application, or None if not found
        """
        try:
            return JobApplication.objects.get(id=application_id)
        except JobApplication.DoesNotExist:
            return None
    
    @staticmethod
    def get_application_counts_by_status(job_id=None, employer_profile=None):
        """
        Get counts of applications grouped by status
        
        Args:
            job_id (int): Optional job ID to filter by
            employer_profile (EmployerProfile): Optional employer profile to filter by
            
        Returns:
            dict: Dictionary of status counts
        """
        query = JobApplication.objects
        
        if job_id:
            query = query.filter(job_id=job_id)
        elif employer_profile:
            query = query.filter(job__employer=employer_profile)
        
        status_counts = {}
        for status_choice in JobApplication.STATUS_CHOICES:
            status_code = status_choice[0]
            status_counts[status_code] = query.filter(status=status_code).count()
            
        return status_counts
    
    @staticmethod
    def get_recent_applications(employer_profile, limit=5):
        """
        Get recent applications for an employer
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            limit (int): Maximum number of applications to return
            
        Returns:
            QuerySet: Recent job applications
        """
        return JobApplication.objects.filter(
            job__employer=employer_profile
        ).select_related('job', 'user').order_by('-applied_at')[:limit]
    
    @staticmethod
    def mark_application_as_read(application_id):
        """
        Mark an application as read
        
        Args:
            application_id (int): ID of the application
            
        Returns:
            bool: Success status
        """
        try:
            application = JobApplication.objects.get(id=application_id)
            application.is_read = True
            application.save(update_fields=['is_read'])
            return True
        except JobApplication.DoesNotExist:
            return False
            
    @staticmethod
    def mark_application_as_viewed(application_id):
        """
        Mark an application as viewed
        
        Args:
            application_id (int): ID of the application
            
        Returns:
            bool: Success status
        """
        try:
            application = JobApplication.objects.get(id=application_id)
            application.is_viewed = True
            application.save(update_fields=['is_viewed'])
            return True
        except JobApplication.DoesNotExist:
            return False 