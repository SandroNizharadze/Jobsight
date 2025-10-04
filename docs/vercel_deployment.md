# Deploying to Vercel

This document provides instructions for deploying the Jobsight application to Vercel.

## Prerequisites

1. A Vercel account
2. The Vercel CLI installed (`npm install -g vercel`)
3. A PostgreSQL database (Vercel doesn't provide PostgreSQL, so you'll need to use an external service like Supabase, Neon, or Railway)

## Configuration Files

The following files have been added/modified to support Vercel deployment:

- `vercel.json`: Configuration for Vercel deployment
- `requirements-vercel.txt`: Dependencies with pre-built wheels for Vercel
- `runtime.txt`: Specifies Python version
- `package.json`: Defines build commands
- `vercel-build.sh`: Script for building the application
- `jobsy/vercel.app.py`: Entry point for Vercel
- `jobsy/vercel_settings.py`: Vercel-specific Django settings

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

### Python Environment Issues

If you encounter issues with Python commands not being found:

1. Make sure the `vercel-build.sh` script is executable (`chmod +x vercel-build.sh`)
2. Try using the full path to Python: `/opt/vercel/python3/bin/python`
3. Check that the Vercel Python runtime is specified correctly in `vercel.json`

### psycopg2-binary Installation Issues

If you encounter issues with psycopg2-binary installation, the `requirements-vercel.txt` file includes a reference to pre-built wheels. If issues persist, try:

1. Using a different PostgreSQL adapter like `dj-database-url` with SQLite for testing
2. Using a different PostgreSQL client library like `pg8000` or `psycopg2cffi`

### Static Files Issues

If static files aren't being served correctly:

1. Make sure `whitenoise` is configured properly in settings.py
2. Check that `collectstatic` is running during the build process
3. Verify that the static files routes in `vercel.json` are correct

### Database Connection Issues

If the application can't connect to the database:

1. Double-check the `DATABASE_URL` environment variable in Vercel project settings
2. Make sure the database is accessible from Vercel's servers
3. Try using a different PostgreSQL client library
