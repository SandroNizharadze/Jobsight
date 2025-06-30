from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import JobListing


class Command(BaseCommand):
    help = 'Updates job statuses based on expiration dates and initializes last_extended_at field'

    def handle(self, *args, **options):
        # Get all jobs with status 'approved' or 'expired'
        jobs = JobListing.objects.filter(status__in=['approved', 'expired'])
        
        updated_count = 0
        initialized_count = 0
        
        for job in jobs:
            # Update status based on expiration date
            if job.update_status_from_expiration():
                updated_count += 1
                
            # Initialize last_extended_at if it's null
            if job.last_extended_at is None:
                job.last_extended_at = job.posted_at
                job.save(update_fields=['last_extended_at'])
                initialized_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} job statuses and initialized {initialized_count} last_extended_at fields')
        ) 