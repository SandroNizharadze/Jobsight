from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import PricingPackage, PricingPackageTranslation

class Command(BaseCommand):
    help = 'Updates package descriptions with visibility information'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Updating package descriptions...'))
        
        try:
            with transaction.atomic():
                # Update Georgian descriptions
                standard = PricingPackage.objects.get(package_type='standard')
                premium = PricingPackage.objects.get(package_type='premium')
                premium_plus = PricingPackage.objects.get(package_type='premium_plus')
                
                standard.description = 'საშუალო ხილვადობა'
                premium.description = 'მაღალი ხილვადობა'
                premium_plus.description = 'მაქსიმალური ხილვადობა'
                
                standard.save()
                premium.save()
                premium_plus.save()
                
                # Update English translations
                en_standard = PricingPackageTranslation.objects.get(package=standard, language_code='en')
                en_premium = PricingPackageTranslation.objects.get(package=premium, language_code='en')
                en_premium_plus = PricingPackageTranslation.objects.get(package=premium_plus, language_code='en')
                
                en_standard.description = 'Medium visibility'
                en_premium.description = 'High visibility'
                en_premium_plus.description = 'Maximum visibility'
                
                en_standard.save()
                en_premium.save()
                en_premium_plus.save()
                
                self.stdout.write(self.style.SUCCESS('Successfully updated package descriptions'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating package descriptions: {str(e)}'))
            raise
