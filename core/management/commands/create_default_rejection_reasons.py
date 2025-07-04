from django.core.management.base import BaseCommand
from core.models import RejectionReason

class Command(BaseCommand):
    help = 'Creates default rejection reasons if they do not exist'

    def handle(self, *args, **options):
        default_reasons = [
            {'code': 'არასაკმარისი_კვალიფიკაცია', 'name': 'არასაკმარისი კვალიფიკაცია'},
            {'code': 'გამოცდილების_ნაკლებობა', 'name': 'გამოცდილების ნაკლებობა'},
            {'code': 'უნარების_შეუსაბამობა', 'name': 'უნარების შეუსაბამობა'},
            {'code': 'სხვა_კანდიდატი_შეირჩა', 'name': 'სხვა კანდიდატი შეირჩა'},
            {'code': 'პოზიცია_შეივსო', 'name': 'პოზიცია შეივსო'},
            {'code': 'ანაზღაურების_მოლოდინები', 'name': 'ანაზღაურების მოლოდინები'},
            {'code': 'კომუნიკაციის_პრობლემები', 'name': 'კომუნიკაციის პრობლემები'},
            {'code': 'პოზიცია_გაუქმდა', 'name': 'პოზიცია გაუქმდა'},
        ]
        
        created_count = 0
        updated_count = 0
        
        for reason_data in default_reasons:
            reason, created = RejectionReason.objects.update_or_create(
                code=reason_data['code'],
                defaults={'name': reason_data['name']}
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new rejection reasons'))
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} existing rejection reasons')) 