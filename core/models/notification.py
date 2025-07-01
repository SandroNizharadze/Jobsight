from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class EmployerNotification(models.Model):
    """
    Model to store notifications for employers
    """
    NOTIFICATION_TYPES = [
        ('job_status_update', _('Job Status Update')),
        ('new_application', _('New Application')),
    ]
    
    employer_profile = models.ForeignKey('EmployerProfile', on_delete=models.CASCADE, related_name='notifications', verbose_name=_("დამსაქმებელი"))
    job = models.ForeignKey('JobListing', on_delete=models.SET_NULL, null=True, related_name='notifications', verbose_name=_("ვაკანსია"))
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("ვაკანსიის სათაური"))
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name=_("შეტყობინების ტიპი"))
    message = models.TextField(verbose_name=_("შეტყობინება"))
    is_read = models.BooleanField(default=False, db_index=True, verbose_name=_("წაკითხულია"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("შექმნის თარიღი"))
    
    def save(self, *args, **kwargs):
        # Store job title for historical record if job exists
        if self.job and not self.job_title:
            self.job_title = self.job.title
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employer_profile', 'is_read']),
            models.Index(fields=['job', 'notification_type']),
        ]
        verbose_name = _("დამსაქმებლის შეტყობინება")
        verbose_name_plural = _("დამსაქმებლის შეტყობინებები")


class CandidateNotification(models.Model):
    """
    Model to store notifications for candidates
    """
    NOTIFICATION_TYPES = [
        ('application_status_update', _('Application Status Update')),
        ('interview_invitation', _('Interview Invitation')),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name=_("მომხმარებელი"))
    application = models.ForeignKey('JobApplication', on_delete=models.SET_NULL, null=True, related_name='candidate_notifications', verbose_name=_("აპლიკაცია"))
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("ვაკანსიის სათაური"))
    company_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("კომპანია"))
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, verbose_name=_("შეტყობინების ტიპი"))
    message = models.TextField(verbose_name=_("შეტყობინება"))
    is_read = models.BooleanField(default=False, db_index=True, verbose_name=_("წაკითხულია"))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("შექმნის თარიღი"))
    
    def save(self, *args, **kwargs):
        # Store job title and company for historical record if application exists
        if self.application and not self.job_title:
            if self.application.job:
                self.job_title = self.application.job.title
                self.company_name = self.application.job.company
            else:
                self.job_title = self.application.job_title
                self.company_name = self.application.job_company
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['application', 'notification_type']),
        ]
        verbose_name = _("კანდიდატის შეტყობინება")
        verbose_name_plural = _("კანდიდატის შეტყობინებები") 