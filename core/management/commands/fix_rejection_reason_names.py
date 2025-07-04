from django.core.management.base import BaseCommand
from core.models import RejectionReason

class Command(BaseCommand):
    help = 'Fixes rejection reason names by replacing underscores with spaces'

    def handle(self, *args, **options):
        fixed_count = 0
        
        for reason in RejectionReason.objects.all():
            if '_' in reason.name:
                old_name = reason.name
                # Replace underscores with spaces in the name
                reason.name = reason.name.replace('_', ' ')
                reason.save()
                
                self.stdout.write(self.style.SUCCESS(f'Fixed name: "{old_name}" → "{reason.name}"'))
                fixed_count += 1
        
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} rejection reason names'))
        else:
            self.stdout.write(self.style.SUCCESS('All rejection reason names are already correct')) 