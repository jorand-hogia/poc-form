#!/bin/bash
set -e

# Initialize the database
echo "Initializing database..."
python -m flask db init || true
python -m flask db migrate -m "Initial migration" || true
python -m flask db upgrade || true

# Start the application
echo "Starting application..."
exec gunicorn --bind 0.0.0.0:8080 wsgi:app 