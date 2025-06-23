from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
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
    description = CKEditor5Field(verbose_name=_("ვაკანსიის აღწერა"))
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True, verbose_name=_("მინიმალური ხელფასი"))
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("მაქსიმალური ხელფასი"))
    salary_type = models.CharField(max_length=50, choices=SALARY_TYPE_CHOICES, default='თვეში', verbose_name=_("ხელფასის ტიპი"))
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, db_index=True, verbose_name=_("კატეგორია"))
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, db_index=True, verbose_name=_("ლოკაცია"))
    employer = models.ForeignKey('EmployerProfile', on_delete=models.CASCADE, related_name='job_listings', verbose_name=_("დამსაქმებელი"))
    posted_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("გამოქვეყნების თარიღი"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("განახლების თარიღი"))
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name=_("ვადის გასვლის თარიღი"))
    interests = models.CharField(max_length=255, blank=True, verbose_name=_("ინტერესები"))
    fields = models.CharField(max_length=255, blank=True, verbose_name=_("სფეროები"))
    experience = models.CharField(max_length=100, choices=EXPERIENCE_CHOICES, db_index=True, verbose_name=_("გამოცდილება"))
    job_preferences = models.CharField(max_length=255, choices=JOB_PREFERENCE_CHOICES, verbose_name=_("სამუშაო გრაფიკი"))
    considers_students = models.BooleanField(default=False, choices=CONSIDERS_STUDENTS_CHOICES, verbose_name=_("განიხილავს სტუდენტებს"))
    STATUS_CHOICES = [
        ('pending_review', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review', db_index=True, verbose_name=_("სტატუსი"))
    admin_feedback = models.TextField(blank=True, verbose_name=_("ადმინის უკუკავშირი"))
    PREMIUM_LEVEL_CHOICES = [
        ('standard', _('Standard')),
        ('premium', _('Premium')),
        ('premium_plus', _('Premium +')),
    ]
    premium_level = models.CharField(max_length=20, choices=PREMIUM_LEVEL_CHOICES, default='standard', db_index=True, verbose_name=_("პრემიუმ დონე"))
    georgian_language_only = models.BooleanField(choices=[(True, 'კი'), (False, 'არა')], default=False, verbose_name=_("პოზიციაზე მოთხოვნილია მხოლოდ ქართული ენის ცოდნა"))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("ნახვების რაოდენობა"))

    def __str__(self):
        return f"{self.title} at {self.company}"

    def is_expired(self):
        """Check if the job posting has expired"""
        if self.status == 'expired':
            return True
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
    
    def extend_expiration(self, days=30):
        """Extend the job expiration date by the specified number of days"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=days)
        else:
            # If job is expired, extend from current date
            if self.is_expired():
                self.expires_at = timezone.now() + timedelta(days=days)
            # Otherwise extend from current expiration date
            else:
                self.expires_at = self.expires_at + timedelta(days=days)
        
        self.save(update_fields=['expires_at'])
        return self.expires_at

    class Meta:
        ordering = ['-posted_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['status', 'location']),
            models.Index(fields=['employer', 'status']),
            models.Index(fields=['expires_at']),
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