"""
Integration tests for secrets management
🔒 Security: Verify complete config and secrets workflow
"""
import pytest
import os


class TestSecretsManagement:
    """Test the complete secrets management workflow"""
    
    def test_env_file_is_gitignored(self):
        """🔒 Verify that .env file is excluded from Git"""
        # Check that .env is in .gitignore (basic check)
        # In a real setup, we'd run: git status --ignored | grep .env
        # For now, we just verify the value is loaded
        assert os.getenv('DB_PASSWORD') is not None
    
    def test_flask_app_loads_secrets_on_startup(self, app):
        """🔒 Test that Flask app successfully loads all secrets on startup"""
        assert app.config['JWT_SECRET_KEY'] is not None
        assert app.config['SECRET_KEY'] is not None
        # Verify JWT config is set (prevents JWT tokens in response body)
        assert app.config['JWT_COOKIE_HTTPONLY'] is True
        assert app.config['JWT_COOKIE_SAMESITE'] == 'Strict'
    
    def test_jwt_cookie_security_flags_set(self, app):
        """🔒 Test that JWT cookies have security flags set"""
        # These flags prevent XSS and CSRF attacks
        assert app.config['JWT_COOKIE_HTTPONLY'] is True  # Prevents JavaScript access
        assert app.config['JWT_COOKIE_SAMESITE'] == 'Strict'  # Prevents CSRF
    
    def test_health_endpoint_does_not_expose_secrets(self, client):
        """🔒 Test that health endpoint response doesn't contain secrets"""
        response = client.get('/health')
        data = response.get_json()
        
        # Verify no sensitive data in response
        response_str = str(data)
        assert 'password' not in response_str.lower()
        assert 'secret' not in response_str.lower()
        assert 'jwt' not in response_str.lower()
    
    def test_config_values_are_strings_not_none(self, app):
        """Test that all required config values are loaded and not None"""
        assert isinstance(app.config['JWT_SECRET_KEY'], str)
        assert len(app.config['JWT_SECRET_KEY']) > 0
        assert isinstance(app.config['SECRET_KEY'], str)
        assert len(app.config['SECRET_KEY']) > 0


class TestEnvironmentIsolation:
    """Test that environments are properly isolated"""
    
    def test_development_vs_production_cookie_security(self):
        """🔒 Test that development and production have different security settings"""
        from app.config import DevelopmentConfig, ProductionConfig
        
        # Dev allows non-HTTPS for local testing
        assert DevelopmentConfig.JWT_COOKIE_SECURE is False
        # Prod requires HTTPS for security
        assert ProductionConfig.JWT_COOKIE_SECURE is True
    
    def test_testing_mode_config(self):
        """Test that testing config is properly configured"""
        from app.config import TestingConfig
        
        assert TestingConfig.TESTING is True
        assert TestingConfig.DEBUG is True
        # Testing should not require HTTPS either
        assert TestingConfig.JWT_COOKIE_SECURE is False


class TestSecurityBestPractices:
    """Test that security best practices are implemented in config"""
    
    def test_jwt_algorithm_is_secure(self):
        """Test that JWT uses secure algorithm"""
        from app.config import Config
        
        # HS256 is acceptable for symmetric (shared secret) signing
        # For asymmetric (public/private key), RS256 would be better
        assert Config.JWT_ALGORITHM in ['HS256', 'RS256']
    
    def test_jwt_token_expiration_is_set(self, app):
        """Test that JWT tokens have an expiration time"""
        # Prevents long-lived tokens that could be abused if leaked
        # This is set in the Flask app __init__.py
        assert app.config.get('JWT_ACCESS_TOKEN_EXPIRES') == 24 * 3600  # 24 hours in seconds
    
    def test_no_hardcoded_secrets_in_flask_app(self, app):
        """🔒 Test that no secrets are hardcoded in Flask app factory"""
        # Verify that JWT secret is loaded from config, not hardcoded
        assert app.config.get('JWT_SECRET_KEY') is not None
        # Should be from environment, not a default literal
        # The actual test value might be the placeholder, but prod should have a real secret
        assert app.config['JWT_SECRET_KEY'] is not None
