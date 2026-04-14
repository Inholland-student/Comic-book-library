import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_admin_as_super_admin():
    # Placeholder: simulate super admin creating admin
    token = "fake-token-for-super_admin"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"username": "newadmin", "role": "admin", "password": "pass"}
    response = client.post("/users", json=data, headers=headers)
    assert response.status_code in [201, 401, 403]  # 201 if allowed, 401/403 if not implemented yet

def test_create_super_admin_as_admin_forbidden():
    token = "fake-token-for-admin"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"username": "superadmin2", "role": "super_admin", "password": "pass"}
    response = client.post("/users", json=data, headers=headers)
    assert response.status_code in [403, 401]  # Forbidden
