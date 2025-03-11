FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir Werkzeug==2.3.7
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install python-dotenv

COPY . .

# Create database directory
RUN mkdir -p instance

# Initialize database
RUN flask db init || true
RUN flask db migrate -m "Initial migration" || true
RUN flask db upgrade || true

EXPOSE 8080

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"] 