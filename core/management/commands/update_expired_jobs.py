import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Q
from core.models import JobListing, EmployerProfile

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates job statuses for expired jobs and logs employers who lose Premium+ access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only show what would be changed without actually updating the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()
        
        self.stdout.write(self.style.NOTICE('Checking for expired jobs...'))
        
        # Find all jobs that have expired but still have 'approved' status
        expired_jobs = JobListing.objects.filter(
            status='approved',
            expires_at__lt=now,
            deleted_at__isnull=True
        )
        
        expired_count = expired_jobs.count()
        
        if expired_count == 0:
            self.stdout.write(self.style.SUCCESS('No expired jobs found!'))
            return
            
        self.stdout.write(self.style.WARNING(f'Found {expired_count} expired jobs'))
        
        # Update job statuses
        if not dry_run:
            expired_jobs.update(status='expired')
            self.stdout.write(self.style.SUCCESS(f'Updated {expired_count} jobs to expired status'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Would update {expired_count} jobs to expired status'))
        
        # Now check for employers who will lose Premium+ access
        self.stdout.write(self.style.NOTICE('Checking for employers losing Premium+ access...'))
        
        # Get all employers who have Premium+ jobs that just expired
        employers_with_expired_premium_plus = set(expired_jobs.filter(
            premium_level='premium_plus'
        ).values_list('employer_id', flat=True))
        
        # For these employers, check if they still have any active Premium+ jobs
        employers_losing_access = []
        
        for employer_id in employers_with_expired_premium_plus:
            active_premium_plus_count = JobListing.objects.filter(
                employer_id=employer_id,
                premium_level='premium_plus',
                status='approved',
                expires_at__gt=now,
                deleted_at__isnull=True
            ).count()
            
            if active_premium_plus_count == 0:
                try:
                    employer = EmployerProfile.objects.get(id=employer_id)
                    employers_losing_access.append(employer)
                    
                    # Log the event
                    self.stdout.write(self.style.WARNING(
                        f'Employer {employer.company_name} (ID: {employer.id}) is losing Premium+ access'
                    ))
                    logger.info(f'Employer {employer.company_name} (ID: {employer.id}) has lost Premium+ access due to job expiration')
                except EmployerProfile.DoesNotExist:
                    continue
        
        # Summary output
        if employers_losing_access:
            self.stdout.write(self.style.WARNING(
                f'{len(employers_losing_access)} employers will lose Premium+ access'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('No employers will lose Premium+ access')) 