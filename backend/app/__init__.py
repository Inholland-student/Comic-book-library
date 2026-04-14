"""
Flask app factory for Comic Book Library API
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app(config_name='development'):
    """
    Application factory pattern.
    Creates and configures Flask app with blueprints and extensions.
    """
    app = Flask(__name__)
    
    # Load config based on environment
    if config_name == 'testing':
        from .config import TestingConfig
        app.config.from_object(TestingConfig)
    elif config_name == 'production':
        from .config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from .config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize Flask extensions
    CORS(app, supports_credentials=True)  # Enable CORS with credentials (for cookies)
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = app.config['JWT_SECRET']
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Store JWT in cookies, not Authorization header
    app.config['JWT_COOKIE_SECURE'] = app.config['JWT_COOKIE_SECURE']  # False for dev, True for prod
    app.config['JWT_COOKIE_SAMESITE'] = 'Strict'  # Prevent CSRF attacks
    app.config['JWT_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access (XSS protection)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 24 * 3600  # 24 hours
    # 🔒 CSRF protection: httpOnly + SameSite=Strict provides strong CSRF protection
    # Disable CSRF token verification for API endpoints (not HTML forms)
    app.config['JWT_CSRF_PROTECT'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF token checks for cookie-based JWTs
    
    jwt = JWTManager(app)
    
    # Health check endpoint (for Docker healthcheck)
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok'}, 200
    
    # Register blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from .routes.comics import comics_bp
    app.register_blueprint(comics_bp)
    
    return app
