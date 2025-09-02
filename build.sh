#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations if DATABASE_URL is set and accessible
if [ -n "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    python manage.py migrate --no-input || echo "Migration skipped (database may not be ready yet)"
else
    echo "DATABASE_URL not set, skipping migrations"
fi