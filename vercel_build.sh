#!/bin/bash

# Install Python packages from requirements-vercel-prod.txt
pip install -r requirements-vercel-prod.txt

# Collect static files
python manage.py collectstatic --noinput
