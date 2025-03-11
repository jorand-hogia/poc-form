FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir Werkzeug==2.3.7
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv

COPY . .

# Create database directory with proper permissions
RUN mkdir -p instance
RUN chmod 777 instance

# We'll initialize the database at runtime now, not build time
# This ensures the database file has proper permissions

EXPOSE 8080

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Create entrypoint script to initialize database before starting the app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 