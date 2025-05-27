from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import JobListing
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Mark expired jobs with the expired status'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find jobs that have expired but still have 'approved' status
        expired_jobs = JobListing.objects.filter(
            status='approved',
            expires_at__lt=now
        )
        
        count = expired_jobs.count()
        if count > 0:
            # Update all expired jobs to have 'expired' status
            expired_jobs.update(status='expired')
            self.stdout.write(self.style.SUCCESS(f'Successfully marked {count} jobs as expired'))
            logger.info(f'Marked {count} jobs as expired')
        else:
            self.stdout.write(self.style.SUCCESS('No expired jobs found'))
            logger.info('No expired jobs found') 