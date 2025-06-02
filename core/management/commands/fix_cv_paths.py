import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import UserProfile
import logging
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fix CV file paths in the database to ensure proper S3 access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Just show what would be done without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('Starting CV path fix...'))
        
        # Check if S3 is enabled
        if not settings.USE_S3:
            self.stdout.write(self.style.WARNING('S3 is not enabled. Set USE_S3=True in your environment.'))
            return
            
        # Initialize S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Get all profiles with CVs
        profiles = UserProfile.objects.filter(cv__isnull=False).exclude(cv='')
        self.stdout.write(f'Found {profiles.count()} profiles with CV files')
        
        fixed_count = 0
        error_count = 0
        
        for profile in profiles:
            try:
                # Get the current CV path
                current_path = profile.cv.name
                self.stdout.write(f'Processing CV: {current_path}')
                
                # If the path starts with 'media/private/', remove it to make it relative
                if current_path.startswith('media/private/'):
                    new_path = current_path.replace('media/private/', '')
                    
                    # Check if the file exists in S3
                    try:
                        s3.head_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=f'media/private/{new_path}'
                        )
                        
                        # Update the path in the database
                        profile.cv.name = new_path
                        profile.save(update_fields=['cv'])
                        self.stdout.write(self.style.SUCCESS(f'Fixed path: {current_path} -> {new_path}'))
                        fixed_count += 1
                        
                    except ClientError as e:
                        if e.response['Error']['Code'] == '404':
                            self.stdout.write(self.style.WARNING(f'File not found in S3: media/private/{new_path}'))
                            
                            # Try to find the file with just the filename
                            filename = os.path.basename(new_path)
                            try:
                                s3.head_object(
                                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                    Key=f'media/private/cvs/{filename}'
                                )
                                # Update to the correct path
                                profile.cv.name = f'cvs/{filename}'
                                profile.save(update_fields=['cv'])
                                self.stdout.write(self.style.SUCCESS(f'Fixed path using filename: {current_path} -> cvs/{filename}'))
                                fixed_count += 1
                            except ClientError:
                                self.stdout.write(self.style.ERROR(f'Could not find file in S3: {filename}'))
                                error_count += 1
                        else:
                            self.stdout.write(self.style.ERROR(f'Error checking S3: {str(e)}'))
                            error_count += 1
                
                # If path doesn't start with cvs/ but is a CV file, fix it
                elif not current_path.startswith('cvs/') and current_path.endswith(('.pdf', '.doc', '.docx')):
                    filename = os.path.basename(current_path)
                    new_path = f'cvs/{filename}'
                    
                    # Check if the file exists in S3 with the new path
                    try:
                        s3.head_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=f'media/private/{new_path}'
                        )
                        
                        # Update the path in the database
                        profile.cv.name = new_path
                        profile.save(update_fields=['cv'])
                        self.stdout.write(self.style.SUCCESS(f'Fixed path: {current_path} -> {new_path}'))
                        fixed_count += 1
                        
                    except ClientError:
                        self.stdout.write(self.style.WARNING(f'File not found in S3: media/private/{new_path}'))
                        error_count += 1
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing profile {profile.id}: {str(e)}'))
                error_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'CV path fix completed. Fixed: {fixed_count}, Errors: {error_count}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("This was a dry run. No changes were made to the database.")) 