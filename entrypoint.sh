#!/bin/bash
set -e

# Display environment for debugging
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la
echo "Instance directory contents:"
ls -la instance || echo "Instance directory not found"

# Ensure instance directory exists with proper permissions
mkdir -p /app/instance
chmod 777 /app/instance
chown -R nobody:nogroup /app/instance

# Initialize the database
export FLASK_APP=app.py
echo "Initializing database..."
python -m flask db init || echo "DB already initialized"
python -m flask db migrate || echo "No migrations to run"
python -m flask db upgrade
echo "Database initialization complete"

# Set environment variables
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Start the application with gunicorn
echo "Starting application..."
exec gunicorn --bind 0.0.0.0:8080 app:app 