#!/bin/bash

# Install Python packages from requirements-minimal.txt
pip install -r requirements-minimal.txt

# Collect static files
python manage.py collectstatic --noinput
