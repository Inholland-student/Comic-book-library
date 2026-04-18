"""
Role-Based Access Control (RBAC) middleware
🔒 Security: Decorator to restrict endpoints by user role
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from .user_db import get_user_by_uuid


def require_role(*allowed_roles):
    """
    Decorator to restrict endpoint access by user role.
    
    Usage:
        @app.route('/api/comics', methods=['POST'])
        @require_role('admin', 'super_admin')
        def create_comic():
            return {...}, 201
    
    🔒 Security:
    - Check 1: @jwt_required() ensures user is authenticated
    - Check 2: Verify user role is in allowed_roles list
    - Returns 403 Forbidden if role not in allowed list
    
    Args:
        *allowed_roles: Tuple of role strings (e.g. 'admin', 'super_admin')
    
    Returns:
        Decorator function
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()  # First: verify JWT, returns 401 if missing/invalid
        def wrapper(*args, **kwargs):
            # Second: get user identity from JWT
            user_uuid = get_jwt_identity()  # JWT identity stored as string
            user = get_user_by_uuid(user_uuid)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Third: check if user role is in allowed list
            if user.role not in allowed_roles:
                return jsonify({
                    'error': f'Access denied. Required role: {", ".join(allowed_roles)}'
                }), 403
            
            # Pass control to actual endpoint
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


# Convenience decorators for common role combinations
def require_admin(fn):
    """Restrict to admin or super_admin"""
    return require_role('admin', 'super_admin')(fn)

def require_any_user(fn):
    """Restrict to any authenticated user (any role)"""
    return require_role('friend', 'admin', 'super_admin')(fn)

def require_super_admin(fn):
    """Restrict to super_admin only"""
    return require_role('super_admin')(fn)
