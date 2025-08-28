from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import ComparisonRow, ComparisonRowTranslation

class Command(BaseCommand):
    help = 'Updates English translations for comparison table rows for production environment'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting translation update for production...'))
        
        try:
            with transaction.atomic():
                # Dictionary mapping Georgian feature names to English translations
                translations = {
                    'მთავარ გვერდზე გამოჩენა': 'Featured on homepage',
                    'პრემიუმის ნიშანი': 'Premium badge',
                    'პრემიუმ+ ნიშანი': 'Premium+ badge',
                    'განმასხვავებელი ნიშანი': 'Distinctive badge',
                    'ძიებისას პრიორიტეტულობა': 'Search priority',
                    'ლოგოს გამოჩენა': 'Logo display',
                    'დამსაქმებლის პროფილი': 'Employer profile',
                    'სივების ანალიტიკა': 'CV analytics',
                    'დამსაქმებლის პროფილი და სივების ანალიტიკა': 'Employer profile and CV analytics',
                    'სოც. ქსელებში გაზიარება': 'Social media sharing',
                    'მთავარ გვერდზე ყოფნა': 'Featured on homepage',
                    'სივების ბაზა (მალე)': 'CV database (coming soon)',
                    'სივების ბაზაზე წვდომა': 'CV database access',
                    'სივების ბაზაზე წვდომა (მალე)': 'CV database access (coming soon)',
                    'კანდიდატებისთვის უკუკავშირის დაბრუნების სისტემა': 'Candidate feedback system',
                    'ძიებისას პრიორიტეტულობა: დაბალი': 'Search priority: Low',
                    'ძიებისას პრიორიტეტულობა: საშუალო': 'Search priority: Medium',
                    'ძიებისას პრიორიტეტულობა: მაღალი': 'Search priority: High',
                    'სოც. ქსელებში გაზიარება ჯგუფური პოსტის სახით': 'Social media sharing as group post',
                    'სოც. ქსელებში გაზიარება ინდივიდუალური პოსტის სახით': 'Social media sharing as individual post',
                    'მთავარი გვერდის პირველი სექცია': 'First section of homepage',
                    'მთავარი გვერდის მეორე სექცია': 'Second section of homepage',
                }
                
                # Dictionary mapping Georgian values to English translations
                value_translations = {
                    'დაბალი': 'Low',
                    'საშუალო': 'Medium',
                    'მაღალი': 'High',
                    'პრემიუმი': 'Premium',
                    'პრემიუმ+': 'Premium+',
                    'სტანდარტული': 'Standard',
                    'მეორე სექცია': 'Second section',
                    'პირველი სექცია': 'First section',
                    'ჯგუფური პოსტი': 'Group post',
                    'ინდივიდუალური პოსტი': 'Individual post',
                    'ინდივიდუალური და ჯგუფური პოსტი': 'Individual and group post',
                    'უფასო': 'Free',
                    'საშუალო ხილვადობა': 'Medium visibility',
                    'მაღალი ხილვადობა': 'High visibility',
                    'მაქსიმალური ხილვადობა': 'Maximum visibility',
                    'აირჩიე': 'Choose',
                    'პოპულარული': 'Popular',
                    '1 განცხადება - პერიოდი 30 დღე': '1 job posting - 30 days period',
                    '1 job posting - 30 days period': '1 job posting - 30 days period',
                    'დღე': 'days',
                    'განცხადება': 'job posting',
                    'პერიოდი': 'period',
                }
                
                # First, ensure all rows have translation records
                self.stdout.write('Creating missing translation records...')
                rows = ComparisonRow.objects.all()
                created_count = 0
                
                for row in rows:
                    translation, created = ComparisonRowTranslation.objects.get_or_create(
                        row=row,
                        language_code='en',
                        defaults={
                            'feature_name': translations.get(row.feature_name, row.feature_name),
                            'standard_value': value_translations.get(row.standard_value, row.standard_value),
                            'premium_value': value_translations.get(row.premium_value, row.premium_value),
                            'premium_plus_value': value_translations.get(row.premium_plus_value, row.premium_plus_value),
                        }
                    )
                    if created:
                        created_count += 1
                
                self.stdout.write(self.style.SUCCESS(f'Created {created_count} new translation records'))
                
                # Now update all existing translations
                self.stdout.write('Updating existing translation records...')
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
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating translations: {str(e)}'))
            raise
        
        self.stdout.write(self.style.SUCCESS('Translation update completed successfully'))
