from app import create_app
from datetime import datetime

app = create_app('testing')
client = app.test_client()

# Register
username = f'test_user_{datetime.now().timestamp()}'
register_data = {
    'username': username,
    'email': f'{username}@test.local',
    'password': 'SecurePassword123!'
}
resp = client.post('/api/auth/register', json=register_data)
print(f"Register: {resp.status_code}")

# Login
login_data = {
    'username': username,
    'password': 'SecurePassword123!'
}
resp = client.post('/api/auth/login', json=login_data)
print(f"Login: {resp.status_code}")

# GET /me (test cookie)
resp = client.get('/api/auth/me')
print(f"GET /me: {resp.status_code}")

# Logout
resp = client.post('/api/auth/logout')
print(f"Logout: {resp.status_code}")
if resp.status_code != 204:
    print(f"Logout response: {resp.get_json()}")


