#!/usr/bin/env python
"""
Database initialization script for Render deployment
Run this after the database is ready
"""

import os
import sys
import django
import time
from urllib.parse import urlparse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def wait_for_db():
    """Wait for database to be ready"""
    import psycopg2
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL not set!")
        return False
    
    result = urlparse(database_url)
    max_retries = 30
    retry_count = 0
    
    print("Waiting for database connection...")
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host=result.hostname,
                port=result.port
            )
            conn.close()
            print("✓ Database is ready!")
            return True
        except Exception as e:
            retry_count += 1
            print(f"  Waiting... ({retry_count}/{max_retries})")
            time.sleep(2)
    
    print("✗ Database connection timeout")
    return False

def run_migrations():
    """Run database migrations"""
    from django.core.management import execute_from_command_line
    
    print("\nRunning database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--no-input'])
        print("✓ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

def create_superuser():
    """Create superuser if it doesn't exist"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    email = os.environ.get('SUPERUSER_EMAIL')
    name = os.environ.get('SUPERUSER_NAME')
    password = os.environ.get('SUPERUSER_PASSWORD')
    
    if not all([email, name, password]):
        print("\n⚠ Superuser credentials not found in environment variables")
        print("  Set SUPERUSER_EMAIL, SUPERUSER_NAME, and SUPERUSER_PASSWORD")
        return False
    
    try:
        if User.objects.filter(email=email).exists():
            print(f"\n✓ Superuser already exists: {email}")
        else:
            User.objects.create_superuser(email=email, name=name, password=password)
            print(f"\n✓ Superuser created: {email}")
        return True
    except Exception as e:
        print(f"\n✗ Failed to create superuser: {e}")
        return False

def main():
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    # Wait for database
    if not wait_for_db():
        print("\n✗ Database initialization failed")
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("\n✗ Migration failed")
        sys.exit(1)
    
    # Create superuser
    create_superuser()
    
    print("\n" + "=" * 60)
    print("✓ Database initialization completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()