from django.core.management.base import BaseCommand
from core.models import RejectionReason, JobApplication
from django.db import transaction

class Command(BaseCommand):
    help = 'Merges similar rejection reasons'

    def handle(self, *args, **options):
        # Define groups of similar reasons to merge
        # Format: [(primary_code, [similar_codes_to_merge])]
        similar_groups = [
            ('გამოცდილების_ნაკლებობა', ['არასაკმარისი_გამოცდილება']),
            ('უნარების_შეუსაბამობა', ['უნარების_ნაკლებობა']),
            ('ანაზღაურების_მოლოდინები', ['არარეალისტური_ხელფასის_მოლოდინი']),
        ]
        
        with transaction.atomic():
            for primary_code, similar_codes in similar_groups:
                try:
                    # Get the primary reason
                    primary_reason = RejectionReason.objects.get(code=primary_code)
                    
                    self.stdout.write(f'Primary reason: {primary_reason.code} - {primary_reason.name}')
                    
                    # Process each similar reason
                    for similar_code in similar_codes:
                        try:
                            similar_reason = RejectionReason.objects.get(code=similar_code)
                            
                            self.stdout.write(f'  Merging: {similar_reason.code} - {similar_reason.name}')
                            
                            # Get applications using this reason
                            applications = JobApplication.objects.filter(rejection_reasons=similar_reason)
                            
                            # Add the primary reason to these applications
                            for app in applications:
                                app.rejection_reasons.add(primary_reason)
                                app.rejection_reasons.remove(similar_reason)
                                self.stdout.write(f'    Updated application {app.id}')
                            
                            # Delete the similar reason
                            self.stdout.write(f'    Deleting reason ID {similar_reason.id}')
                            similar_reason.delete()
                            
                        except RejectionReason.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'  Similar reason not found: {similar_code}'))
                
                except RejectionReason.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Primary reason not found: {primary_code}'))
        
        self.stdout.write(self.style.SUCCESS('Merge complete')) 