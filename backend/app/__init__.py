"""
Flask app factory for Comic Book Library API
"""

from flask import Flask
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .features.common.persistence.db import db

limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")


def create_app(config_name="development"):
    """
    Application factory pattern.
    Creates and configures Flask app with blueprints and extensions.
    """
    app = Flask(__name__)

    if config_name == "testing":
        from .config import TestingConfig

        app.config.from_object(TestingConfig)
    elif config_name == "production":
        from .config import ProductionConfig

        app.config.from_object(ProductionConfig)
    else:
        from .config import DevelopmentConfig

        app.config.from_object(DevelopmentConfig)

    # Init db + migrations
    db.init_app(app)
    Migrate(app, db)

    # Import models so Alembic can detect them
    from .features.comics.comic import Comic
    from .features.auth.user import User

    # CORS
    CORS(
        app,
        supports_credentials=True,
        origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
    )

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = app.config["JWT_SECRET"]
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = app.config["JWT_COOKIE_SECURE"]
    app.config["JWT_COOKIE_SAMESITE"] = "Strict"
    app.config["JWT_COOKIE_HTTPONLY"] = True
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 24 * 3600
    app.config["JWT_CSRF_PROTECT"] = False
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False

    jwt = JWTManager(app)
    limiter.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {
            "error": "Too many login attempts",
            "message": "You have exceeded the allowed number of login requests. Please try again later.",
        }, 429

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    # Register blueprints
    from .features.auth.auth_routes import auth_bp

    app.register_blueprint(auth_bp)

    from .features.comics.comic_routes import comics_bp

    app.register_blueprint(comics_bp)

    return app
