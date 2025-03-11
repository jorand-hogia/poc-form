#!/usr/bin/env python
"""
Database initialization script.
Run this script to create and initialize the database.
"""
import os
from app import create_app, db

# Create the app with the factory pattern
app = create_app()

with app.app_context():
    # Create the instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("Created instance directory")
    
    # Initialize the database
    db.create_all()
    print("Database tables created")
    
    # Print database info
    print(f"Database file: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    print("Database initialization complete") 