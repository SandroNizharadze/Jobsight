#!/bin/bash

# Use Vercel's Python
export PATH="/opt/vercel/python3/bin:$PATH"

# Install wheel package
python -m pip install wheel

# Install dependencies from Vercel-specific requirements file
python -m pip install -r requirements-vercel.txt

# Collect static files
python manage.py collectstatic --noinput
