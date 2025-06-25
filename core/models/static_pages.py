from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

class StaticPage(models.Model):
    PRIVACY_POLICY = 'privacy_policy'
    TERMS_CONDITIONS = 'terms_conditions'
    
    PAGE_TYPES = [
        (PRIVACY_POLICY, _('Privacy Policy')),
        (TERMS_CONDITIONS, _('Terms & Conditions')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    page_type = models.CharField(
        _('Page Type'),
        max_length=50,
        choices=PAGE_TYPES,
        unique=True
    )
    content = RichTextField(_('Content'))
    last_updated = models.DateTimeField(_('Last Updated'), auto_now=True)
    
    class Meta:
        verbose_name = _('Static Page')
        verbose_name_plural = _('Static Pages')
    
    def __str__(self):
        return self.title 