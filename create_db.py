#!/usr/bin/env python
"""
Very simple script to create a basic SQLite database file.
This is useful when you encounter permission issues with SQLAlchemy.
"""
import os
import sqlite3

# Ensure instance directory exists
instance_dir = "instance"
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)
    print(f"Created directory: {instance_dir}")

# Create the database file
db_path = os.path.join(instance_dir, "submissions.db")
print(f"Creating database at: {db_path}")

# Connect to SQLite (this will create the file if it doesn't exist)
conn = sqlite3.connect(db_path)

# Create a basic table for testing
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    context TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Commit and close
conn.commit()
conn.close()

# Set permissions
try:
    os.chmod(db_path, 0o666)  # Read/write for everyone
    print(f"Set permissions on database file: {db_path}")
except Exception as e:
    print(f"Warning: Could not set permissions: {e}")

print(f"Database file created successfully at: {db_path}")
print("You can now run the application with: python app.py") 