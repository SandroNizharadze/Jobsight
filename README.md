# [Jobsight.ge](https://jobsight.ge) - Job Listing Platform

Jobsight is a comprehensive job listing platform built with Django, designed to connect employers and job seekers in Georgia. The platform features a modern, responsive interface with multi-language support and specialized tools for both employers and job seekers.

> **Note:** The site is currently hosted on Render's free plan. When visiting for the first time, it may take 1-2 minutes to load as the application spins up from idle state.

## Features

- Job listing creation and management
- Employer profiles with company information
- Job seeker profiles with CV upload
- Premium job listings with enhanced visibility and user database access
- Search and filter jobs by various criteria
- Responsive design for mobile and desktop
- Multi-language support (English and Georgian)
- Many other tools and metrics for Employers.

## Technology Stack

### Backend
- **Django**: Python web framework for rapid development
- **PostgreSQL**: Primary database for data storage
- **Django REST Framework**: For API endpoints
- **AWS S3**: For storing and serving media files
- **Social Auth**: Integration with Google OAuth for authentication

### Frontend
- **Tailwind CSS**: For responsive and modern UI design
- **JavaScript**: For interactive elements and enhanced user experience
- **CKEditor 5**: Rich text editor for job descriptions
- **Responsive Design**: Mobile-first approach for all device compatibility

**Why not React/Angular?** I chose vanilla JavaScript with Django templates over modern frontend frameworks because:
- **SEO Optimization**: Server-side rendering ensures job listings are properly indexed by search engines
- **Performance**: Faster initial page loads without large JavaScript bundles
- **Simplicity**: Easier to maintain and debug with a smaller, focused tech stack (I'm not frontend dev)
- **Django Integration**: Seamless integration with Django's form handling and template system
- **Content-Focused**: Job platforms benefit from static HTML delivery rather than complex client-side interactions

### Deployment
- **Render**: Cloud hosting platform
- **Supabase**: PostgreSQL database hosting with connection pooling for production
- **WhiteNoise**: Static file serving
- **Boto3**: AWS S3 integration for media storage

## Project Structure

The application follows a modular architecture:

- **core/**: Main Django app containing all business logic
  - **models/**: Database models for jobs, employers, users, etc.
  - **views/**: View functions organized by feature area
  - **templates/**: HTML templates with Tailwind CSS styling
  - **services/**: Business logic layer for complex operations
  - **repositories/**: Data access layer for database operations

- **jobsy/**: Project configuration and settings
  - **settings.py**: Main settings file
  - **s3_settings.py**: AWS S3 configuration
  - **render_settings.py**: Production deployment settings

- **static/**: CSS, JavaScript, and image assets
  - **css/**: Tailwind-compiled CSS files
  - **js/**: JavaScript modules
  - **images/**: Static images and icons

## License

This project is proprietary and is not licensed for public use, modification, or distribution. The source code is available for viewing purposes only. See the LICENSE file for details.

