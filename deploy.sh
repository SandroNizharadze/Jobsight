#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Explicitly install gunicorn and verify it's installed
pip install gunicorn
which gunicorn || echo "Gunicorn not found in PATH"

# Collect static files
python manage.py collectstatic --noinput

# Try to apply migrations
python manage.py migrate

# If migrations fail, try to merge them
if [ $? -ne 0 ]; then
    echo "Migrations failed, attempting to merge..."
    python manage.py makemigrations --merge --noinput
    python manage.py migrate
fi

# Start the application with gunicorn
exec gunicorn jobsy.wsgi:application 