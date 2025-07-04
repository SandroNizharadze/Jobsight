from django.core.management.base import BaseCommand
from core.models import RejectionReason, JobApplication
from django.db.models import Count
from django.db import transaction

class Command(BaseCommand):
    help = 'Cleans up duplicate rejection reasons by merging them'

    def handle(self, *args, **options):
        # Find duplicate names
        duplicate_names = RejectionReason.objects.values('name') \
                         .annotate(name_count=Count('name')) \
                         .filter(name_count__gt=1)
        
        if not duplicate_names.exists():
            self.stdout.write(self.style.SUCCESS('No duplicate rejection reason names found'))
            return
        
        self.stdout.write(f'Found {duplicate_names.count()} duplicate rejection reason names')
        
        # Process each duplicate name
        with transaction.atomic():
            for dup in duplicate_names:
                name = dup['name']
                reasons = RejectionReason.objects.filter(name=name).order_by('id')
                
                if reasons.count() <= 1:
                    continue
                
                # Keep the first one (with lowest ID)
                primary_reason = reasons.first()
                duplicate_reasons = reasons.exclude(id=primary_reason.id)
                
                self.stdout.write(f'Processing duplicates for "{name}" - keeping ID {primary_reason.id}')
                
                # For each duplicate
                for reason in duplicate_reasons:
                    # Get all applications using this reason
                    applications = JobApplication.objects.filter(rejection_reasons=reason)
                    
                    # Add the primary reason to these applications
                    for app in applications:
                        app.rejection_reasons.add(primary_reason)
                        app.rejection_reasons.remove(reason)
                        self.stdout.write(f'  Updated application {app.id}')
                    
                    # Delete the duplicate reason
                    self.stdout.write(f'  Deleting duplicate reason ID {reason.id}')
                    reason.delete()
        
        self.stdout.write(self.style.SUCCESS('Cleanup complete')) 