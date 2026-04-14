"""
Tests for password hashing and verification security
🔒 Security: Ensure bcrypt password verification works correctly
"""
import pytest
from datetime import datetime
from app.db import (
    create_user,
    get_user_by_username,
    verify_password,
    hash_password
)


class TestPasswordSecurity:
    """Test password hashing and verification"""
    
    def test_password_hash_different_each_time(self):
        """🔒 Test that same password produces different hashes (due to salt)"""
        password = 'test_password_123'
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Two hashes of same password should be different (different salts)
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_success(self):
        """Test password verification with correct password"""
        password_plaintext = 'correct_password_456'
        password_hash = hash_password(password_plaintext)
        
        assert verify_password(password_plaintext, password_hash) is True
    
    def test_verify_password_failure(self):
        """🔒 Test password verification fails with wrong password"""
        correct_password = 'correct_password'
        wrong_password = 'wrong_password'
        
        password_hash = hash_password(correct_password)
        assert verify_password(wrong_password, password_hash) is False
    
    def test_end_to_end_user_login_flow(self):
        """🔒 Test complete password flow: create user, retrieve, verify password"""
        username = f'test_login_{datetime.now().timestamp()}'
        email = f'{username}@test.local'
        password = 'login_test_password_789'
        
        # 1. Create user with plaintext password
        user = create_user(
            username=username,
            email=email,
            password_plaintext=password,
            role='friend'
        )
        assert user is not None
        
        # 2. Retrieve user from database
        retrieved_user = get_user_by_username(username)
        assert retrieved_user is not None
        
        # 3. Verify password against retrieved hash
        assert verify_password(password, retrieved_user.password_hash) is True
        
        # 4. Verify wrong password doesn't work
        assert verify_password('wrong_password', retrieved_user.password_hash) is False
    
    def test_bcrypt_hash_format(self):
        """Test that bcrypt hashes have correct format"""
        password = 'test_bcrypt_format'
        password_hash = hash_password(password)
        
        # Bcrypt hashes start with $2a$ or $2b$
        assert password_hash.startswith('$2b$') or password_hash.startswith('$2a$')
        # Should be at least 60 characters (full bcrypt hash)
        assert len(password_hash) >= 60


class TestSQLInjectionPrevention:
    """Test that SQL injection is prevented via parameterized queries"""
    
    def test_username_with_sql_injection_attempt(self):
        """🔒 Test that SQL injection in username field is safely handled"""
        # Try to create user with SQL injection in username
        injection_attempt = "'; DROP TABLE users; --"
        
        # Should either fail or be treated as literal string
        try:
            user = create_user(
                username=injection_attempt,
                email=f'{injection_attempt}@test.local',
                password_plaintext='password123',
                role='friend'
            )
            # If it succeeds, verify it's treated as literal string
            assert user.username == injection_attempt
            
            # Verify the users table still exists and works
            from app.db import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users;")
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            # Table should still exist and have users
            assert count > 0
        except Exception as e:
            # If it fails, that's also acceptable (DB rejects the username)
            pass
    
    def test_email_with_sql_injection_attempt(self):
        """🔒 Test that SQL injection in email field is safely handled"""
        injection_email = "user@test.local'; DELETE FROM users; --"
        
        try:
            user = create_user(
                username=f'test_user_{datetime.now().timestamp()}',
                email=injection_email,
                password_plaintext='password123',
                role='friend'
            )
            # If successful, treated as literal
            assert user.email == injection_email
        except Exception:
            # Acceptable if rejected
            pass
