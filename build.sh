#!/bin/bash
# Install wheel package
pip install wheel

# Install dependencies from Vercel-specific requirements file
pip install -r requirements-vercel.txt

# Collect static files
python manage.py collectstatic --noinput
