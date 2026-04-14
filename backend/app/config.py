import os
from dotenv import load_dotenv

# Load .env file from root
load_dotenv()

class Config:
    """Base configuration - loads from .env"""
    
    # Database
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET')
    JWT_ALGORITHM = 'HS256'
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', os.getenv('JWT_SECRET'))  # Fallback for Flask session
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Validate required config
    required_keys = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'JWT_SECRET']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_keys)}. Check .env file.")

class DevelopmentConfig(Config):
    """Development-specific config"""
    DEBUG = True
    TESTING = False
    JWT_COOKIE_SECURE = False  # Allow non-HTTPS for local dev


class TestingConfig(Config):
    """Testing-specific config"""
    DEBUG = True
    TESTING = True
    JWT_COOKIE_SECURE = False
    # Use in-memory or test DB in tests


class ProductionConfig(Config):
    """Production-specific config"""
    DEBUG = False
    TESTING = False
    JWT_COOKIE_SECURE = True  # HTTPS only in production
