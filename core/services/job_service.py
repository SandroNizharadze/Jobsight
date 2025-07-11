from datetime import timedelta
from django.utils import timezone
from core.models import JobApplication, SavedJob
from core.repositories.job_repository import JobRepository

class JobService:
    """
    Service class for handling job-related business logic
    This follows the Single Responsibility Principle by centralizing job-related operations
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
        return JobRepository.get_active_jobs(filters)
    
    @staticmethod
    def extend_job_expiration(job_id, days=30):
        """
        Extend the expiration date of a job listing
        
        Args:
            job_id (int): ID of the job listing
            days (int): Number of days to extend by
            
        Returns:
            JobListing: The updated job listing, or None if not found
        """
        job = JobRepository.get_job_by_id(job_id)
        if not job:
            return None
            
        # Only update the expiration date, don't change status
        # Status changes should be handled by the view
        
        # If job is expired, extend from current date
        if job.is_expired():
            job.expires_at = timezone.now() + timedelta(days=days)
        # Otherwise extend from current expiration date
        elif job.expires_at:
            job.expires_at = job.expires_at + timedelta(days=days)
        # If no expiration date set, set one
        else:
            job.expires_at = timezone.now() + timedelta(days=days)
        
        # Only update expires_at, don't change status
        job.save(update_fields=['expires_at'])
        return job
    
    @staticmethod
    def apply_for_job(job_id, user=None, guest_name=None, guest_email=None, cover_letter=None, resume=None):
        """
        Submit a job application
        
        Args:
            job_id (int): ID of the job to apply for
            user: Django user object (for logged-in users)
            guest_name (str): Name of guest applicant
            guest_email (str): Email of guest applicant
            cover_letter (str): Cover letter text
            resume (File): Resume file
            
        Returns:
            tuple: (JobApplication, str) - The created application and status message
        """
        job = JobRepository.get_job_by_id(job_id)
        if not job or job.status != 'approved':
            return None, "Job not found or not active"
        
        # Check if user has already applied
        if user and JobApplication.objects.filter(job=job, user=user).exists():
            return None, "You have already applied for this job"
        
        # Check if guest email has already applied
        if guest_email and JobApplication.objects.filter(job=job, guest_email=guest_email).exists():
            return None, "This email has already been used to apply for this job"
        
        # Create application
        application = JobApplication(
            job=job,
            user=user,
            guest_name=guest_name,
            guest_email=guest_email,
            cover_letter=cover_letter,
            resume=resume
        )
        application.save()
        
        return application, "Application submitted successfully"
    
    @staticmethod
    def toggle_saved_job(user, job_id):
        """
        Toggle whether a job is saved by a user
        
        Args:
            user: Django user object
            job_id (int): ID of the job to save/unsave
            
        Returns:
            tuple: (bool, str) - Success status and message
        """
        job = JobRepository.get_job_by_id(job_id)
        if not job:
            return False, "Job not found"
        
        # Check if already saved
        saved_job = SavedJob.objects.filter(user=user, job=job).first()
        
        if saved_job:
            # Unsave the job
            saved_job.delete()
            return True, "Job removed from saved jobs"
        else:
            # Save the job
            SavedJob.objects.create(user=user, job=job)
            return True, "Job saved successfully" 