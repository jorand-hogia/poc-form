#!/usr/bin/env python
"""
Local database initialization script.
Use this to initialize the SQLite database for local development.
"""
import os
import shutil
from app import create_app, db

print("Initializing local database...")

# Create the app with the factory pattern
app = create_app()

with app.app_context():
    # Create the instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("Created instance directory")
    
    # Ensure instance directory has the right permissions
    try:
        os.chmod('instance', 0o777)
        print("Set instance directory permissions")
    except Exception as e:
        print(f"Warning: Could not set permissions on instance directory: {e}")
    
    # Database path from config
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"Database path: {db_path}")
        
        # Create parent directories if needed
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created directory: {db_dir}")
    
    # Initialize the database
    db.create_all()
    print("Database tables created")
    
    # Print database info
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Try to run migrations if they exist
    if os.path.exists('migrations'):
        try:
            from flask_migrate import upgrade
            upgrade()
            print("Applied database migrations")
        except Exception as e:
            print(f"Warning: Could not apply migrations: {e}")
    
    print("Database initialization complete")
    print("\nYou can now run the application with: python app.py") 