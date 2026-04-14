"""
Pytest configuration and fixtures for Comic Library tests
"""
import pytest
from app import create_app
import os

@pytest.fixture
def app():
    """Create Flask app for testing"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app('testing')
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create Flask CLI runner"""
    return app.test_cli_runner()
