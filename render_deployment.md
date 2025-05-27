# Deploying to Render with Supabase

This guide explains how to deploy the Jobsy application to Render using Supabase as the database.

## Prerequisites

- A Supabase account with a project set up
- A Render account

## Environment Variables

Add the following environment variables to your Render Web Service:

```
USE_SUPABASE=True
SUPABASE_POOLER_CONNECTION_STRING=<your-supabase-connection-string>
```

> **Important**: 
> 1. Replace `<your-supabase-connection-string>` with your actual Supabase pooler connection string
> 2. The `@` symbol in passwords must be URL-encoded as `%40` to avoid connection issues

## Additional Environment Variables

Also add these environment variables that are already in your local .env file:

```
USE_S3=True
AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
AWS_STORAGE_BUCKET_NAME=<your-s3-bucket-name>
AWS_S3_REGION_NAME=<your-aws-region>
GOOGLE_OAUTH2_KEY=<your-google-oauth2-key>
GOOGLE_OAUTH2_SECRET=<your-google-oauth2-secret>
```

## Deployment Steps

1. Log in to your Render dashboard
2. Navigate to your Web Service for Jobsy
3. Go to the "Environment" tab
4. Add all the environment variables listed above
5. Click "Save Changes"
6. Trigger a manual deploy by clicking "Deploy" > "Deploy latest commit"

## Verifying the Deployment

After deployment, you can verify that your application is using Supabase by checking the logs. You should see messages indicating successful connection to the Supabase database.

## Troubleshooting

If you encounter database connection issues:

1. Check if the `USE_SUPABASE` environment variable is set to `True`
2. Verify that the `SUPABASE_POOLER_CONNECTION_STRING` is correctly formatted with the `@` symbol in the password URL-encoded as `%40`
3. Check if your Supabase project is active and accepting connections
4. Review the Render logs for any specific error messages 