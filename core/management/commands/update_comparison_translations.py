from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import ComparisonRowTranslation

class Command(BaseCommand):
    help = 'Updates English translations for comparison table rows'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Dictionary mapping Georgian feature names to English translations
            translations = {
                'მთავარ გვერდზე გამოჩენა': 'Featured on homepage',
                'პრემიუმის ნიშანი': 'Premium badge',
                'ძიებისას პრიორიტეტულობა': 'Search priority',
                'ლოგოს გამოჩენა': 'Logo display',
                'დამსაქმებლის პროფილი': 'Employer profile',
                'სივების ანალიტიკა': 'CV analytics',
                'სოც. ქსელებში გაზიარება': 'Social media sharing',
            }
            
            # Dictionary mapping Georgian values to English translations
            value_translations = {
                'დაბალი': 'Low',
                'საშუალო': 'Medium',
                'მაღალი': 'High',
                'პრემიუმი': 'Premium',
                'პრემიუმ+': 'Premium+',
                'მეორე სექცია': 'Second section',
                'პირველი სექცია': 'First section',
                'ჯგუფური პოსტი': 'Group post',
                'ინდივიდუალური და ჯგუფური პოსტი': 'Individual and group post',
                'უფასო': 'Free',
            }
            
            # Get all English translations
            en_translations = ComparisonRowTranslation.objects.filter(language_code='en')
            updated_count = 0
            
            for translation in en_translations:
                # Update feature name if it's in our dictionary
                if translation.row.feature_name in translations:
                    translation.feature_name = translations[translation.row.feature_name]
                    updated_count += 1
                
                # Update standard value if it's in our value dictionary
                if translation.row.standard_value in value_translations:
                    translation.standard_value = value_translations[translation.row.standard_value]
                    updated_count += 1
                
                # Update premium value if it's in our value dictionary
                if translation.row.premium_value in value_translations:
                    translation.premium_value = value_translations[translation.row.premium_value]
                    updated_count += 1
                
                # Update premium plus value if it's in our value dictionary
                if translation.row.premium_plus_value in value_translations:
                    translation.premium_plus_value = value_translations[translation.row.premium_plus_value]
                    updated_count += 1
                
                translation.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} translations'))

