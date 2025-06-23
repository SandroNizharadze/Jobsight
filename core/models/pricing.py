from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class PricingPackage(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('standard', _('Standard')),
        ('premium', _('Premium')),
        ('premium_plus', _('Premium Plus')),
    ]
    
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, unique=True, verbose_name=_("Package Type"))
    name = models.CharField(max_length=100, verbose_name=_("Package Name"))
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Original Price"))
    current_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Current Price"))
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    is_popular = models.BooleanField(default=False, verbose_name=_("Is Popular"))
    is_free = models.BooleanField(default=False, verbose_name=_("Is Free"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Display Order"))
    has_discount_badge = models.BooleanField(default=True, verbose_name=_("Show Discount Badge"))
    
    class Meta:
        verbose_name = _("Pricing Package")
        verbose_name_plural = _("Pricing Packages")
        ordering = ['display_order', 'package_type']
    
    def __str__(self):
        return self.name
    
    def has_discount(self):
        return self.original_price and self.current_price < self.original_price
    
    def get_absolute_url(self):
        return reverse('pricing')


class PricingFeature(models.Model):
    package = models.ForeignKey(PricingPackage, on_delete=models.CASCADE, related_name='features', verbose_name=_("Package"))
    text = models.CharField(max_length=255, verbose_name=_("Feature Text"))
    is_included = models.BooleanField(default=True, verbose_name=_("Is Included"))
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Display Order"))
    
    class Meta:
        verbose_name = _("Pricing Feature")
        verbose_name_plural = _("Pricing Features")
        ordering = ['display_order', 'id']
    
    def __str__(self):
        return f"{self.package.name} - {self.text}"


class ComparisonTable(models.Model):
    """Model to manage the pricing comparison table separately from package features"""
    title = models.CharField(max_length=255, verbose_name=_("Table Title"), default=_("პაკეტების შედარება"))
    subtitle = models.CharField(max_length=255, verbose_name=_("Table Subtitle"), 
                               default=_("დეტალური შედარება, რომ აირჩიოთ თქვენი ბიზნესისთვის შესაფერისი პაკეტი"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    
    class Meta:
        verbose_name = _("Comparison Table")
        verbose_name_plural = _("Comparison Tables")
    
    def __str__(self):
        return self.title


class ComparisonRow(models.Model):
    """Individual row in the pricing comparison table"""
    DISPLAY_TYPE_CHOICES = [
        ('text', _('Text')),
        ('checkmark', _('Checkmark')),
        ('badge', _('Badge')),
        ('special', _('Special Format')),
    ]
    
    table = models.ForeignKey(ComparisonTable, on_delete=models.CASCADE, related_name='rows', verbose_name=_("Comparison Table"))
    feature_name = models.CharField(max_length=255, verbose_name=_("Feature Name"))
    display_type = models.CharField(max_length=20, choices=DISPLAY_TYPE_CHOICES, default='checkmark', 
                                   verbose_name=_("Display Type"))
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name=_("Display Order"))
    
    # Values for each package type
    standard_value = models.CharField(max_length=255, verbose_name=_("Standard Value"), blank=True)
    standard_included = models.BooleanField(default=False, verbose_name=_("Included in Standard"))
    
    premium_value = models.CharField(max_length=255, verbose_name=_("Premium Value"), blank=True)
    premium_included = models.BooleanField(default=True, verbose_name=_("Included in Premium"))
    
    premium_plus_value = models.CharField(max_length=255, verbose_name=_("Premium Plus Value"), blank=True)
    premium_plus_included = models.BooleanField(default=True, verbose_name=_("Included in Premium Plus"))
    
    class Meta:
        verbose_name = _("Comparison Row")
        verbose_name_plural = _("Comparison Rows")
        ordering = ['display_order', 'id']
    
    def __str__(self):
        return f"{self.table.title} - {self.feature_name}" 