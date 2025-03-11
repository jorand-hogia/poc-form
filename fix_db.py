#!/usr/bin/env python
"""
Database repair script.
This script will completely recreate the SQLite database from scratch,
ensuring proper paths, permissions, and schema creation.
"""
import os
import shutil
import sqlite3
from app import create_app, db

print("\n=== SQLITE DATABASE REPAIR TOOL ===")

# Create application context
app = create_app()

with app.app_context():
    # Get database path from config
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URI: {db_uri}")
    
    if not db_uri.startswith('sqlite:///'):
        print(f"Error: This is only for SQLite databases. Current URI: {db_uri}")
        exit(1)
    
    # Extract path from URI
    db_path = db_uri.replace('sqlite:////', '').replace('sqlite:///', '')
    print(f"Database path: {db_path}")
    
    # Ensure parent directories exist
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}")
        
        # Set directory permissions
        try:
            os.chmod(db_dir, 0o777)
            print(f"Set full permissions on: {db_dir}")
        except Exception as e:
            print(f"Warning: Could not set permissions on directory: {e}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        try:
            print(f"Removing existing database: {db_path}")
            os.remove(db_path)
        except Exception as e:
            print(f"Warning: Could not remove existing database: {e}")
    
    # Create fresh database file
    try:
        # Create empty file
        with open(db_path, 'w') as f:
            pass
        
        # Set full permissions
        os.chmod(db_path, 0o666)
        print(f"Created empty database file with permissions: {db_path}")
        
        # Test basic SQLite connection
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO test VALUES (1)")
        test_result = conn.execute("SELECT * FROM test").fetchone()
        conn.close()
        
        if test_result and test_result[0] == 1:
            print("Basic SQLite connection test: SUCCESSFUL")
        else:
            print("Basic SQLite connection test: FAILED - unexpected result")
    except Exception as e:
        print(f"Error creating/testing SQLite database: {e}")
        exit(1)
    
    # Create schema using SQLAlchemy
    try:
        db.create_all()
        print("Created database schema with SQLAlchemy")
        
        # Verify tables
        from app.models import Submission
        try:
            # Try to add and query a test record
            test_submission = Submission(subject="Test", context="Database repair test")
            db.session.add(test_submission)
            db.session.commit()
            
            # Query it back
            test_result = Submission.query.filter_by(subject="Test").first()
            if test_result and test_result.subject == "Test":
                print("SQLAlchemy write/read test: SUCCESSFUL")
                
                # Clean up test data
                db.session.delete(test_result)
                db.session.commit()
            else:
                print("SQLAlchemy write/read test: FAILED - couldn't retrieve test record")
        except Exception as e:
            db.session.rollback()
            print(f"SQLAlchemy write/read test FAILED: {e}")
    except Exception as e:
        print(f"Error creating schema with SQLAlchemy: {e}")
        exit(1)
    
    print("\n=== DATABASE REPAIR COMPLETED SUCCESSFULLY ===")
    print(f"Your database is now ready at: {db_path}")
    print("You can now run the application with: python app.py") 