# POC Container

A simple containerized Flask application that provides a web form for data submission and an API to retrieve the stored data. This container is designed to be connected to the [POC Portal](https://github.com/jorand-hogia/poc-portal).

## Features

- Web form with subject and context fields
- API endpoint for retrieving all submissions
- API endpoint for creating submissions programmatically
- OpenAPI documentation with Swagger UI
- Containerized for easy deployment
- Compatible with Python 3.13 and above

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Container

1. Clone this repository:
   ```bash
   git clone <this-repository-url>
   cd poc-container
   ```

2. Build and start the container:
   ```bash
   docker-compose up -d
   ```

3. The web form will be available at `http://localhost:8080`
4. The API documentation will be available at `http://localhost:8080/api/docs`

## API Endpoints

All API endpoints are documented with OpenAPI and available through the Swagger UI at `/api/docs`.

### Get All Submissions

```
GET /api/submissions
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "subject": "Example Subject",
      "context": "Example Context",
      "created_at": "2023-01-01T12:00:00"
    },
    ...
  ]
}
```

### Create a New Submission

```
POST /api/submissions
```

Request body:
```json
{
  "subject": "New Subject",
  "context": "New Context"
}
```

Response:
```json
{
  "success": true,
  "message": "Submission created successfully",
  "data": {
    "id": 2,
    "subject": "New Subject",
    "context": "New Context",
    "created_at": "2023-01-01T12:30:00"
  }
}
```

### Get a Specific Submission

```
GET /api/submissions/{id}
```

Response:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "subject": "Example Subject",
    "context": "Example Context",
    "created_at": "2023-01-01T12:00:00"
  }
}
```

### Delete a Submission

```
DELETE /api/submissions/{id}
```

Response:
```
204 No Content
```

## Connecting to POC Portal

To connect this container to the POC Portal:

1. First, make sure the poc-portal is running:
   ```bash
   git clone https://github.com/jorand-hogia/poc-portal.git
   cd poc-portal
   docker-compose up -d
   ```

2. Then, start this form service container:
   ```bash
   cd poc-container
   docker-compose up -d
   ```

3. The docker-compose file is pre-configured to connect to the poc-portal network.

4. In the POC Portal settings page (http://localhost:5000/settings), configure a connection to this service with:
   - Name: Form Service
   - URL: `http://form-service:8080/api/submissions`

5. Test the connection in the portal settings page, then navigate to the dashboard to view the submissions.

## Local Development

If you're not using Docker, you can run the application locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install python-dotenv
   ```

2. Initialize the database:
   ```bash
   python -m flask db init
   python -m flask db migrate -m "Initial migration" 
   python -m flask db upgrade
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## License

[MIT License](LICENSE) 