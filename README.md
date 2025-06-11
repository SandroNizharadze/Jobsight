# Jobsight - Job Listing Platform

Jobsight is a comprehensive job listing platform built with Django.

## Environment Variables and Security

To run this application securely, you need to set up the following environment variables. Create a `.env` file in the project root with these variables:

```
# Django Settings
DEBUG=True
DJANGO_SECRET_KEY=your-secure-secret-key-here

# Database Settings
DB_NAME=jobsy_db
DB_USER=admin
DB_PASSWORD=your-secure-db-password
DB_HOST=localhost
DB_PORT=5432

# Supabase Settings (Render deployment)
USE_SUPABASE=False
SUPABASE_POOLER_CONNECTION_STRING=postgres://username:password@host:port/database

# S3 Configuration
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Google OAuth2 Settings
GOOGLE_OAUTH2_KEY=your-google-client-id
GOOGLE_OAUTH2_SECRET=your-google-client-secret

# Admin Creation Settings
ADMIN_CREATION_KEY=your-secure-admin-creation-key

# Demo Data Settings (Optional)
DEMO_ADMIN_EMAIL=admin@example.com
DEMO_ADMIN_PASSWORD=secure-admin-password
DEMO_EMPLOYER_PASSWORD=secure-employer-password
```

### Security Best Practices

1. Never commit your `.env` file or any file containing secrets to version control
2. Generate a strong, random Django secret key
3. Use environment-specific settings files that load variables from the environment
4. Set restrictive permissions on files containing secrets
5. Rotate your secrets regularly
6. Use a secret management service in production environments

## Features

- Job listing creation and management
- Employer profiles with company information
- Job seeker profiles with CV upload
- Premium job listings with enhanced visibility
- Search and filter jobs by various criteria
- Responsive design for mobile and desktop
- Multi-language support (English and Georgian)

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables as described above
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the server: `python manage.py runserver`

## Deployment

For deployment to Render with Supabase, refer to the [render_deployment.md](render_deployment.md) document. 