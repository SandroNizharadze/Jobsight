#!/bin/bash

# Kill any existing server
pkill -f runserver || true

# Make sure we're using DEBUG mode for development
if grep -q "DEBUG=False" .env; then
  echo "Setting DEBUG=True in .env file for development..."
  sed -i '' 's/DEBUG=False/DEBUG=True/' .env
fi

# Make sure we're still using S3 for media but local for static
if grep -q "USE_S3=False" .env; then
  echo "Setting USE_S3=True in .env file for S3 media storage..."
  sed -i '' 's/USE_S3=False/USE_S3=True/' .env
fi

# Use S3 for media but serve static files locally
export USE_S3=True
export DEBUG=True
export USE_S3_FOR_STATIC=False

# Load other S3 vars
source $(dirname "$0")/s3_tools/export_s3_env.sh

# Get local IP address
LOCAL_IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)

echo "Starting Django development server with:"
echo "  - DEBUG mode: enabled (for CSS and static files)"
echo "  - S3 media storage: enabled (for uploads)"
echo "  - Static files: served locally (USE_S3_FOR_STATIC=False)"
echo "  - Server accessible at: http://$LOCAL_IP:8000"

# Start the server with the local IP binding to make it accessible from other devices
python manage.py runserver $LOCAL_IP:8000 