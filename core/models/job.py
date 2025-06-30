from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from ckeditor.fields import RichTextField
from datetime import timedelta
from core.models.base import SoftDeletionModel

class JobListing(SoftDeletionModel):
    CATEGORY_CHOICES = [
        ('მენეჯმენტი/ადმინისტრირება', _('მენეჯმენტი/ ადმინისტრირება')),
        ('მარკეტინგი', _('მარკეტინგი')),
        ('ფინანსები', _('ფინანსები')),
        ('გაყიდვები/მომხმარებელთან ურთიერთობა', _('გაყიდვები/მომხმარებელთან ურთიერთობა')),
        ('IT/პროგრამირება', _('IT/პროგრამირება')),
        ('დიზაინი', _('დიზაინი')),
        ('ჰორეკა/კვება', _('ჰორეკა/კვება')),
        ('დაცვა', _('დაცვა')),
        ('სილამაზე/მოდა', _('სილამაზე/მოდა')),
        ('მშენებლობა', _('მშენებლობა')),
        ('მედიცინა', _('მედიცინა')),
        ('განათლება', _('განათლება')),
        ('სამართალი', _('სამართალი')),
        ('ტურიზმი', _('ტურიზმი')),
        ('ლოჯისტიკა/დისტრიბუცია', _('ლოჯისტიკა/დისტრიბუცია')),
        ('საბანკო საქმე', _('საბანკო საქმე')),
        ('აზარტული', _('აზარტული')),
        ('სხვა', _('სხვა')),
    ]
    
    LOCATION_CHOICES = [
        ('დისტანციური', _('დისტანციური')),
        ('თბილისი', _('თბილისი')),
        ('აჭარა', _('აჭარა')),
        ('აფხაზეთი', _('აფხაზეთი')),
        ('სვანეთი', _('სვანეთი')),
        ('სამეგრელო', _('სამეგრელო')),
        ('კახეთი', _('კახეთი')),
        ('ლეჩხუმი', _('ლეჩხუმი')),
        ('რაჭა', _('რაჭა')),
        ('გურია', _('გურია')),
        ('ქვემო ქართლი', _('ქვემო ქართლი')),
        ('სამცხე-ჯავახეთი', _('სამცხე-ჯავახეთი')),
        ('შიდა ქართლი', _('შიდა ქართლი')),
        ('მცხეთა-მთიანეთი', _('მცხეთა-მთიანეთი')),
        ('იმერეთი', _('იმერეთი')),
        ('სხვა', _('სხვა')),
    ]
    
    EXPERIENCE_CHOICES = [
        ('გამოცდილების გარეშე', _('გამოცდილების გარეშე')),
        ('დამწყები', _('დამწყები')),
        ('საშუალო დონე', _('საშუალო დონე')),
        ('პროფესიონალი', _('პროფესიონალი')),
    ]
    
    JOB_PREFERENCE_CHOICES = [
        ('სრული განაკვეთი', _('სრული განაკვეთი')),
        ('ნახევარი განაკვეთი', _('ნახევარი განაკვეთი')),
        ('ცვლები', _('ცვლები')),
    ]
    
    CONSIDERS_STUDENTS_CHOICES = [
        (True, _('კი')),
        (False, _('არა')),
    ]
    
    SALARY_TYPE_CHOICES = [
        ('თვეში', _('თვეში')),
        ('კვირაში', _('კვირაში')),
        ('დღეში', _('დღეში')),
        ('საათში', _('საათში')),
    ]

    title = models.CharField(max_length=100, db_index=True, verbose_name=_("ვაკანსიის დასახელება"))
    company = models.CharField(max_length=100, db_index=True, verbose_name=_("კომპანია"))
    description = RichTextField(verbose_name=_("ვაკანსიის აღწერა"))
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True, verbose_name=_("მინიმალური ხელფასი"))
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("მაქსიმალური ხელფასი"))
    salary_type = models.CharField(max_length=50, choices=SALARY_TYPE_CHOICES, default='თვეში', verbose_name=_("ხელფასის ტიპი"))
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, db_index=True, verbose_name=_("კატეგორია"))
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, db_index=True, verbose_name=_("ლოკაცია"))
    employer = models.ForeignKey('EmployerProfile', on_delete=models.CASCADE, related_name='job_listings', verbose_name=_("დამსაქმებელი"))
    posted_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("გამოქვეყნების თარიღი"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("განახლების თარიღი"))
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name=_("ვადის გასვლის თარიღი"))
    experience = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES, db_index=True, verbose_name=_("გამოცდილება"))
    job_preferences = models.CharField(max_length=255, choices=JOB_PREFERENCE_CHOICES, verbose_name=_("სამუშაო გრაფიკი"))
    considers_students = models.BooleanField(default=False, choices=CONSIDERS_STUDENTS_CHOICES, verbose_name=_("განიხილავს სტუდენტებს"))
    
    PREMIUM_LEVEL_CHOICES = [
        ('standard', _('Standard')),
        ('premium', _('Premium')),
        ('premium_plus', _('Premium +')),
    ]
    premium_level = models.CharField(max_length=20, choices=PREMIUM_LEVEL_CHOICES, default='standard', db_index=True, verbose_name=_("პრემიუმ დონე"))
    georgian_language_only = models.BooleanField(choices=[(True, 'კი'), (False, 'არა')], default=False, verbose_name=_("პოზიციაზე მოთხოვნილია მხოლოდ ქართული ენის ცოდნა"))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("ნახვების რაოდენობა"))
    use_external_link = models.BooleanField(default=False, verbose_name=_('ატვირთულია გარე ლინკით'))
    external_link = models.URLField(blank=True, verbose_name=_('External Link'))
    last_extended_at = models.DateTimeField(null=True, blank=True, verbose_name=_("ბოლო გაგრძელების თარიღი"))

    STATUS_CHOICES = [
        ('pending_review', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
        ('extended_review', _('Extended (Under Review)')),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review', db_index=True, verbose_name=_("სტატუსი"))
    admin_feedback = models.TextField(blank=True, verbose_name=_("ადმინის უკუკავშირი"))
    def __str__(self):
        return f"{self.title} at {self.company}"

    def is_expired(self):
        """Check if the job posting has expired"""
        # If status is explicitly set to 'expired', return True
        if self.status == 'expired':
            return True
        
        # Otherwise check the expiration date
        if not self.expires_at:
            return False
            
        return timezone.now() >= self.expires_at

    def days_until_expiration(self):
        """Calculate days remaining until job expires"""
        if not self.expires_at:
            return None
        
        if self.is_expired():
            return 0
        
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    def update_status_from_expiration(self):
        """Update the job status based on expiration date"""
        # Only update status if job is approved or expired
        if self.status not in ['approved', 'expired']:
            return False
            
        is_expired_now = timezone.now() >= self.expires_at if self.expires_at else False
        
        # If job has expired but status is not 'expired'
        if is_expired_now and self.status != 'expired':
            self.status = 'expired'
            self.save(update_fields=['status'])
            return True
            
        # If job is not expired but status is 'expired'
        if not is_expired_now and self.status == 'expired':
            self.status = 'approved'
            self.save(update_fields=['status'])
            return True
            
        return False
        
    def extend_expiration(self, days=30, bump_to_top=True):
        """
        Extend the job expiration date by the specified number of days
        
        Args:
            days (int): Number of days to extend by
            bump_to_top (bool): Whether to bump the job to the top of listings
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=days)
        else:
            # If job is expired, extend from current date
            if self.is_expired():
                self.expires_at = timezone.now() + timedelta(days=days)
                # If the job status is 'expired', update it to 'approved'
                if self.status == 'expired':
                    self.status = 'approved'
            # Otherwise extend from current expiration date
            else:
                self.expires_at = self.expires_at + timedelta(days=days)
        
        # Set last_extended_at to now if bumping to top
        if bump_to_top:
            self.last_extended_at = timezone.now()
            self.save(update_fields=['expires_at', 'status', 'last_extended_at'])
        else:
            self.save(update_fields=['expires_at', 'status'])
        
        # Update status based on new expiration date
        self.update_status_from_expiration()
        return self.expires_at

    class Meta:
        # Order by last_extended_at (newest first), then by posted_at (newest first)
        ordering = ['-last_extended_at', '-posted_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['status', 'location']),
            models.Index(fields=['employer', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['last_extended_at']),
        ]
        verbose_name = _("ვაკანსია")
        verbose_name_plural = _("ვაკანსიები")


class RejectionReason(models.Model):
    """Model for predefined rejection reasons"""
    REASON_CHOICES = [
        ('ენის_ცოდნის_ნაკლებობა', _("ენის ცოდნის ნაკლებობა")),
        ('არასაკმარისი_გამოცდილება', _("არასაკმარისი გამოცდილება")),
        ('უნარების_ნაკლებობა', _("უნარების ნაკლებობა")),
        ('შეუსაბამო_საცხოვრებელი_ადგილი', _("შეუსაბამო საცხოვრებელი ადგილი")),
        ('სივიში_არ_არის_საკმარისი_ინფორმაცია', _("სივიში არ არის საკმარისი ინფორმაცია")),
        ('განათლების_შეუსაბამობა', _("განათლების შეუსაბამობა")),
        ('კარიერული_მიზნების_შეუსაბამობა', _("კარიერული მიზნების შეუსაბამობა")),
        ('სივის_ფორმატის_სტრუქტურის_ხარვეზები', _("სივის ფორმატის/სტრუქტურის ხარვეზები")),
        ('სერთიფიკატების_ლიცენზიების_ნაკლებობა', _("სერთიფიკატების/ლიცენზიების ნაკლებობა")),
        ('არარელევანტური_სამუშაო_ისტორია', _("არარელევანტური სამუშაო ისტორია")),
        ('სხვა', _("სხვა")),
    ]
    
    name = models.CharField(max_length=100, choices=REASON_CHOICES, unique=True, verbose_name=_("მიზეზი"))
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        verbose_name = _("უარის მიზეზი")
        verbose_name_plural = _("უარის მიზეზები") 