# Deploying to Vercel

This document provides instructions for deploying the Jobsight application to Vercel.

## Prerequisites

1. A Vercel account
2. The Vercel CLI installed (`npm install -g vercel`)
3. A PostgreSQL database (Vercel doesn't provide PostgreSQL, so you'll need to use an external service like Supabase, Neon, or Railway)

## Configuration Files

The following files have been added/modified to support Vercel deployment:

- `vercel.json`: Configuration for Vercel deployment
- `requirements-minimal.txt`: Minimal dependencies for Vercel deployment
- `runtime.txt`: Specifies Python version (3.12)
- `package.json`: Defines build commands
- `vercel_build.sh`: Script for building the application
- `jobsy/vercel.app.py`: Entry point for Vercel
- `jobsy/vercel_settings.py`: Vercel-specific Django settings
- `.vercelignore`: Excludes unnecessary files from deployment

## Key Changes

1. Using `pg8000` instead of `psycopg2-binary` to avoid compilation issues
2. Using Python 3.12 (Vercel's default) for compatibility
3. Custom settings file for Vercel deployment
4. Simplified build process
5. Proper Vercel configuration without invalid framework settings
6. Removed pyproject.toml to avoid package discovery issues
7. Added static build configuration for static files

## Environment Variables

Set the following environment variables in your Vercel project settings:

- `DATABASE_URL`: Your PostgreSQL database URL
- `DJANGO_SECRET_KEY`: A secure secret key for Django
- `DEBUG`: Set to 'False' for production
- Other environment variables as needed (email settings, S3 settings, etc.)

## Deployment Steps

1. Log in to Vercel:
   ```
   vercel login
   ```

2. Deploy the application:
   ```
   vercel
   ```

3. For production deployment:
   ```
   vercel --prod
   ```

## Troubleshooting

### Configuration Issues

If you encounter configuration errors:

1. Make sure the `vercel.json` file doesn't contain any invalid fields (like unsupported framework names)
2. Check that the Vercel Python runtime is specified correctly in `vercel.json`
3. Verify that `runtime.txt` is properly formatted
4. If you encounter package discovery issues, ensure that no `pyproject.toml` file exists in your project

### Python Environment Issues

If you encounter issues with Python commands not being found:

1. Make sure the `vercel_build.sh` script is executable (`chmod +x vercel_build.sh`)
2. Try using explicit paths to Python executables in build scripts

### Database Connection Issues

If the application can't connect to the database:

1. Double-check the `DATABASE_URL` environment variable in Vercel project settings
2. Make sure the database is accessible from Vercel's servers
3. Check the database adapter configuration in `vercel_settings.py`

### Static Files Issues

If static files aren't being served correctly:

1. Make sure `whitenoise` is configured properly in settings.py
2. Check that `collectstatic` is running during the build process
3. Verify that the static files routes in `vercel.json` are correct

### Deployment Size Issues

If your deployment is too large:

1. Use the `.vercelignore` file to exclude unnecessary files
2. Remove unused dependencies from `requirements-vercel-prod.txt`
3. Consider using a CDN for static files
