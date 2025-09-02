#!/usr/bin/env bash
# Manual migration script for Render PostgreSQL
# Run this in Render Shell after deployment

echo "================================================"
echo "PostgreSQL Database Setup for Render"
echo "================================================"

# Check DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL is not set!"
    echo "Please ensure your database is properly configured in Render."
    exit 1
fi

echo "DATABASE_URL is configured ✓"

# Run the Python initialization script
python init_db.py

echo ""
echo "================================================"
echo "Setup completed!"
echo "You can now access:"
echo "  - Your app at: https://w-manual-bot.onrender.com"
echo "  - Admin panel at: https://w-manual-bot.onrender.com/admin"
echo "================================================"