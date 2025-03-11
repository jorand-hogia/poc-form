#!/bin/bash
set -e

# Show the environment for debugging
echo "Current user: $(id)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la
echo "App directory permissions:"
ls -la /app

# Create the instance directory if it doesn't exist
echo "Creating instance directory with proper permissions"
mkdir -p /app/instance 
chmod -R 777 /app/instance
ls -la /app/instance

# Explicitly set the database file path and permissions
touch /app/instance/submissions.db
chmod 666 /app/instance/submissions.db
echo "Database file permissions:"
ls -la /app/instance/submissions.db

# Set up the database
export FLASK_APP=app.py
echo "Running database migrations..."

# Skip db init if migrations directory already exists
if [ ! -d "migrations" ]; then
    echo "Initializing database..."
    python -m flask db init
else
    echo "Migrations directory already exists, skipping init"
fi

# Run migrations (with simple error handling)
echo "Attempting to run migrations..."
python -m flask db migrate || echo "Migration failed, but continuing"
python -m flask db upgrade || echo "Upgrade failed, but continuing"

# Create a minimal database schema if migrations failed
echo "Ensuring database schema exists..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created')
"

# Set environment variables for the application
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Start the application
echo "Starting application..."
exec gunicorn --bind 0.0.0.0:8080 app:app 