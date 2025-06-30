from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import JobListing


class Command(BaseCommand):
    help = 'Updates job statuses based on expiration dates'

    def handle(self, *args, **options):
        # Get all jobs with status 'approved' or 'expired'
        jobs = JobListing.objects.filter(status__in=['approved', 'expired'])
        
        updated_count = 0
        for job in jobs:
            if job.update_status_from_expiration():
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} job statuses')
        ) 