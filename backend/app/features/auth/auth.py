"""
Authentication helper functions
🔒 Security: JWT token creation, verification, password hashing
"""
from flask_jwt_extended import create_access_token
from datetime import timedelta
from .password_service import verify_password as verify_password_hash
from .user_db import get_user_by_username
from .user import User


def create_jwt_token(user_uuid: str, username: str, role: str, expires_in_hours: int = 24) -> str:
    """
    Create a JWT token with user claims
    
    Args:
        user_uuid: User UUID to include in token
        username: Username to include in token
        role: User role to include in token
        expires_in_hours: Token expiration time in hours
    
    Returns:
        JWT token string
    """
    expires = timedelta(hours=expires_in_hours)
    additional_claims = {
        'user_uuid': str(user_uuid),  # Include user_uuid in claims
        'username': username,
        'role': role
    }
    # 🔒 identity must be a string for Flask-JWT-Extended
    token = create_access_token(
        identity=str(user_uuid),  # Convert to string for JWT subject
        additional_claims=additional_claims,
        expires_delta=expires
    )
    return token


def verify_login(username: str, password_plaintext: str) -> User | None:
    """
    Verify user login credentials
    
    Args:
        username: Username to login
        password_plaintext: Plaintext password to verify
    
    Returns:
        User object if credentials valid, None otherwise
    """
    user = get_user_by_username(username)
    if not user:
        return None
    
    # Verify password against hash
    if not verify_password_hash(password_plaintext, user.password_hash):
        return None
    
    return user
