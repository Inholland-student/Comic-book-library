import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure /app is in sys.path for Docker
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from main import app

@pytest.fixture
def client():
    return TestClient(app)
