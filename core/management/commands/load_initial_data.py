from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from core.models import PricingPackage, PricingFeature, ComparisonTable, ComparisonRow

class Command(BaseCommand):
    help = 'Loads initial data for the pricing packages'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating initial pricing packages...'))
        
        # Create Standard Package
        standard_package, created = PricingPackage.objects.update_or_create(
            package_type='standard',
            defaults={
                'name': _('სტანდარტული'),
                'original_price': 40.00,
                'current_price': 0.00,
                'is_free': True,
                'description': _('იდეალურია დამწყები კომპანიებისთვის'),
                'display_order': 1,
                'has_discount_badge': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created standard package: {str(standard_package.name)}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated standard package: {str(standard_package.name)}'))
        
        # Standard package features
        standard_features = [
            {'text': _('1 განცხადება - პერიოდი 30 დღე'), 'is_included': True},
            {'text': _('მთავარ გვერდზე ყოფნა'), 'is_included': False},
            {'text': _('ლოგოს გამოჩენა'), 'is_included': True},
            {'text': _('დამსაქმებლის პროფილი და სივების ანალიტიკა'), 'is_included': True},
            {'text': _('ძიებისას პრიორიტეტულობა: დაბალი'), 'is_included': True},
        ]
        
        # Delete existing features
        PricingFeature.objects.filter(package=standard_package).delete()
        
        # Create new features
        for i, feature in enumerate(standard_features):
            PricingFeature.objects.create(
                package=standard_package,
                text=feature['text'],
                is_included=feature['is_included'],
                display_order=i+1
            )
        
        # Create Premium Package
        premium_package, created = PricingPackage.objects.update_or_create(
            package_type='premium',
            defaults={
                'name': _('პრემიუმი'),
                'original_price': 95.00,
                'current_price': 50.00,
                'is_popular': True,
                'description': _('იდეალურია აქტიური დამსაქმებლებისთვის'),
                'display_order': 2,
                'has_discount_badge': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created premium package: {str(premium_package.name)}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated premium package: {str(premium_package.name)}'))
        
        # Premium package features
        premium_features = [
            {'text': _('1 განცხადება - პერიოდი 30 დღე'), 'is_included': True},
            {'text': _('მთავარი გვერდის მეორე სექცია'), 'is_included': True},
            {'text': _('ლოგოს გამოჩენა'), 'is_included': True},
            {'text': _('სოც. ქსელებში გაზიარება ჯგუფური პოსტის სახით'), 'is_included': True},
            {'text': _('პრემიუმის ნიშანი'), 'is_included': True},
            {'text': _('ძიებისას პრიორიტეტულობა: საშუალო'), 'is_included': True},
            {'text': _('დამსაქმებლის პროფილი და სივების ანალიტიკა'), 'is_included': True},
            {'text': _('სივების ბაზაზე წვდომა'), 'is_included': True},
        ]
        
        # Delete existing features
        PricingFeature.objects.filter(package=premium_package).delete()
        
        # Create new features
        for i, feature in enumerate(premium_features):
            PricingFeature.objects.create(
                package=premium_package,
                text=feature['text'],
                is_included=feature['is_included'],
                display_order=i+1
            )
        
        # Create Premium Plus Package
        premium_plus_package, created = PricingPackage.objects.update_or_create(
            package_type='premium_plus',
            defaults={
                'name': _('პრემიუმ+'),
                'original_price': 120.00,
                'current_price': 60.00,
                'description': _('იდეალურია მაღალი კონკურენციის პოზიციებისთვის'),
                'display_order': 3,
                'has_discount_badge': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created premium plus package: {str(premium_plus_package.name)}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated premium plus package: {str(premium_plus_package.name)}'))
        
        # Premium Plus package features
        premium_plus_features = [
            {'text': _('1 განცხადება - პერიოდი 30 დღე'), 'is_included': True},
            {'text': _('მთავარი გვერდის პირველი სექცია'), 'is_included': True},
            {'text': _('ლოგოს გამოჩენა'), 'is_included': True},
            {'text': _('სოც. ქსელებში გაზიარება ინდივიდუალური და ჯგუფური პოსტის სახით'), 'is_included': True},
            {'text': _('პრემიუმ+ ნიშანი'), 'is_included': True},
            {'text': _('ძიებისას პრიორიტეტულობა: მაღალი'), 'is_included': True},
            {'text': _('დამსაქმებლის პროფილი და სივების ანალიტიკა'), 'is_included': True},
            {'text': _('სივების ბაზაზე წვდომა'), 'is_included': True},
            {'text': _('სპეციალური გვერდი კომპანიისთვის'), 'is_included': True},
        ]
        
        # Delete existing features
        PricingFeature.objects.filter(package=premium_plus_package).delete()
        
        # Create new features
        for i, feature in enumerate(premium_plus_features):
            PricingFeature.objects.create(
                package=premium_plus_package,
                text=feature['text'],
                is_included=feature['is_included'],
                display_order=i+1
            )
            
        # Create Comparison Table
        self.stdout.write(self.style.SUCCESS('Creating comparison table...'))
        
        comparison_table, created = ComparisonTable.objects.update_or_create(
            id=1,
            defaults={
                'title': _('პაკეტების შედარება'),
                'subtitle': _('დეტალური შედარება, რომ აირჩიოთ თქვენი ბიზნესისთვის შესაფერისი პაკეტი'),
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created comparison table: {str(comparison_table.title)}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated comparison table: {str(comparison_table.title)}'))
        
        # Comparison table rows
        comparison_rows = [
            {
                'feature_name': _('მთავარ გვერდზე გამოჩენა'),
                'display_type': 'text',
                'standard_value': '',
                'standard_included': False,
                'premium_value': _('მეორე სექცია'),
                'premium_included': True,
                'premium_plus_value': _('პირველი სექცია'),
                'premium_plus_included': True,
                'display_order': 1
            },
            {
                'feature_name': _('პრემიუმის ნიშანი'),
                'display_type': 'badge',
                'standard_value': '',
                'standard_included': False,
                'premium_value': _('პრემიუმი'),
                'premium_included': True,
                'premium_plus_value': _('პრემიუმ+'),
                'premium_plus_included': True,
                'display_order': 2
            },
            {
                'feature_name': _('ძიებისას პრიორიტეტულობა'),
                'display_type': 'badge',
                'standard_value': _('დაბალი'),
                'standard_included': True,
                'premium_value': _('საშუალო'),
                'premium_included': True,
                'premium_plus_value': _('მაღალი'),
                'premium_plus_included': True,
                'display_order': 3
            },
            {
                'feature_name': _('ლოგოს გამოჩენა'),
                'display_type': 'checkmark',
                'standard_value': '',
                'standard_included': True,
                'premium_value': '',
                'premium_included': True,
                'premium_plus_value': '',
                'premium_plus_included': True,
                'display_order': 4
            },
            {
                'feature_name': _('დამსაქმებლის პროფილი'),
                'display_type': 'checkmark',
                'standard_value': '',
                'standard_included': True,
                'premium_value': '',
                'premium_included': True,
                'premium_plus_value': '',
                'premium_plus_included': True,
                'display_order': 5
            },
            {
                'feature_name': _('სივების ანალიტიკა'),
                'display_type': 'checkmark',
                'standard_value': '',
                'standard_included': True,
                'premium_value': '',
                'premium_included': True,
                'premium_plus_value': '',
                'premium_plus_included': True,
                'display_order': 6
            },
            {
                'feature_name': _('სოც. ქსელებში გაზიარება'),
                'display_type': 'text',
                'standard_value': '',
                'standard_included': False,
                'premium_value': _('ჯგუფური პოსტი'),
                'premium_included': True,
                'premium_plus_value': _('ინდივიდუალური და ჯგუფური პოსტი'),
                'premium_plus_included': True,
                'display_order': 7
            },
        ]
        
        # Delete existing rows
        ComparisonRow.objects.filter(table=comparison_table).delete()
        
        # Create new rows
        for row_data in comparison_rows:
            ComparisonRow.objects.create(
                table=comparison_table,
                feature_name=row_data['feature_name'],
                display_type=row_data['display_type'],
                standard_value=row_data['standard_value'],
                standard_included=row_data['standard_included'],
                premium_value=row_data['premium_value'],
                premium_included=row_data['premium_included'],
                premium_plus_value=row_data['premium_plus_value'],
                premium_plus_included=row_data['premium_plus_included'],
                display_order=row_data['display_order']
            )
            
        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully')) 