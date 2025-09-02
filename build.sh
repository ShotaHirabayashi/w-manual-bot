#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Pre-download models to avoid timeout during runtime
echo "Pre-downloading AI models..."
python << EOF
import os
os.environ['USE_LITE_AI_SERVICE'] = 'true'  # Force lite mode during build
print("Skipping heavy model downloads - using lite mode")
EOF

# Collect static files
python manage.py collectstatic --no-input

echo "Build completed successfully!"
echo ""
echo "================================================================"
echo "IMPORTANT: Database migrations need to be run manually"
echo "After deployment, run the following in Render Shell:"
echo "./migrate_manual.sh"
echo "================================================================"