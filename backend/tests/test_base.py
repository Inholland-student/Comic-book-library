"""
Test basic Flask app setup
"""
import pytest

def test_app_creation(app):
    """Test that Flask app creates successfully"""
    assert app is not None
    # The app should be in testing mode (set by conftest.py fixture)
    # Though FLASK_ENV env var might be 'development', the app config is from TestingConfig
    assert app.config['TESTING'] is True

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
