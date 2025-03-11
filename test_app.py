import pytest
from app import create_app
from app.models import Submission
from app import db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    """Test that the index page loads properly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Submit Information' in response.data

def test_health_check(client):
    """Test that the health check endpoint works"""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'

def test_api_docs(client):
    """Test that the API docs endpoint loads"""
    response = client.get('/api/docs')
    assert response.status_code == 200
    assert b'Swagger' in response.data

def test_api_get_submissions(client):
    """Test that the GET submissions API endpoint works"""
    response = client.get('/api/submissions')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'success' in json_data
    assert 'data' in json_data 