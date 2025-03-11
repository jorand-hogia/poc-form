#!/bin/bash
set -e

# Show the environment for debugging
echo "Current user: $(id)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la
echo "App directory permissions:"
ls -la /app

# Create the instance directory for file storage
echo "Creating storage directory with proper permissions"
mkdir -p /app/instance 
chmod -R 777 /app/instance
ls -la /app/instance

# Create submissions file if it doesn't exist
touch /app/instance/submissions.json
chmod 666 /app/instance/submissions.json
echo "Storage file permissions:"
ls -la /app/instance/submissions.json

# Set environment variables for the application
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Start the application
echo "Starting application..."
exec gunicorn --bind 0.0.0.0:8080 wsgi:app 