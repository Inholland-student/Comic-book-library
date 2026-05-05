import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration - loads from .env"""

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGORITHM = "HS256"

    SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET"))
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    required_keys = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME", "JWT_SECRET"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing_keys)}. Check .env file."
        )


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    JWT_COOKIE_SECURE = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    JWT_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    JWT_COOKIE_SECURE = True
