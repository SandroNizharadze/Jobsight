#!/bin/bash

# Add Vercel's Python to the PATH
export PATH="/vercel/.local/bin:/vercel/path0/node_modules/.bin:$PATH"

# Use Python from Vercel's environment
if [ -f "/vercel/path0/.vercel/python/bin/python" ]; then
    PYTHON_PATH="/vercel/path0/.vercel/python/bin/python"
elif [ -f "/opt/vercel/python3/bin/python" ]; then
    PYTHON_PATH="/opt/vercel/python3/bin/python"
else
    PYTHON_PATH="python3"
fi

# Install Python packages from requirements-minimal.txt
$PYTHON_PATH -m pip install -r requirements-minimal.txt

# Collect static files
$PYTHON_PATH manage.py collectstatic --noinput
