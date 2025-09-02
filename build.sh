#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

echo "Build completed successfully!"
echo ""
echo "================================================================"
echo "IMPORTANT: Database migrations need to be run manually"
echo "After deployment, run the following in Render Shell:"
echo "./migrate_manual.sh"
echo "================================================================"