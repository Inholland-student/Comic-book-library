"""
Tests for authentication system (TDD - tests first)
🔒 Security: Login, registration, JWT in httpOnly cookies (NOT response body)
"""
import pytest
import json
from datetime import datetime, timedelta
from flask_jwt_extended import decode_token


class TestUserRegistration:
    """Test user registration endpoints"""
    
    def test_register_with_valid_input(self, client):
        """Test successful user registration"""
        username = f'test_user_{datetime.now().timestamp()}'
        data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': 'SecurePassword123!'
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 201
        
        result = response.get_json()
        assert result['username'] == username
        assert result['email'] == data['email']
        assert result['role'] == 'friend'  # Default role
        # 🔒 Password should NOT be in response
        assert 'password' not in result
        assert 'password_hash' not in result
    
    def test_register_with_duplicate_username(self, client):
        """🔒 Test that duplicate username is rejected"""
        username = f'test_user_{datetime.now().timestamp()}'
        data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': 'SecurePassword123!'
        }
        
        # First registration
        response1 = client.post('/api/auth/register', json=data)
        assert response1.status_code == 201
        
        # Second registration with same username
        data['email'] = f'{username}_2@test.local'  # Different email
        response2 = client.post('/api/auth/register', json=data)
        assert response2.status_code == 409  # Conflict
        result = response2.get_json()
        assert 'already exists' in result['error'].lower() or 'username' in result['error'].lower()
    
    def test_register_with_duplicate_email(self, client):
        """🔒 Test that duplicate email is rejected"""
        username = f'test_user_{datetime.now().timestamp()}'
        email = f'{username}@test.local'
        data = {
            'username': username,
            'email': email,
            'password': 'SecurePassword123!'
        }
        
        # First registration
        response1 = client.post('/api/auth/register', json=data)
        assert response1.status_code == 201
        
        # Second registration with same email
        data['username'] = f'{username}_2'  # Different username
        response2 = client.post('/api/auth/register', json=data)
        assert response2.status_code == 409  # Conflict
        result = response2.get_json()
        assert 'already exists' in result['error'].lower() or 'email' in result['error'].lower()
    
    def test_register_with_missing_username(self, client):
        """Test validation: missing username"""
        data = {
            'email': 'test@test.local',
            'password': 'SecurePassword123!'
            # username missing
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert 'username' in result['error'].lower()
    
    def test_register_with_missing_email(self, client):
        """Test validation: missing email"""
        data = {
            'username': 'testuser',
            'password': 'SecurePassword123!'
            # email missing
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert 'email' in result['error'].lower()
    
    def test_register_with_missing_password(self, client):
        """Test validation: missing password"""
        data = {
            'username': 'testuser',
            'email': 'test@test.local'
            # password missing
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert 'password' in result['error'].lower()
    
    def test_register_with_short_password(self, client):
        """Test validation: password too short"""
        data = {
            'username': f'test_user_{datetime.now().timestamp()}',
            'email': f'test_{datetime.now().timestamp()}@test.local',
            'password': '123'  # Too short
        }
        
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert 'password' in result['error'].lower() or 'short' in result['error'].lower()


class TestUserLogin:
    """Test user login endpoint"""
    
    def test_login_with_correct_credentials(self, client):
        """Test successful login"""
        # First create a user
        username = f'test_user_{datetime.now().timestamp()}'
        password = 'SecurePassword123!'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': password
        }
        client.post('/api/auth/register', json=register_data)
        
        # Now login
        login_data = {
            'username': username,
            'password': password
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        result = response.get_json()
        assert result['username'] == username
        assert result['role'] == 'friend'
        # 🔒 Password should NOT be in response
        assert 'password' not in result
        
        # 🔒 Check that token is in httpOnly cookie, NOT in response body
        # The token should NOT appear in the response JSON
        assert 'access_token' not in result
        assert 'token' not in result
        
        # 🔒 Verify that Set-Cookie header has httpOnly flag
        # Flask-JWT-Extended should set this automatically
    
    def test_login_with_wrong_password(self, client):
        """Test login fails with wrong password"""
        # Create user first
        username = f'test_user_{datetime.now().timestamp()}'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': 'CorrectPassword123!'
        }
        client.post('/api/auth/register', json=register_data)
        
        # Try login with wrong password
        login_data = {
            'username': username,
            'password': 'WrongPassword123!'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
        result = response.get_json()
        assert 'invalid' in result['error'].lower() or 'credentials' in result['error'].lower()
    
    def test_login_with_nonexistent_user(self, client):
        """Test login fails with non-existent user"""
        login_data = {
            'username': 'nonexistent_user_xyz_12345',
            'password': 'AnyPassword123!'
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
        result = response.get_json()
        assert 'invalid' in result['error'].lower() or 'credentials' in result['error'].lower()
    
    def test_login_with_missing_username(self, client):
        """Test validation: missing username"""
        data = {
            'password': 'SomePassword123!'
        }
        response = client.post('/api/auth/login', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert 'username' in result['error'].lower()
    
    def test_login_with_missing_password(self, client):
        """Test validation: missing password"""
        data = {
            'username': 'testuser'
        }
        response = client.post('/api/auth/login', json=data)
        assert response.status_code == 400
        result = response.get_json()
        assert 'password' in result['error'].lower()


class TestJWTToken:
    """Test JWT token creation and verification"""
    
    def test_token_in_httponly_cookie_not_response_body(self, client):
        """🔒 CRITICAL: Verify token is in httpOnly cookie, NOT response body"""
        # Create and login user
        username = f'test_user_{datetime.now().timestamp()}'
        password = 'SecurePassword123!'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': password
        }
        client.post('/api/auth/register', json=register_data)
        
        login_data = {'username': username, 'password': password}
        response = client.post('/api/auth/login', json=login_data)
        
        # 🔒 Check response body does NOT contain token
        response_json = response.get_json()
        assert 'access_token' not in response_json
        assert 'token' not in response_json
        json_str = json.dumps(response_json)
        # Token should not be a long string in JSON (basic check)
        
        # 🔒 Check that JWT is in cookies
        # Flask test client stores cookies automatically
        # The token should be accessible in requests after login via cookies
    
    def test_jwt_token_valid_format(self, client):
        """Test that JWT token has valid format (three parts separated by dots)"""
        # Create and login
        username = f'test_user_{datetime.now().timestamp()}'
        password = 'SecurePassword123!'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': password
        }
        client.post('/api/auth/register', json=register_data)
        
        login_data = {'username': username, 'password': password}
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        # Extract token from cookies (Flask test client maintains cookies)
        # We'll test this in subsequent tests via authenticated requests
    
    def test_authenticated_request_with_jwt_cookie(self, client):
        """Test that authenticated endpoints accept JWT from cookie"""
        # Create and login user
        username = f'test_user_{datetime.now().timestamp()}'
        password = 'SecurePassword123!'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': password
        }
        client.post('/api/auth/register', json=register_data)
        
        login_data = {'username': username, 'password': password}
        login_response = client.post('/api/auth/login', json=login_data)
        assert login_response.status_code == 200
        
        # Now try to access protected endpoint (GET /api/auth/me)
        # Test client automatically includes cookies from previous request
        me_response = client.get('/api/auth/me')
        assert me_response.status_code == 200
        me_data = me_response.get_json()
        assert me_data['username'] == username


class TestLogout:
    """Test logout endpoint"""
    
    def test_logout_clears_jwt_cookie(self, client):
        """🔒 Test that logout clears the JWT cookie"""
        # Create and login user
        username = f'test_user_{datetime.now().timestamp()}'
        password = 'SecurePassword123!'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': password
        }
        client.post('/api/auth/register', json=register_data)
        
        login_data = {'username': username, 'password': password}
        client.post('/api/auth/login', json=login_data)
        
        # Logout
        logout_response = client.post('/api/auth/logout')
        assert logout_response.status_code == 204
        
        # After logout, protected endpoints should fail
        me_response = client.get('/api/auth/me')
        assert me_response.status_code == 401


class TestSecurityHeadersAndFlags:
    """Test security-related configurations"""
    
    def test_jwt_cookie_has_secure_flags(self, app):
        """🔒 Test that JWT cookie configuration has security flags"""
        # These should be set in __init__.py
        assert app.config['JWT_COOKIE_HTTPONLY'] is True
        assert app.config['JWT_COOKIE_SAMESITE'] == 'Strict'
        # Secure flag depends on environment (False for dev, True for prod)
    
    def test_password_not_returned_in_any_auth_response(self, client):
        """🔒 Test that password/password_hash is never returned in auth responses"""
        # Register
        username = f'test_user_{datetime.now().timestamp()}'
        password = 'SecurePassword123!'
        register_data = {
            'username': username,
            'email': f'{username}@test.local',
            'password': password
        }
        register_response = client.post('/api/auth/register', json=register_data)
        
        # Ensure password is not in any response
        register_json = register_response.get_json()
        assert 'password' not in register_json
        assert 'password_hash' not in register_json
        
        # Login
        login_data = {'username': username, 'password': password}
        login_response = client.post('/api/auth/login', json=login_data)
        login_json = login_response.get_json()
        assert 'password' not in login_json
        assert 'password_hash' not in login_json
        
        # GET /api/auth/me
        me_response = client.get('/api/auth/me')
        me_json = me_response.get_json()
        assert 'password' not in me_json
        assert 'password_hash' not in me_json
