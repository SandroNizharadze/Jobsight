from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from core.models import UserProfile
import os
import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Upload a test CV to S3 for testing purposes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting test CV upload...'))
        
        # Check if S3 is enabled
        if not settings.USE_S3:
            self.stdout.write(self.style.ERROR('S3 is not enabled. Set USE_S3=True in your environment.'))
            return
            
        # Create test user if it doesn't exist
        username = 'testcvuser'
        email = 'testcv@example.com'
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Using existing user: {username}')
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, email=email, password='password123')
            self.stdout.write(f'Created new user: {username}')
        
        # Get or create UserProfile
        try:
            profile = UserProfile.objects.get(user=user)
            self.stdout.write(f'Using existing profile for user: {username}')
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(
                user=user,
                role='candidate',
                visible_to_employers=True,
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(f'Created new profile for user: {username}')
        
        # Create a simple test PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Resources<<>>/Contents 4 0 R>>endobj 4 0 obj<</Length 22>>stream\nBT\n/F1 12 Tf\n100 700 Td\n(Test CV) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\n0000000182 00000 n\ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n254\n%%EOF"
        
        # Save the test CV to the profile
        filename = 'test_cv.pdf'
        profile.cv.save(f'cvs/{filename}', ContentFile(pdf_content), save=True)
        
        self.stdout.write(self.style.SUCCESS(f'Saved test CV to profile: {profile.cv.name}'))
        
        # Verify the file exists in S3
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Get the file key
            file_key = profile.cv.name
            if not file_key.startswith('media/private/'):
                file_key = f'media/private/{file_key}'
            
            # Check if file exists in S3
            s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            
            # Generate a signed URL
            url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': file_key
                },
                ExpiresIn=3600
            )
            
            self.stdout.write(self.style.SUCCESS(f'File exists in S3 bucket: {settings.AWS_STORAGE_BUCKET_NAME}'))
            self.stdout.write(self.style.SUCCESS(f'S3 key: {file_key}'))
            self.stdout.write(self.style.SUCCESS(f'Signed URL (valid for 1 hour): {url}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error verifying file in S3: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Test CV upload completed.')) 