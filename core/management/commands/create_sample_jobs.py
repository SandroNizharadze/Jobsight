import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import EmployerProfile, JobListing, UserProfile

class Command(BaseCommand):
    help = 'Creates sample job listings with all required fields for development purposes'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of job listings to create')

    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create employer profiles
        employers = self._ensure_employers()
        
        # Create job listings
        created_count = 0
        for i in range(count):
            # Select a random employer
            employer = random.choice(employers)
            
            # Create job listing with all required fields
            job_listing = self._create_job_listing(employer, i)
            if job_listing:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Created job listing: {job_listing.title} at {job_listing.company} (ID: {job_listing.id})'
                ))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} sample job listings'))

    def _ensure_employers(self):
        """Ensure we have at least one employer profile"""
        employers = list(EmployerProfile.objects.all())
        
        if not employers:
            self.stdout.write(self.style.WARNING('No employer profiles found. Creating a sample employer.'))
            
            # Create a user for the employer
            employer_user, created = User.objects.get_or_create(
                username='employer@example.com',
                defaults={
                    'email': 'employer@example.com',
                    'first_name': 'Sample',
                    'last_name': 'Employer',
                }
            )
            
            if created:
                employer_user.set_password('password123')
                employer_user.save()
            
            # Create user profile
            user_profile, _ = UserProfile.objects.get_or_create(
                user=employer_user,
                defaults={'role': 'employer'}
            )
            user_profile.role = 'employer'
            user_profile.save()
            
            # Create employer profile
            employer_profile, created = EmployerProfile.objects.get_or_create(
                user_profile=user_profile,
                defaults={
                    'company_name': 'Sample Company',
                    'company_website': 'https://example.com',
                    'company_description': 'This is a sample company for development testing.',
                    'industry': 'IT და პროგრამული უზრუნველყოფა',
                    'company_size': '10-50',
                    'location': 'თბილისი',
                    'has_cv_database_access': True,
                    'show_phone_number': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created employer profile: {employer_profile.company_name}'))
            
            employers.append(employer_profile)
        
        return employers

    def _create_job_listing(self, employer, index):
        """Create a job listing with all required fields"""
        # Sample data
        titles = [
            'Python დეველოპერი',
            'React ფრონტენდ სპეციალისტი',
            'UI/UX დიზაინერი',
            'მარკეტინგის მენეჯერი',
            'დეიტა ანალიტიკოსი',
            'დეიტა სციენსისტი',
            'DevOps ინჟინერი',
            'პროდუქტის მენეჯერი',
            'მობაილ დეველოპერი',
            'QA ტესტერი',
        ]
        
        descriptions = [
            """<h3>პოზიციის აღწერა:</h3>
<p>ჩვენ ვეძებთ გამოცდილ Python დეველოპერს, რომელიც იმუშავებს ჩვენს გუნდთან ერთად ახალი პროდუქტების შექმნაზე.</p>
<h3>მოთხოვნები:</h3>
<ul>
<li>გამოცდილება Python-ში 2+ წელი</li>
<li>Django ან Flask ფრეიმვორკების ცოდნა</li>
<li>მონაცემთა ბაზებთან მუშაობის გამოცდილება (PostgreSQL, MySQL)</li>
<li>REST API-ების შექმნის გამოცდილება</li>
</ul>""",

            """<h3>პოზიციის აღწერა:</h3>
<p>ჩვენი გუნდი ეძებს React დეველოპერს, რომელსაც აქვს მოდერნული ფრონტენდ ტექნოლოგიების ცოდნა.</p>
<h3>მოთხოვნები:</h3>
<ul>
<li>გამოცდილება React.js-ში 2+ წელი</li>
<li>JavaScript-ის და TypeScript-ის კარგი ცოდნა</li>
<li>HTML/CSS-ის კარგი ცოდნა</li>
<li>Redux-ის გამოცდილება</li>
</ul>""",

            """<h3>პოზიციის აღწერა:</h3>
<p>ჩვენ გვესაჭიროება კრეატიული UI/UX დიზაინერი, რომელსაც შეუძლია შექმნას მომხმარებელზე ორიენტირებული ინტერფეისები.</p>
<h3>მოთხოვნები:</h3>
<ul>
<li>გამოცდილება UI/UX დიზაინში 3+ წელი</li>
<li>Figma, Sketch ან Adobe XD-ის ცოდნა</li>
<li>მომხმარებლის გამოცდილების კვლევის უნარები</li>
<li>დიზაინ სისტემებთან მუშაობის გამოცდილება</li>
</ul>""",
        ]
        
        categories = [c[0] for c in JobListing.CATEGORY_CHOICES]
        locations = [l[0] for l in JobListing.LOCATION_CHOICES]
        experiences = [e[0] for e in JobListing.EXPERIENCE_CHOICES]
        job_preferences = [jp[0] for jp in JobListing.JOB_PREFERENCE_CHOICES]
        premium_levels = [pl[0] for pl in JobListing.PREMIUM_LEVEL_CHOICES]
        
        # Create job listing
        try:
            # Ensure index doesn't go out of bounds
            title_index = index % len(titles)
            desc_index = index % len(descriptions)
            
            # Set expiration date (30 days from now)
            expires_at = timezone.now() + timedelta(days=30)
            
            job_listing = JobListing.objects.create(
                title=titles[title_index],
                company=employer.company_name,
                description=descriptions[desc_index],
                salary_min=random.randint(1000, 3000),
                salary_max=random.randint(3000, 6000),
                salary_type='თვეში',
                category=random.choice(categories),
                location=random.choice(locations),
                employer=employer,
                expires_at=expires_at,
                experience=random.choice(experiences),
                job_preferences=random.choice(job_preferences),
                considers_students=random.choice([True, False]),
                status='approved',
                premium_level=random.choice(premium_levels),
                georgian_language_only=random.choice([True, False]),
                view_count=random.randint(0, 100)
            )
            
            return job_listing
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating job listing: {str(e)}'))
            return None 