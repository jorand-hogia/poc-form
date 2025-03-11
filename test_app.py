import pytest
import os
import json
import shutil
from app import create_app
from app.models import Submission

@pytest.fixture
def app():
    # Create test storage directory
    test_storage_dir = "instance_test"
    os.makedirs(test_storage_dir, exist_ok=True)
    
    # Create test app with configuration
    app = create_app({
        'TESTING': True,
        'STORAGE_DIR': test_storage_dir
    })
    
    # Create empty submissions file for testing
    test_submissions_file = os.path.join(test_storage_dir, "submissions.json")
    with open(test_submissions_file, 'w') as f:
        json.dump([], f)
    
    with app.app_context():
        yield app
        
        # Clean up test storage
        shutil.rmtree(test_storage_dir, ignore_errors=True)

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