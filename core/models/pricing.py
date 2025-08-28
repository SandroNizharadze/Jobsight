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
    
    def get_translated_name(self, language_code='ka'):
        """Get translated name for the package"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.name if translation.name else self.name
        except PricingPackageTranslation.DoesNotExist:
            return self.name
    
    def get_translated_description(self, language_code='ka'):
        """Get translated description for the package"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.description if translation.description else self.description
        except PricingPackageTranslation.DoesNotExist:
            return self.description


class PricingPackageTranslation(models.Model):
    """Admin-controlled translations for pricing packages"""
    LANGUAGE_CHOICES = [
        ('ka', _('Georgian')),
        ('en', _('English')),
    ]
    
    package = models.ForeignKey(PricingPackage, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Package"))
    language_code = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_("Language"))
    name = models.CharField(max_length=100, blank=True, verbose_name=_("Translated Name"))
    description = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Description"))
    
    class Meta:
        verbose_name = _("Pricing Package Translation")
        verbose_name_plural = _("Pricing Package Translations")
        unique_together = ('package', 'language_code')
        ordering = ['package__display_order', 'language_code']
    
    def __str__(self):
        return f"{self.package.name} - {self.get_language_code_display()}"


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
    
    def get_translated_text(self, language_code='ka'):
        """Get translated text for the feature"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.text if translation.text else self.text
        except PricingFeatureTranslation.DoesNotExist:
            return self.text


class PricingFeatureTranslation(models.Model):
    """Admin-controlled translations for pricing features"""
    LANGUAGE_CHOICES = [
        ('ka', _('Georgian')),
        ('en', _('English')),
    ]
    
    feature = models.ForeignKey(PricingFeature, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Feature"))
    language_code = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_("Language"))
    text = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Text"))
    
    class Meta:
        verbose_name = _("Pricing Feature Translation")
        verbose_name_plural = _("Pricing Feature Translations")
        unique_together = ('feature', 'language_code')
        ordering = ['feature__display_order', 'language_code']
    
    def __str__(self):
        return f"{self.feature.text} - {self.get_language_code_display()}"


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
    
    def get_translated_title(self, language_code='ka'):
        """Get translated title for the comparison table"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.title if translation.title else self.title
        except ComparisonTableTranslation.DoesNotExist:
            return self.title
    
    def get_translated_subtitle(self, language_code='ka'):
        """Get translated subtitle for the comparison table"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.subtitle if translation.subtitle else self.subtitle
        except ComparisonTableTranslation.DoesNotExist:
            return self.subtitle


class ComparisonTableTranslation(models.Model):
    """Admin-controlled translations for comparison table"""
    LANGUAGE_CHOICES = [
        ('ka', _('Georgian')),
        ('en', _('English')),
    ]
    
    table = models.ForeignKey(ComparisonTable, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Table"))
    language_code = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_("Language"))
    title = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Title"))
    subtitle = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Subtitle"))
    
    class Meta:
        verbose_name = _("Comparison Table Translation")
        verbose_name_plural = _("Comparison Table Translations")
        unique_together = ('table', 'language_code')
        ordering = ['table__id', 'language_code']
    
    def __str__(self):
        return f"{self.table.title} - {self.get_language_code_display()}"


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
    
    def get_translated_feature_name(self, language_code='ka'):
        """Get translated feature name"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.feature_name if translation.feature_name else self.feature_name
        except ComparisonRowTranslation.DoesNotExist:
            return self.feature_name
    
    def get_translated_standard_value(self, language_code='ka'):
        """Get translated standard value"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.standard_value if translation.standard_value else self.standard_value
        except ComparisonRowTranslation.DoesNotExist:
            return self.standard_value
    
    def get_translated_premium_value(self, language_code='ka'):
        """Get translated premium value"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.premium_value if translation.premium_value else self.premium_value
        except ComparisonRowTranslation.DoesNotExist:
            return self.premium_value
    
    def get_translated_premium_plus_value(self, language_code='ka'):
        """Get translated premium plus value"""
        try:
            translation = self.translations.get(language_code=language_code)
            return translation.premium_plus_value if translation.premium_plus_value else self.premium_plus_value
        except ComparisonRowTranslation.DoesNotExist:
            return self.premium_plus_value


class ComparisonRowTranslation(models.Model):
    """Admin-controlled translations for comparison row values"""
    LANGUAGE_CHOICES = [
        ('ka', _('Georgian')),
        ('en', _('English')),
    ]
    
    row = models.ForeignKey(ComparisonRow, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Row"))
    language_code = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, verbose_name=_("Language"))
    feature_name = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Feature Name"))
    standard_value = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Standard Value"))
    premium_value = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Premium Value"))
    premium_plus_value = models.CharField(max_length=255, blank=True, verbose_name=_("Translated Premium Plus Value"))
    
    class Meta:
        verbose_name = _("Comparison Row Translation")
        verbose_name_plural = _("Comparison Row Translations")
        unique_together = ('row', 'language_code')
        ordering = ['row__display_order', 'language_code']
    
    def __str__(self):
        return f"{self.row.feature_name} - {self.get_language_code_display()}" 