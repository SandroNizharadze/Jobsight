#!/bin/bash

# Script to update translations in production environment

# Set environment variables if needed
# export DJANGO_SETTINGS_MODULE=jobsy.settings

# Navigate to project directory
cd "$(dirname "$0")"

echo "Starting translation update process..."

# Run the Django management command
python3 manage.py update_production_translations

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Translation update completed successfully."
    exit 0
else
    echo "Error: Translation update failed."
    exit 1
fi
