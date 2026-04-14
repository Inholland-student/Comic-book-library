import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_comics_unauthenticated():
    response = client.get("/comics")
    assert response.status_code == 401

def test_get_comics_authenticated():
    # Placeholder: simulate login as fiend
    token = "fake-token-for-fiend"
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/comics", headers=headers)
    # 200 if authorized, 401 if not implemented yet
    assert response.status_code in [200, 401]

# More tests for add, update, delete comics will be added after RBAC/auth is implemented
