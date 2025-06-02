#!/bin/bash

# Script to fix S3 paths and configure AWS credentials for Jobsy CV database

echo "Jobsy S3 Configuration Helper"
echo "============================"
echo

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Backup .env file
cp .env .env.backup
echo "Created backup of .env file at .env.backup"

# Enable S3 in .env
sed -i '' 's/USE_S3=False/USE_S3=True/g' .env
echo "Enabled S3 in .env file (USE_S3=True)"

# Check if AWS credentials are already in .env
if grep -q "AWS_ACCESS_KEY_ID" .env; then
    echo "AWS credentials already exist in .env file"
else
    # Prompt for AWS credentials
    echo
    echo "Please enter your AWS credentials:"
    read -p "AWS Access Key ID: " aws_access_key
    read -p "AWS Secret Access Key: " aws_secret_key
    read -p "AWS S3 Bucket Name [jobsy-media-files]: " aws_bucket
    read -p "AWS Region [us-east-1]: " aws_region
    
    # Set defaults if empty
    aws_bucket=${aws_bucket:-jobsy-media-files}
    aws_region=${aws_region:-us-east-1}
    
    # Add AWS credentials to .env
    echo "" >> .env
    echo "# AWS S3 Configuration" >> .env
    echo "AWS_ACCESS_KEY_ID=$aws_access_key" >> .env
    echo "AWS_SECRET_ACCESS_KEY=$aws_secret_key" >> .env
    echo "AWS_STORAGE_BUCKET_NAME=$aws_bucket" >> .env
    echo "AWS_S3_REGION_NAME=$aws_region" >> .env
    
    echo "Added AWS credentials to .env file"
fi

echo
echo "Running Django management commands to fix CV paths..."

# Run fix_cv_paths command
python3 manage.py fix_cv_paths
echo

# Check if S3 configuration is working
echo "Checking S3 configuration..."
python3 manage.py check_env
echo

echo "Done! Your S3 configuration should now be working."
echo
echo "If you still have issues, please check:"
echo "1. AWS credentials are correct"
echo "2. S3 bucket exists and is accessible"
echo "3. Django logs for detailed error messages"
echo
echo "To migrate existing local CV files to S3, run:"
echo "python3 manage.py migrate_media_to_s3"
