from django.db.models import Count
from core.models import EmployerNotification

class NotificationRepository:
    """
    Repository class for notification-related database operations
    This follows the Repository pattern to abstract data access
    """
    
    @staticmethod
    def create_job_status_notification(employer_profile, job, message):
        """
        Create a job status update notification
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            job (JobListing): The job listing
            message (str): The notification message
            
        Returns:
            EmployerNotification: The created notification
        """
        notification = EmployerNotification(
            employer_profile=employer_profile,
            job=job,
            notification_type='job_status_update',
            message=message
        )
        notification.save()
        return notification
    
    @staticmethod
    def create_new_application_notification(employer_profile, job, message):
        """
        Create a new application notification
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            job (JobListing): The job listing
            message (str): The notification message
            
        Returns:
            EmployerNotification: The created notification
        """
        notification = EmployerNotification(
            employer_profile=employer_profile,
            job=job,
            notification_type='new_application',
            message=message
        )
        notification.save()
        return notification
    
    @staticmethod
    def get_employer_notifications(employer_profile, unread_only=False):
        """
        Get notifications for an employer
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            unread_only (bool): Whether to return only unread notifications
            
        Returns:
            QuerySet: Filtered notifications
        """
        query = EmployerNotification.objects.filter(employer_profile=employer_profile)
        
        if unread_only:
            query = query.filter(is_read=False)
            
        return query.order_by('-created_at')
    
    @staticmethod
    def get_unread_notification_count(employer_profile):
        """
        Get count of unread notifications for an employer
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            
        Returns:
            int: Count of unread notifications
        """
        return EmployerNotification.objects.filter(
            employer_profile=employer_profile,
            is_read=False
        ).count()
    
    @staticmethod
    def get_unread_notification_count_by_job(employer_profile, job_id):
        """
        Get count of unread notifications for a specific job
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            job_id (int): ID of the job
            
        Returns:
            int: Count of unread notifications
        """
        return EmployerNotification.objects.filter(
            employer_profile=employer_profile,
            job_id=job_id,
            is_read=False
        ).count()
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """
        Mark a notification as read
        
        Args:
            notification_id (int): ID of the notification
            
        Returns:
            bool: Success status
        """
        try:
            notification = EmployerNotification.objects.get(id=notification_id)
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return True
        except EmployerNotification.DoesNotExist:
            return False
    
    @staticmethod
    def mark_all_notifications_as_read(employer_profile):
        """
        Mark all notifications as read for an employer
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            
        Returns:
            int: Number of notifications marked as read
        """
        return EmployerNotification.objects.filter(
            employer_profile=employer_profile,
            is_read=False
        ).update(is_read=True)
    
    @staticmethod
    def mark_job_notifications_as_read(employer_profile, job_id):
        """
        Mark all notifications for a specific job as read
        
        Args:
            employer_profile (EmployerProfile): The employer profile
            job_id (int): ID of the job
            
        Returns:
            int: Number of notifications marked as read
        """
        return EmployerNotification.objects.filter(
            employer_profile=employer_profile,
            job_id=job_id,
            is_read=False
        ).update(is_read=True) 