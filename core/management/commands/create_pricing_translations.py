from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from core.models import (
    PricingPackage, PricingFeature, ComparisonTable, ComparisonRow,
    PricingPackageTranslation, PricingFeatureTranslation,
    ComparisonTableTranslation, ComparisonRowTranslation
)

class Command(BaseCommand):
    help = 'Creates initial translation records for pricing content'

    def handle(self, *args, **kwargs):
        self._create_package_translations()
        self._create_feature_translations()
        self._create_comparison_translations()
        
        self.stdout.write(self.style.SUCCESS('Initial pricing translations successfully created'))
    
    def _create_package_translations(self):
        """Create initial translation records for pricing packages"""
        self.stdout.write(self.style.SUCCESS('Creating package translations...'))
        
        for package in PricingPackage.objects.all():
            # English translations only
            PricingPackageTranslation.objects.get_or_create(
                package=package,
                language_code='en',
                defaults={
                    'name': self._get_english_package_name(package.package_type),
                    'description': self._get_english_package_description(package.package_type),
                }
            )
    
    def _create_feature_translations(self):
        """Create initial translation records for pricing features"""
        self.stdout.write(self.style.SUCCESS('Creating feature translations...'))
        
        for feature in PricingFeature.objects.all():
            # English translations only
            PricingFeatureTranslation.objects.get_or_create(
                feature=feature,
                language_code='en',
                defaults={
                    'text': self._get_english_feature_text(feature.text),
                }
            )
    
    def _create_comparison_translations(self):
        """Create initial translation records for comparison table and rows"""
        self.stdout.write(self.style.SUCCESS('Creating comparison translations...'))
        
        # Create translations for comparison table
        comparison_table = ComparisonTable.objects.filter(is_active=True).first()
        if comparison_table:
            ComparisonTableTranslation.objects.get_or_create(
                table=comparison_table,
                language_code='en',
                defaults={
                    'title': 'Package Comparison',
                    'subtitle': 'Detailed comparison to choose the right package for your business',
                }
            )
        
        # Create translations for comparison rows
        for row in ComparisonRow.objects.all():
            ComparisonRowTranslation.objects.get_or_create(
                row=row,
                language_code='en',
                defaults={
                    'feature_name': self._get_english_feature_name(row.feature_name),
                    'standard_value': self._get_english_value(row.standard_value),
                    'premium_value': self._get_english_value(row.premium_value),
                    'premium_plus_value': self._get_english_value(row.premium_plus_value),
                }
            )
    
    def _get_english_package_name(self, package_type):
        """Get English package name"""
        names = {
            'standard': 'Standard',
            'premium': 'Premium',
            'premium_plus': 'Premium Plus',
        }
        return names.get(package_type, package_type.title())
    
    def _get_english_package_description(self, package_type):
        """Get English package description"""
        descriptions = {
            'standard': 'Perfect for startup companies',
            'premium': 'Perfect for active employers',
            'premium_plus': 'Perfect for large companies',
        }
        return descriptions.get(package_type, '')
    
    def _get_english_feature_text(self, georgian_text):
        """Get English feature text based on Georgian text"""
        translations = {
            '1 განცხადება - პერიოდი 30 დღე': '1 job posting - 30 days period',
            'მთავარ გვერდზე ყოფნა': 'Featured on homepage',
            'ლოგოს გამოჩენა': 'Logo display',
            'დამსაქმებლის პროფილი და სივების ანალიტიკა': 'Employer profile and job analytics',
            'ძიებისას პრიორიტეტულობა: დაბალი': 'Search priority: Low',
            '5 განცხადება - პერიოდი 60 დღე': '5 job postings - 60 days period',
            'ძიებისას პრიორიტეტულობა: საშუალო': 'Search priority: Medium',
            'CV ბაზაზე წვდომა': 'Access to CV database',
            'ულიმიტო განცხადება - პერიოდი 90 დღე': 'Unlimited job postings - 90 days period',
            'ძიებისას პრიორიტეტულობა: მაღალი': 'Search priority: High',
            'პრიორიტეტული მხარდაჭერა': 'Priority support',
        }
        return translations.get(georgian_text, georgian_text)
    
    def _get_english_feature_name(self, georgian_name):
        """Get English feature name"""
        translations = {
            'განცხადებების რაოდენობა': 'Number of job postings',
            'განცხადების ვადა': 'Job posting period',
            'მთავარ გვერდზე ყოფნა': 'Featured on homepage',
            'CV ბაზაზე წვდომა': 'Access to CV database',
            'პრიორიტეტული მხარდაჭერა': 'Priority support',
        }
        return translations.get(georgian_name, georgian_name)
    
    def _get_english_value(self, georgian_value):
        """Get English value"""
        translations = {
            'არა': 'No',
            'კი': 'Yes',
            'ულიმიტო': 'Unlimited',
        }
        return translations.get(georgian_value, georgian_value)
