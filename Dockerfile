FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory with proper permissions
RUN mkdir -p /app/instance && chmod 777 /app/instance

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose the port
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 