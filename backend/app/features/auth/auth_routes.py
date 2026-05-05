"""
Authentication routes blueprint
🔒 Security: Login, register, logout with JWT in httpOnly cookies
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_limiter.util import get_remote_address
from .user_db import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_uuid,
)
from .auth import verify_login, create_jwt_token
from app import limiter
import re

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# Input validation
def validate_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Basic checks: at least one letter, one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)

    if not (has_letter and has_number):
        return False, "Password must contain at least one letter and one number"

    return True, ""


@auth_bp.route("/users", methods=["POST"])
@jwt_required()
def create_user_by_staff():
    """admin may only create friend; super_admin may create admin or friend."""
    actor = get_user_by_uuid(get_jwt_identity())
    if not actor:
        return jsonify({"error": "User not found"}), 404
    if actor.role.value not in ("super_admin", "admin"):
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    requested_role = (data.get("role") or "").strip()

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    if actor.role.value == "admin":
        if requested_role and requested_role != "friend":
            return jsonify({"error": "admin can only create friend users"}), 400
        new_role = "friend"
    else:
        if requested_role not in ("admin", "friend"):
            return jsonify({"error": "role must be admin or friend"}), 400
        new_role = requested_role

    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    valid_pwd, pwd_msg = validate_password(password)
    if not valid_pwd:
        return jsonify({"error": pwd_msg}), 400

    if get_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 409
    if get_user_by_email(email):
        return jsonify({"error": "Email already exists"}), 409

    try:
        user = create_user(
            username=username,
            email=email,
            password_plaintext=password,
            role=new_role,
        )
        return (
            jsonify(
                {
                    "uuid": user.uuid,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": f"Could not create user: {str(e)}"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user

    Request JSON:
        username: str (required, unique)
        email: str (required, unique)
        password: str (required, min 8 chars)

    Response:
        201: User created successfully
        400: Validation error
        409: Username or email already exists
    """
    data = request.get_json()

    # Validation
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username:
        return jsonify({"error": "username is required"}), 400
    if not email:
        return jsonify({"error": "email is required"}), 400
    if not password:
        return jsonify({"error": "password is required"}), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Validate password strength
    valid_pwd, pwd_msg = validate_password(password)
    if not valid_pwd:
        return jsonify({"error": pwd_msg}), 400

    # Check for duplicate username
    if get_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 409

    # Check for duplicate email
    if get_user_by_email(email):
        return jsonify({"error": "Email already exists"}), 409

    # Create user
    try:
        user = create_user(
            username=username,
            email=email,
            password_plaintext=password,
            role="friend",  # New users are friends by default
        )

        # 🔒 Response does NOT include password or password_hash
        return (
            jsonify(
                {
                    "uuid": user.uuid,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role.value,
                    "created_at": (
                        user.created_at.isoformat() if user.created_at else None
                    ),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


def username_rate_limit_key():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip().lower()

    if username:
        return f"login:{username}"

    return f"ip:{get_remote_address()}"


# Rate limiting:
# 30 login requests per 15 minutes per IP
# 5 login requests per 15 minutes per username
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("30 per 15 minutes", key_func=get_remote_address)
@limiter.limit("5 per 15 minutes", key_func=username_rate_limit_key)
def login():
    """
    Login user and set JWT in httpOnly cookie

    Request JSON:
        username: str (required)
        password: str (required)

    Response:
        200: Login successful (JWT set in httpOnly cookie)
        400: Validation error
        401: Invalid credentials

    🔒 Security: Token is set in httpOnly cookie via set_access_cookies(),
    NOT returned in response body to prevent XSS token theft
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username:
        return jsonify({"error": "username is required"}), 400
    if not password:
        return jsonify({"error": "password is required"}), 400

    # Verify credentials
    user = verify_login(username, password)
    if not user:
        # Generic message prevents username enumeration
        return jsonify({"error": "Invalid username or password"}), 401

    # 🔒 Create JWT token
    access_token = create_jwt_token(
        user_uuid=str(user.uuid), username=user.username, role=user.role.value
    )

    # 🔒 Create response WITHOUT token in body
    response = jsonify(
        {
            "uuid": user.uuid,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "message": "Login successful",
            # 🔒 NO 'access_token' or 'token' field - token is in httpOnly cookie only!
        }
    )

    # 🔒 Use Flask-JWT-Extended's set_access_cookies() to set httpOnly cookie
    # This function automatically:
    # - Sets the token in the response cookie
    # - Marks it as httpOnly (JavaScript can't access)
    # - Sets SameSite flag (already configured in __init__.py as Strict)
    # - Sets Secure flag based on config (True for prod HTTPS, False for dev)
    from flask_jwt_extended import set_access_cookies

    set_access_cookies(response, access_token)

    return response, 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """
    Get current logged-in user info
    Requires: JWT token in cookie

    Response:
        200: User info
        401: Not authenticated
    """
    user_uuid = get_jwt_identity()  # JWT identity is stored as string
    user = get_user_by_uuid(user_uuid)

    if not user:
        return jsonify({"error": "User not found"}), 404

    # 🔒 Response does NOT include password_hash
    return (
        jsonify(
            {
                "uuid": user.uuid,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
        ),
        200,
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Logout user by clearing JWT cookie

    Response:
        204: Logout successful (no content)
        401: Not authenticated (no JWT cookie)

    🔒 Security: Manually verify JWT from cookie to bypass CSRF checks
    since httpOnly + SameSite=Strict already provide CSRF protection
    """
    # Manually verify JWT from cookie by parsing the cookie directly
    # This bypasses Flask-JWT-Extended's CSRF token checks
    import jwt
    from flask import current_app

    # Get JWT from cookie
    auth_cookie = request.cookies.get(
        current_app.config.get("JWT_COOKIE_NAME", "access_token_cookie")
    )
    if not auth_cookie:
        return jsonify({"error": "Missing JWT cookie"}), 401

    try:
        # Manually decode and verify JWT
        jwt.decode(
            auth_cookie, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
        )
    except Exception as e:
        return jsonify({"error": f"Invalid token: {str(e)}"}), 401

    response = jsonify()
    # 🔒 Use Flask-JWT-Extended's unset_jwt_cookies() to clear the cookie
    unset_jwt_cookies(response)
    return response, 204
