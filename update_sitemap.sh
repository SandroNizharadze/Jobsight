#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Virtual environment not found, proceeding without activation"
fi

# Generate sitemap
echo "Generating sitemap..."
python3 manage.py generate_sitemap

# Check if the sitemap was generated successfully
if [ -f "static/sitemap.xml" ]; then
    echo "Sitemap generated successfully at static/sitemap.xml"
    
    # If using S3, upload the sitemap to S3
    if [ "$USE_S3" = "True" ]; then
        echo "Uploading sitemap to S3..."
        # Assuming AWS CLI is configured
        aws s3 cp static/sitemap.xml s3://$AWS_STORAGE_BUCKET_NAME/static/sitemap.xml --acl public-read
        echo "Sitemap uploaded to S3"
    else
        echo "Not using S3, sitemap is available locally"
    fi
    
    # Restart the server if needed
    # echo "Restarting server..."
    # pkill -f runserver
    # python3 manage.py runserver &
else
    echo "Error: Sitemap not generated"
    exit 1
fi

echo "Sitemap update process completed successfully" 