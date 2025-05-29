import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import UserProfile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix CV file paths in the database and verify they exist in S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Just show what would be done without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('Starting CV path fix operation'))
        
        # Check if S3 is enabled
        if not hasattr(settings, 'USE_S3') or not settings.USE_S3:
            self.stdout.write(self.style.ERROR('S3 storage is not enabled. Aborting operation.'))
            return
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            region_name=settings.AWS_S3_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Get all profiles with CVs
        profiles = UserProfile.objects.exclude(cv__isnull=True).exclude(cv='')
        self.stdout.write(f"Found {profiles.count()} profiles with CVs")
        
        fixed = 0
        errors = 0
        not_found = 0
        
        for profile in profiles:
            if not profile.cv:
                continue
                
            original_path = profile.cv.name
            self.stdout.write(f"Processing CV for user {profile.user.username}: {original_path}")
            
            # Define possible path formats
            path_formats = [
                original_path,  # Original path as stored in DB
                f"media/private/{original_path}",  # With media/private prefix
                f"private/{original_path}",  # With private prefix
                f"cvs/{original_path.split('/')[-1]}" if '/' in original_path else f"cvs/{original_path}",  # Just cvs/filename
            ]
            
            # If the path already starts with cvs/ but doesn't have the expected structure
            if original_path.startswith('cvs/'):
                path_formats.append(original_path)
            elif not any(fmt.startswith('cvs/') for fmt in path_formats):
                path_formats.append(f"cvs/{original_path}")
            
            # Remove duplicates
            path_formats = list(set(path_formats))
            
            found = False
            working_path = None
            
            # Check each path format
            for path in path_formats:
                try:
                    self.stdout.write(f"  Checking S3 for: {path}")
                    s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=path)
                    self.stdout.write(self.style.SUCCESS(f"  ✓ File exists at: {path}"))
                    found = True
                    working_path = path
                    break
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        self.stdout.write(f"  ✗ File not found at: {path}")
                    else:
                        self.stdout.write(self.style.ERROR(f"  ! Error checking path {path}: {str(e)}"))
            
            if found:
                # If the path is different from what's in the database, update it
                if working_path != original_path:
                    if not dry_run:
                        profile.cv.name = working_path
                        profile.save(update_fields=['cv'])
                        self.stdout.write(self.style.SUCCESS(f"  Updated path from {original_path} to {working_path}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"  [DRY RUN] Would update path from {original_path} to {working_path}"))
                    fixed += 1
                else:
                    self.stdout.write(f"  Path is already correct: {original_path}")
            else:
                self.stdout.write(self.style.ERROR(f"  Could not find CV file for {profile.user.username} in any expected location"))
                not_found += 1
        
        self.stdout.write(self.style.SUCCESS(f"Operation complete. Fixed: {fixed}, Not found: {not_found}, Errors: {errors}"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("This was a dry run. No changes were made to the database.")) 