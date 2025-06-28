from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Import storage backends if S3 is enabled
if hasattr(settings, 'USE_S3') and settings.USE_S3:
    from jobsy.storage_backends import PublicMediaStorage, PrivateMediaStorage
else:
    PublicMediaStorage = None
    PrivateMediaStorage = None

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('განხილვის_პროცესში', _('განხილვის პროცესში')),
        ('გასაუბრება', _('გასაუბრება')),
        ('რეზერვი', _('რეზერვი')),
    ]
    
    job = models.ForeignKey('JobListing', on_delete=models.SET_NULL, null=True, related_name='applications', verbose_name=_("ვაკანსია"))
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("ვაკანსიის სათაური"))
    job_company = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("კომპანია"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications', null=True, blank=True, verbose_name=_("მომხმარებელი"))
    guest_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("სტუმრის სახელი"))
    guest_email = models.EmailField(blank=True, null=True, verbose_name=_("სტუმრის ელ-ფოსტა"))
    cover_letter = models.TextField(verbose_name=_("მოტივაციის წერილი"))
    
    # Use PrivateMediaStorage for sensitive resume files when S3 is enabled
    if PrivateMediaStorage:
        resume = models.FileField(
            upload_to='resumes/', 
            storage=PrivateMediaStorage(),
            verbose_name=_("რეზიუმე")
        )
    else:
        resume = models.FileField(
            upload_to='resumes/', 
            verbose_name=_("რეზიუმე")
        )
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='განხილვის_პროცესში', db_index=True, verbose_name=_("სტატუსი"))
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("აპლიკაციის თარიღი"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("განახლების თარიღი"))
    is_read = models.BooleanField(default=False, db_index=True, verbose_name=_("წაკითხულია"))
    is_viewed = models.BooleanField(default=False, db_index=True, verbose_name=_("ნანახია"))
    rejection_reasons = models.ManyToManyField('RejectionReason', blank=True, related_name='applications', verbose_name=_("უარის მიზეზები"))
    feedback = models.TextField(blank=True, verbose_name=_("უკუკავშირი"))
    
    def save(self, *args, **kwargs):
        # Store job details for historical record if job exists
        if self.job and not self.job_title:
            self.job_title = self.job.title
            self.job_company = self.job.company
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['user', 'status']),
        ]
        verbose_name = _("აპლიკაცია")
        verbose_name_plural = _("აპლიკაციები")
    
    def __str__(self):
        if self.user:
            applicant = self.user.username
        elif self.guest_name:
            applicant = f"{self.guest_name} (Guest)"
        else:
            applicant = "Unknown Applicant"
        
        job_title = self.job_title if self.job_title else (self.job.title if self.job else "Unknown Job")
        return f"{applicant} - {job_title}"


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_jobs', verbose_name=_("მომხმარებელი"))
    job = models.ForeignKey('JobListing', on_delete=models.SET_NULL, null=True, related_name='saved_by', verbose_name=_("ვაკანსია"))
    # Store job details for historical record
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("ვაკანსიის სათაური"))
    job_company = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("კომპანია"))
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name=_("შენახვის თარიღი"))
    
    def save(self, *args, **kwargs):
        # Save job details for historical record
        if self.job and not self.job_title:
            self.job_title = self.job.title
            self.job_company = self.job.company
        
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('user', 'job')
        verbose_name = _("შენახული ვაკანსია")
        verbose_name_plural = _("შენახული ვაკანსიები")
        ordering = ['-saved_at']
    
    def __str__(self):
        job_title = self.job_title if self.job_title else (self.job.title if self.job else "Unknown Job")
        return f"{self.user.username} - {job_title}"


class CVAccess(models.Model):
    """Track employer access to candidate CVs"""
    employer_profile = models.ForeignKey('EmployerProfile', on_delete=models.CASCADE, related_name='cv_accesses')
    candidate_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='cv_accesses')
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('employer_profile', 'candidate_profile')
        verbose_name = _("CV წვდომა")
        verbose_name_plural = _("CV წვდომები")
    
    def __str__(self):
        return f"{self.employer_profile.company_name} accessed {self.candidate_profile.user.username}'s CV" 